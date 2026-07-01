;------------------------------------------------------------------------------
; Inno Setup script for Markdown Converter
;
; Packages the published (framework-dependent, ReadyToRun, win-x64) output and
; delegates Windows Explorer context-menu registration to the app's own
; `install` / `uninstall` verbs (which write HKLM COM + HKCR shell keys).
;
; Build via Installer\build-installer.ps1 (it publishes first, then runs ISCC).
;------------------------------------------------------------------------------

#define MyAppName "Markdown Converter"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "DevEpic"
#define MyAppURL "https://github.com/DevEpic/MarkdownConverter"
#define MyAppExeName "MarkdownConverter.exe"
#define MyPublishDir "publish"

[Setup]
; A stable, unique AppId keeps upgrades/uninstalls consistent across versions.
AppId={{8F3A1C2D-5E47-4B9A-9C6E-2D7F4A1B8E30}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\MarkdownConverter
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
; Context-menu registration touches HKLM\Software\Classes — requires elevation.
PrivilegesRequired=admin
OutputDir=dist
OutputBaseFilename=MarkdownConverter-Setup-{#MyAppVersion}
SetupIconFile=..\MarkdownConverter.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; Custom wizard branding images (BMP). Paths are relative to this .iss file.
WizardImageFile=WizardImage.bmp
WizardSmallImageFile=WizardSmallImage.bmp
WizardImageStretch=yes
WizardImageBackColor=clWhite
; This is an x64-only application (COM comhost is built x64).
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Adding the CLI to PATH edits the system environment; this makes Setup broadcast
; WM_SETTINGCHANGE so new terminals pick up the change without a reboot.
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Optional: expose the bundled markitdown.exe on the system PATH so users can run
; `markitdown` from any terminal. Unchecked by default.
Name: "addtopath"; Description: "Add the markitdown command-line tool to PATH (run 'markitdown' from any terminal)"; \
    GroupDescription: "Command-line tool:"; Flags: unchecked

[Files]
Source: "{#MyPublishDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
; Append the CLI folder to the system PATH when the addtopath task is selected.
; NeedsAddPath guards against adding a duplicate entry on re-install/upgrade.
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\markitdown"; \
    Tasks: addtopath; Check: NeedsAddPath()

[Icons]
Name: "{group}\{#MyAppName} (About)"; Filename: "{app}\{#MyAppExeName}"; Parameters: "about"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
; Register the Explorer context menu after files are in place.
Filename: "{app}\{#MyAppExeName}"; Parameters: "install --silent"; \
    StatusMsg: "Registering Windows Explorer context menu..."; \
    Flags: runhidden waituntilterminated

[UninstallRun]
; Remove the context-menu registrations before deleting the files.
Filename: "{app}\{#MyAppExeName}"; Parameters: "uninstall --silent"; \
    Flags: runhidden waituntilterminated; RunOnceId: "UnregisterContextMenu"

[Code]
const
  EnvironmentKey = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';

// Full path to the folder that contains the bundled markitdown.exe.
function CliDir(): String;
begin
  Result := ExpandConstant('{app}\markitdown');
end;

// Returns True when the CLI folder is not already on the system PATH, so the
// PATH append in the Registry section runs at most once.
function NeedsAddPath(): Boolean;
var
  OrigPath: String;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Uppercase(CliDir()) + ';', ';' + Uppercase(OrigPath) + ';') = 0;
end;

// Removes the CLI folder from the system PATH on uninstall, tolerating the
// segment appearing at the start, middle, or end of the value.
procedure RemoveFromPath();
var
  Paths: String;
  Dir: String;
  P: Integer;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Paths) then
    exit;
  Dir := CliDir();

  P := Pos(Uppercase(';' + Dir), Uppercase(Paths));
  if P > 0 then
    Delete(Paths, P, Length(';' + Dir))
  else
  begin
    P := Pos(Uppercase(Dir + ';'), Uppercase(Paths));
    if P > 0 then
      Delete(Paths, P, Length(Dir + ';'))
    else
    begin
      P := Pos(Uppercase(Dir), Uppercase(Paths));
      if P = 0 then
        exit;
      Delete(Paths, P, Length(Dir));
    end;
  end;

  RegWriteExpandStringValue(HKEY_LOCAL_MACHINE, EnvironmentKey, 'Path', Paths);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
    RemoveFromPath();
end;

// Best-effort check for the .NET Desktop Runtime that a framework-dependent
// build needs. Warns (but lets the user continue) if it can't find a 10.x
// Microsoft.WindowsDesktop.App alongside the 64-bit dotnet host.
function HasDotNet10Desktop(): Boolean;
var
  SharedRoot: String;
  FindRec: TFindRec;
begin
  Result := False;
  SharedRoot := ExpandConstant('{commonpf}\dotnet\shared\Microsoft.WindowsDesktop.App');
  if not DirExists(SharedRoot) then
    exit;

  if FindFirst(SharedRoot + '\10.*', FindRec) then
  begin
    try
      Result := True;
    finally
      FindClose(FindRec);
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not HasDotNet10Desktop() then
  begin
    if MsgBox(
        'The .NET 10 Desktop Runtime (x64) was not detected.' + #13#10 + #13#10 +
        'Markdown Converter needs it to run. You can install it now from:' + #13#10 +
        'https://dotnet.microsoft.com/download/dotnet/10.0' + #13#10 + #13#10 +
        'Continue with installation anyway?',
        mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;

// Returns the previous install's UninstallString (quoted path to unins000.exe),
// or '' if this product is not currently installed. The registry sub-key is
// "<AppId>_is1" under the Uninstall hive.
function GetUninstallString(): String;
var
  Key: String;
  S: String;
begin
  Key := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\' +
         '{8F3A1C2D-5E47-4B9A-9C6E-2D7F4A1B8E30}_is1';
  S := '';
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, Key, 'UninstallString', S) then
    RegQueryStringValue(HKEY_CURRENT_USER, Key, 'UninstallString', S);
  Result := S;
end;

// Runs the previous version's uninstaller silently and waits for it to finish.
// This removes stale files (e.g. an old Third-Party\markitdown engine folder
// from before the layout rename), unregisters the old context menu, and clears
// any prior PATH entry — giving the upgrade a clean base instead of an in-place
// overwrite that would orphan the old engine folder.
procedure UninstallPreviousVersion();
var
  UninstStr: String;
  ResultCode: Integer;
begin
  UninstStr := RemoveQuotes(GetUninstallString());
  if UninstStr = '' then
    exit;
  if not FileExists(UninstStr) then
    exit;
  Exec(UninstStr,
       '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  // Give the OS a moment to release file handles (e.g. the COM comhost DLL)
  // before Setup starts copying the new files into place.
  Sleep(1000);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  UninstallPreviousVersion();
end;
