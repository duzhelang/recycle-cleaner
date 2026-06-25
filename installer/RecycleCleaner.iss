[Setup]
AppId={{B6E2C3D1-6F8A-4C2D-9B77-RecycleCleaner}
AppName=Recycle Cleaner
AppVersion=1.0.0
AppVerName=Recycle Cleaner 1.0.0
AppPublisher=Recycle Cleaner
AppPublisherURL=https://example.com/recycle-cleaner
AppSupportURL=https://example.com/recycle-cleaner
VersionInfoVersion=1.0.0.0
DefaultDirName={autopf}\Recycle Cleaner
DefaultGroupName=Recycle Cleaner
OutputBaseFilename=RecycleCleaner_Setup
OutputDir=Output
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=..\assets\logo.ico
UninstallDisplayIcon={app}\RecycleCleaner.exe
UninstallDisplayName=Recycle Cleaner
LicenseFile=license.txt
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableProgramGroupPage=yes
AppMutex=RecycleCleanerMutex

[Files]
Source: "..\RecycleCleaner.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README_RELEASE.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\Recycle Cleaner"; Filename: "{app}\RecycleCleaner.exe"
Name: "{group}\Uninstall Recycle Cleaner"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Recycle Cleaner"; Filename: "{app}\RecycleCleaner.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\RecycleCleaner.exe"; Description: "Launch Recycle Cleaner"; Flags: nowait postinstall skipifsilent runascurrentuser
