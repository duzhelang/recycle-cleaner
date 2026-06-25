@echo off
setlocal
cd /d "%~dp0"

set UPX_DIR=%~dp0tools\upx

if not exist "%UPX_DIR%\upx.exe" (
  echo [INFO] Downloading UPX...
  mkdir tools\upx_tmp
  curl -L -o tools\upx_tmp\upx.zip "https://github.com/upx/upx/releases/download/v5.0.0/upx-5.0.0-win64.zip"
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path 'tools\upx_tmp\upx.zip' -DestinationPath 'tools\upx_tmp' -Force"
  for /R tools\upx_tmp %%f in (upx.exe) do copy /Y "%%f" "%UPX_DIR%\upx.exe" >nul
  rmdir /S /Q tools\upx_tmp
)

python build.py --name RecycleCleaner --onefile --upx-dir "%UPX_DIR%"
