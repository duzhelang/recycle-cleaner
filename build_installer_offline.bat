@echo off
setlocal
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "get_iscc.ps1" > iscc_out.tmp
set FOUND=
for /f "tokens=1,2 delims=|" %%a in (iscc_out.tmp) do (
  if "%%a"=="FOUND" set FOUND=%%b
)
del /f /q iscc_out.tmp

if defined FOUND (
  "%FOUND%" "installer\RecycleCleaner.iss"
  exit /b %errorlevel%
)

set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
  echo [ERROR] Inno Setup not found.
  exit /b 1
)
%ISCC% "installer\RecycleCleaner.iss"
