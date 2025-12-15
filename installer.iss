; Script de Instalador para Sistema de Reportes
; Compilar con Inno Setup 6

[Setup]
; Información de la aplicación
AppName=Sistema de Reportes
AppVersion=1.0
AppPublisher=Tu Empresa
AppPublisherURL=https://btw-one.com
DefaultDirName={autopf}\SistemaReportes
DefaultGroupName=Sistema de Reportes
OutputDir=.
OutputBaseFilename=SistemaReportes_Setup_v1.0
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\SistemaReportes.exe

; Información visual
WizardStyle=modern
SetupIconFile=
DisableProgramGroupPage=yes
DisableWelcomePage=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un icono en el escritorio"; GroupDescription: "Iconos adicionales:"
Name: "quicklaunchicon"; Description: "Crear un icono en Inicio Rápido"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
; Incluir toda la carpeta dist\SistemaReportes
Source: "dist\SistemaReportes\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "DetenerServidor.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Sistema de Reportes"; Filename: "{app}\SistemaReportes.exe"
Name: "{group}\Detener Servidor"; Filename: "{app}\DetenerServidor.bat"; IconFilename: "{sys}\shell32.dll"; IconIndex: 131
Name: "{group}\{cm:UninstallProgram,Sistema de Reportes}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Sistema de Reportes"; Filename: "{app}\SistemaReportes.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Sistema de Reportes"; Filename: "{app}\SistemaReportes.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\SistemaReportes.exe"; Description: "Ejecutar Sistema de Reportes"; Flags: postinstall skipifsilent nowait

[UninstallDelete]
Type: files; Name: "{app}\.env"
Type: filesandordirs; Name: "{app}\__pycache__"

[Code]
var
  ConfigPage: TInputQueryWizardPage;

procedure InitializeWizard;
var
  Page: TWizardPage;
  StaticText: TNewStaticText;
begin
  // Página de bienvenida personalizada
  Page := CreateCustomPage(wpWelcome, 'Requisitos del Sistema', 'Verifique que cumple con los requisitos antes de continuar');

  StaticText := TNewStaticText.Create(Page);
  StaticText.Parent := Page.Surface;
  StaticText.Caption :=
    'Este sistema requiere:' + #13#10 + #13#10 +
    '  • Windows 7/8/10/11 (64-bit)' + #13#10 +
    '  • MySQL Server instalado y en ejecución' + #13#10 +
    '  • Base de datos configurada' + #13#10 +
    '  • 4 GB de RAM mínimo' + #13#10 +
    '  • 500 MB de espacio en disco' + #13#10 + #13#10 +
    'IMPORTANTE: Debe tener MySQL instalado ANTES de usar el sistema.' + #13#10 +
    'Si no lo tiene, descárguelo de: https://dev.mysql.com/downloads/mysql/';
  StaticText.AutoSize := True;
  StaticText.WordWrap := True;
  StaticText.Width := Page.SurfaceWidth;

  // Página de configuración de MySQL
  ConfigPage := CreateInputQueryPage(wpSelectDir,
    'Configuración de MySQL',
    'Configure la conexión a su base de datos MySQL',
    'Por favor, ingrese los datos de conexión a MySQL. Estos se guardarán en el archivo .env y podrá modificarlos después desde el configurador.');

  ConfigPage.Add('Servidor MySQL:', False);
  ConfigPage.Add('Puerto:', False);
  ConfigPage.Add('Usuario:', False);
  ConfigPage.Add('Contraseña:', True);
  ConfigPage.Add('Nombre de la Base de Datos:', False);

  // Valores por defecto
  ConfigPage.Values[0] := 'localhost';
  ConfigPage.Values[1] := '3306';
  ConfigPage.Values[2] := 'root';
  ConfigPage.Values[3] := '';
  ConfigPage.Values[4] := 'pv';
end;

function TestMySQLConnection(Host, Port, User, Pass, DBName: String): Boolean;
var
  ResultCode: Integer;
  TestScript: String;
  ScriptPath: String;
