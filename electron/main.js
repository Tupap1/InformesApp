/**
 * Electron Main Process
 * Manages Python backend as sidecar and the Electron window
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

// Environment detection
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

// Python backend process reference
let pythonProcess = null;
let mainWindow = null;

// Configuration
const BACKEND_PORT = 5000;
const BACKEND_URL = `http://localhost:${BACKEND_PORT}`;
const MAX_RETRIES = 30;
const RETRY_INTERVAL = 1000; // 1 second

/**
 * Get path to Python executable
 * In DEV: Use system Python
 * In PROD: Use bundled PyInstaller executable
 */
function getPythonPath() {
    if (isDev) {
        // In development, use system Python
        return 'python';
    } else {
        // In production, use the bundled executable
        // PyInstaller creates a single exe in resources/backend/dist/
        const exePath = path.join(
            process.resourcesPath,
            'backend',
            'dist',
            'main.exe'
        );

        console.log('[Electron] Python executable path:', exePath);

        if (!fs.existsSync(exePath)) {
            console.error('[Electron] ERROR: Python executable not found at:', exePath);
            throw new Error(`Python executable not found at: ${exePath}`);
        }

        return exePath;
    }
}

/**
 * Get path to main.py script
 * Only used in DEV mode
 */
function getMainPyPath() {
    if (isDev) {
        return path.join(__dirname, '..', 'main.py');
    }
    return null;
}

/**
 * Start the Python backend process
 */
function startPythonBackend() {
    return new Promise((resolve, reject) => {
        console.log('[Electron] Starting Python backend...');
        console.log('[Electron] Environment:', isDev ? 'DEVELOPMENT' : 'PRODUCTION');

        try {
            const pythonPath = getPythonPath();
            let args = [];

            if (isDev) {
                // In DEV mode, run the Python script
                const mainPyPath = getMainPyPath();
                console.log('[Electron] Running Python script:', mainPyPath);
                args = [mainPyPath];
            }
            // In PROD mode, the exe runs directly without arguments

            console.log('[Electron] Spawning process:', pythonPath, args);

            pythonProcess = spawn(pythonPath, args, {
                cwd: isDev ? path.join(__dirname, '..') : process.resourcesPath,
                env: {
                    ...process.env,
                    PYTHONUNBUFFERED: '1',
                    PORT: String(BACKEND_PORT)
                }
            });

            pythonProcess.stdout.on('data', (data) => {
                console.log(`[Python] ${data.toString().trim()}`);
            });

            pythonProcess.stderr.on('data', (data) => {
                console.error(`[Python ERROR] ${data.toString().trim()}`);
            });

            pythonProcess.on('error', (error) => {
                console.error('[Electron] Failed to start Python process:', error);
                reject(error);
            });

            pythonProcess.on('close', (code) => {
                console.log(`[Electron] Python process exited with code ${code}`);
                pythonProcess = null;
            });

            console.log('[Electron] Python process spawned with PID:', pythonProcess.pid);
            resolve();

        } catch (error) {
            console.error('[Electron] Error starting Python backend:', error);
            reject(error);
        }
    });
}

/**
 * Check if backend is ready by polling the health endpoint
 */
function waitForBackend() {
    return new Promise((resolve, reject) => {
        let retries = 0;

        console.log(`[Electron] Waiting for backend at ${BACKEND_URL}...`);

        const checkBackend = () => {
            http.get(BACKEND_URL, (res) => {
                if (res.statusCode === 200 || res.statusCode === 404) {
                    // 404 is OK - it means the server is running, just no route for '/'
                    console.log('[Electron] Backend is ready!');
                    resolve();
                } else {
                    retry();
                }
            }).on('error', (err) => {
                retry();
            });
        };

        const retry = () => {
            retries++;
            if (retries >= MAX_RETRIES) {
                console.error(`[Electron] Backend failed to start after ${MAX_RETRIES} attempts`);
                reject(new Error('Backend failed to start'));
            } else {
                console.log(`[Electron] Retry ${retries}/${MAX_RETRIES}...`);
                setTimeout(checkBackend, RETRY_INTERVAL);
            }
        };

        checkBackend();
    });
}

/**
 * Create the main Electron window
 */
function createWindow() {
    console.log('[Electron] Creating main window...');

    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1024,
        minHeight: 768,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            // Preload script if needed for IPC
            // preload: path.join(__dirname, 'preload.js')
        },
        show: false, // Don't show until ready
        backgroundColor: '#1a1a2e', // Dark background matching the app theme
        icon: path.join(__dirname, 'icon.ico') // Add your icon here
    });

    // Remove menu bar (optional)
    mainWindow.setMenuBarVisibility(false);

    // Load the app
    if (isDev) {
        // In DEV mode, load from Vite dev server
        mainWindow.loadURL('http://localhost:3000');
        mainWindow.webContents.openDevTools(); // Open DevTools in development
    } else {
        // In PROD mode, load from built React files
        const indexPath = path.join(__dirname, '..', 'dist', 'index.html');
        console.log('[Electron] Loading from:', indexPath);
        mainWindow.loadFile(indexPath);
    }

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        console.log('[Electron] Window ready to show');
        mainWindow.show();
    });

    // Handle window close
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        require('electron').shell.openExternal(url);
        return { action: 'deny' };
    });
}

/**
 * Kill Python process gracefully
 */
function killPythonProcess() {
    if (pythonProcess) {
        console.log('[Electron] Killing Python process...');

        try {
            if (process.platform === 'win32') {
                // On Windows, use taskkill to force kill the process tree
                spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
            } else {
                // On Unix systems, use SIGTERM
                pythonProcess.kill('SIGTERM');

                // Force kill after 2 seconds if still running
                setTimeout(() => {
                    if (pythonProcess) {
                        pythonProcess.kill('SIGKILL');
                    }
                }, 2000);
            }
        } catch (error) {
            console.error('[Electron] Error killing Python process:', error);
        }

        pythonProcess = null;
    }
}

/**
 * App initialization sequence
 */
async function initialize() {
    try {
        console.log('[Electron] Initializing application...');

        // Step 1: Start Python backend
        await startPythonBackend();

        // Step 2: Wait for backend to be ready
        await waitForBackend();

        // Step 3: Create window and load app
        createWindow();

        console.log('[Electron] Application initialized successfully');

    } catch (error) {
        console.error('[Electron] Initialization failed:', error);

        // Show error dialog
        const { dialog } = require('electron');
        dialog.showErrorBox(
            'Error al iniciar',
            `No se pudo iniciar la aplicación:\n\n${error.message}\n\nRevise los logs para más información.`
        );

        // Quit the app
        app.quit();
    }
}

// ----- Electron App Events -----

app.whenReady().then(initialize);

app.on('window-all-closed', () => {
    console.log('[Electron] All windows closed');
    killPythonProcess();
    app.quit();
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

app.on('before-quit', () => {
    console.log('[Electron] App is quitting...');
    killPythonProcess();
});

app.on('will-quit', () => {
    console.log('[Electron] App will quit');
    killPythonProcess();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('[Electron] Uncaught exception:', error);
    killPythonProcess();
});

// ----- IPC Handlers (if needed for future features) -----

ipcMain.handle('get-backend-url', () => {
    return BACKEND_URL;
});

ipcMain.handle('restart-backend', async () => {
    killPythonProcess();
    await startPythonBackend();
    await waitForBackend();
    return { success: true };
});
