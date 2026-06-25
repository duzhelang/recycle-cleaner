@echo off
setlocal
cd /d "%~dp0"

set ISCC_URL=https://files.jrsoftware.org/is/6/innosetup-6.3.3.exe
set ISCC_EXE=%~dp0tools\InnoSetup\ISCC.exe

if not exist "%ISCC_EXE%" (
  echo [INFO] Downloading Inno Setup...
  mkdir tools\InnoSetup_tmp
  curl -L -o tools\InnoSetup_tmp\is.exe "%ISCC_URL%"
  tools\InnoSetup_tmp\is.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR="%~dp0tools\InnoSetup"
  rmdir /S /Q tools\InnoSetup_tmp
)

if not exist "%ISCC_EXE%" (
  echo [ERROR] Inno Setup not found.
  exit /b 1
)

"%ISCC_EXE%" "installer\RecycleCleaner.iss"
