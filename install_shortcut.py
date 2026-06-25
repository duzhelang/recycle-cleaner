from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET_EXE = ROOT / "RecycleCleaner.exe"
TARGET_BAT = ROOT / "run.bat"
SHORTCUT_NAME = "Recycle Cleaner.lnk"


def create_shortcut(target: Path) -> None:
    desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
    shortcut_path = desktop / SHORTCUT_NAME

    ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut('{shortcut_path}')
$lnk.TargetPath = '{target}'
$lnk.WorkingDirectory = '{target.parent}'
$lnk.WindowStyle = 7
$lnk.Save()
"""

    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        check=True,
    )
    print(f"[OK] Shortcut created on Desktop: {shortcut_path}")


def main() -> None:
    if TARGET_EXE.exists():
        create_shortcut(TARGET_EXE)
    elif TARGET_BAT.exists():
        create_shortcut(TARGET_BAT)
    else:
        print("[ERROR] No target found to create shortcut.")
        sys.exit(1)


if __name__ == "__main__":
    main()
