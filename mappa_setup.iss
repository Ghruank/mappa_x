[Setup]
AppName=Mappa
AppVersion=1.0
DefaultDirName={localappdata}\Mappa
DefaultGroupName=Mappa
OutputDir=.
OutputBaseFilename=Mappa_Installer_v3
SetupIconFile=
UninstallDisplayIcon={app}\mappa.exe
Compression=lzma
SolidCompression=yes

[Files]
Source: "mappa.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "install.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Mappa"; Filename: "{app}\mappa.bat"

[Code]
var
  GroqAPI, LlamaPath: string;
  InputQueryPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  InputQueryPage := CreateInputQueryPage(wpWelcome,
    'Mappa Setup', 'Please provide the following information:',
    'Enter your Groq API Key and LLaMA model path.');

  InputQueryPage.Add('Groq API Key:', False);
  InputQueryPage.Add('LLaMA Model Path:', False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Params: string;
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    GroqAPI := InputQueryPage.Values[0];
    LlamaPath := InputQueryPage.Values[1];

    // Pass parameters safely to the batch file
    Params := '"' + GroqAPI + '" "' + LlamaPath + '"';
    Exec(ExpandConstant('{app}\install.bat'), Params, '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
  end;
end;
