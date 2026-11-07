/**
 * Preload script for Electron
 * Exposes safe APIs to the renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Get backend URL
    getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),

    // Restart backend (if needed)
    restartBackend: () => ipcRenderer.invoke('restart-backend'),

    // Platform info
    platform: process.platform,

    // Version info
    versions: {
        node: process.versions.node,
        chrome: process.versions.chrome,
        electron: process.versions.electron
    }
});
