Recycle Cleaner Release

1) Build app
   - Double-click build.bat
   - After build completes, a RecycleCleaner.exe will be generated and copied to the project root.

2) Run app
   - Use RecycleCleaner.exe (recommended, requests admin automatically)
   - Or use run.bat (auto fallback to python run)

3) Create desktop shortcut
   - Run: python install_shortcut.py

Notes:
- The app requests administrator permission because recycle bin cleaning requires elevated access on Windows.
- If you want a custom icon, put an .ico file at assets/logo.ico before building.
