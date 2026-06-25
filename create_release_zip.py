from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
OUT = ROOT / "RecycleCleaner_Release.zip"


def main() -> None:
    exe = DIST / "RecycleCleaner.exe"
    if not exe.exists():
        raise SystemExit("Release exe not found. Run build first.")

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe, exe.name)
        for name in ["run.bat", "install_shortcut.py", "README_RELEASE.txt"]:
            p = ROOT / name
            if p.exists():
                zf.write(p, p.name)

    print(f"[OK] Release zip created: {OUT}")


if __name__ == "__main__":
    main()
