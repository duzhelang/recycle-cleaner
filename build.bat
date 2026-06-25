@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python is not in PATH.
  exit /b 1
)

python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller

if not exist assets mkdir assets
if not exist assets\logo.ico python create_icon.py

python build.py --name RecycleCleaner --noconsole --onefile

echo.
echo If build succeeded, run: python install_shortcut.py
pause
