@echo off
setlocal
cd /d "%~dp0"

if exist RecycleCleaner.exe (
  powershell -Command "Start-Process -FilePath '%~dp0RecycleCleaner.exe' -Verb RunAs -Wait"
) else (
  powershell -Command "Start-Process -FilePath 'python' -ArgumentList 'recycle_cleaner.py' -WorkingDirectory '%~dp0' -Verb RunAs -Wait"
)