begin
  Result := False;

  // Crear script temporal de Python para probar conexión
  ScriptPath := ExpandConstant('{tmp}\test_mysql.py');
  TestScript :=
    'import mysql.connector' + #13#10 +
    'try:' + #13#10 +
    '    conn = mysql.connector.connect(' + #13#10 +
    '        host="' + Host + '",' + #13#10 +
    '        port=' + Port + ',' + #13#10 +
    '        user="' + User + '",' + #13#10 +
    '        password="' + Pass + '",' + #13#10 +
    '        database="' + DBName + '"' + #13#10 +
    '    )' + #13#10 +
    '    conn.close()' + #13#10 +
    '    print("OK")' + #13#10 +
    'except Exception as e:' + #13#10 +
    '    print("ERROR: " + str(e))' + #13#10 +
    '    exit(1)';

  SaveStringToFile(ScriptPath, TestScript, False);

  // Ejecutar el script de prueba (solo si Python está disponible en PATH)
  if Exec(ExpandConstant('{cmd}'), '/C python "' + ScriptPath + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvContent: AnsiString;
  EnvPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Crear archivo .env con la configuración de MySQL
    EnvPath := ExpandConstant('{app}\.env');

    // Usar solo caracteres ASCII para evitar problemas de codificación
    EnvContent :=
      '# Configuracion de la Base de Datos MySQL' + #13#10 +
      '# Formato: mysql+mysqlconnector://usuario:contrasena@host:puerto/nombre_base_datos' + #13#10 +
      'DATABASE_URI=mysql+mysqlconnector://' + ConfigPage.Values[2] + ':' + ConfigPage.Values[3] +
      '@' + ConfigPage.Values[0] + ':' + ConfigPage.Values[1] + '/' + ConfigPage.Values[4] + #13#10 + #13#10 +
      '# Puerto del servidor Flask' + #13#10 +
      'PORT=5000' + #13#10 + #13#10 +
      '# Servidor y threads para Waitress' + #13#10 +
      'HOST=0.0.0.0' + #13#10 +
      'THREADS=4' + #13#10 + #13#10 +
      '# Modo Debug (True para desarrollo, False para produccion)' + #13#10 +
      'FLASK_DEBUG=False' + #13#10 + #13#10 +
      '# Habilitar log de consultas SQL (True para ver queries, False para ocultar)' + #13#10 +
      'SQL_DEBUG=False' + #13#10;

    SaveStringToFile(EnvPath, EnvContent, False);
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  TestResult: Boolean;
begin
  Result := True;

  // Validar configuración de MySQL en la página de configuración
  if CurPageID = ConfigPage.ID then
  begin
    // Validaciones básicas
    if (Trim(ConfigPage.Values[0]) = '') or
       (Trim(ConfigPage.Values[1]) = '') or
       (Trim(ConfigPage.Values[2]) = '') or
       (Trim(ConfigPage.Values[4]) = '') then
    begin
      MsgBox('Por favor, complete todos los campos excepto la contraseña (que puede estar vacía).', mbError, MB_OK);
      Result := False;
      Exit;
    end;

    // Preguntar si desea probar la conexión
    if MsgBox('¿Desea probar la conexión a MySQL antes de continuar?' + #13#10 + #13#10 +
              'Nota: Esto requiere que MySQL esté instalado y en ejecución.',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      TestResult := TestMySQLConnection(
        ConfigPage.Values[0],
        ConfigPage.Values[1],
        ConfigPage.Values[2],
        ConfigPage.Values[3],
        ConfigPage.Values[4]
      );

      if TestResult then
      begin
        MsgBox('✓ Conexión exitosa a MySQL', mbInformation, MB_OK);
      end
      else
      begin
        if MsgBox('✗ No se pudo conectar a MySQL con los datos proporcionados.' + #13#10 + #13#10 +
                  '¿Desea continuar de todos modos?' + #13#10 +
                  'Podrá configurar la conexión más tarde usando el configurador.',
                  mbError, MB_YESNO) = IDNO then
        begin
          Result := False;
        end;
      end;
    end;
  end;
end;
