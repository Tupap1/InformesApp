; Script de Instalador SIMPLIFICADO para Sistema de Reportes
; Compilar con Inno Setup 6
; Este instalador copia solo el ejecutable único autocontenido

[Setup]
; Información de la aplicación
AppName=Sistema de Reportes
AppVersion=1.0
AppPublisher=Tu Empresa
AppPublisherURL=https://btw-one.com
DefaultDirName={autopf}\SistemaReportes
DefaultGroupName=Sistema de Reportes
OutputDir=.
OutputBaseFilename=SistemaReportes_Setup_Final
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
UninstallDisplayIcon={app}\SistemaReportes.exe
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un icono en el escritorio"; GroupDescription: "Iconos adicionales:"
Name: "quicklaunchicon"; Description: "Crear un icono en Inicio Rápido"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
; Solo copiar el ejecutable único
Source: "dist\SistemaReportes.exe"; DestDir: "{app}"; Flags: ignoreversion
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
Type: filesandordirs; Name: "{app}"

[Code]
var
  DatabasePage: TInputQueryWizardPage;
  DatabaseHost: String;
  DatabasePort: String;
  DatabaseName: String;
  DatabaseUser: String;
  DatabasePassword: String;

procedure InitializeWizard;
begin
  // Crear página de configuración de base de datos
  DatabasePage := CreateInputQueryPage(wpSelectTasks,
    'Configuración de Base de Datos MySQL',
    'Configure la conexión a la base de datos',
    'Por favor ingrese los datos de conexión a MySQL. ' +
    'Puede dejar los valores por defecto si MySQL está instalado localmente.');

  DatabasePage.Add('Host (servidor):', False);
  DatabasePage.Values[0] := 'localhost';

  DatabasePage.Add('Puerto:', False);
  DatabasePage.Values[1] := '3306';

  DatabasePage.Add('Nombre de la base de datos:', False);
  DatabasePage.Values[2] := 'pv';

  DatabasePage.Add('Usuario:', False);
  DatabasePage.Values[3] := 'root';

  DatabasePage.Add('Contraseña:', True); // True = campo de contraseña (oculto)
  DatabasePage.Values[4] := '';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = DatabasePage.ID then
  begin
    DatabaseHost := DatabasePage.Values[0];
    DatabasePort := DatabasePage.Values[1];
    DatabaseName := DatabasePage.Values[2];
    DatabaseUser := DatabasePage.Values[3];
    DatabasePassword := DatabasePage.Values[4];

    if DatabaseHost = '' then
    begin
      MsgBox('Debe ingresar el host del servidor MySQL.', mbError, MB_OK);
      Result := False;
      Exit;
    end;

    if DatabaseName = '' then
    begin
      MsgBox('Debe ingresar el nombre de la base de datos.', mbError, MB_OK);
      Result := False;
      Exit;
    end;

    if DatabaseUser = '' then
    begin
      MsgBox('Debe ingresar el usuario de MySQL.', mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvContent: String;
  EnvFilePath: String;
  DatabaseURI: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Crear archivo .env con la configuración
    EnvFilePath := ExpandConstant('{app}\.env');

    // Construir DATABASE_URI
    DatabaseURI := 'mysql+mysqlconnector://' + DatabaseUser;

    if DatabasePassword <> '' then
      DatabaseURI := DatabaseURI + ':' + DatabasePassword;

    DatabaseURI := DatabaseURI + '@' + DatabaseHost + ':' + DatabasePort + '/' + DatabaseName;

    // Contenido del archivo .env
    EnvContent := '# Configuración de la Base de Datos MySQL' + #13#10 +
                  'DATABASE_URI=' + DatabaseURI + #13#10 +
                  '' + #13#10 +
                  '# Puerto del servidor Flask' + #13#10 +
                  'PORT=5000' + #13#10 +
                  '' + #13#10 +
                  '# Servidor y threads para Waitress' + #13#10 +
                  'HOST=0.0.0.0' + #13#10 +
                  'THREADS=4' + #13#10 +
                  '' + #13#10 +
                  '# Modo Debug (True para desarrollo, False para producción)' + #13#10 +
                  'FLASK_DEBUG=False' + #13#10 +
                  '' + #13#10 +
                  '# Habilitar log de consultas SQL (True para ver queries, False para ocultar)' + #13#10 +
                  'SQL_DEBUG=False';

    // Guardar archivo .env
    SaveStringToFile(EnvFilePath, EnvContent, False);
  end;
end;
