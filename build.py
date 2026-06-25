from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_NAME = "RecycleCleaner"


def run() -> None:
    parser = argparse.ArgumentParser(description="Build Recycle Cleaner into a Windows app (.exe)")
    parser.add_argument("--name", default=DEFAULT_NAME, help="Output exe name")
    parser.add_argument("--icon", default=None, help="Optional .ico path")
    parser.add_argument("--console", action="store_true", help="Keep console window")
    parser.add_argument("--onefile", action="store_true", default=True, help="Package into one file")
    parser.add_argument("--onedir", action="store_true", help="Package into one directory")
    parser.add_argument("--upx-dir", default=None, help="Optional UPX directory to compress EXE")
    args = parser.parse_args()

    if args.onedir:
        mode = "--onedir"
    else:
        mode = "--onefile"

    dist = ROOT / "dist"
    build = ROOT / "build"
    spec = ROOT / f"{args.name}.spec"

    assets_dir = ROOT / "assets"
    assets_dir.mkdir(exist_ok=True)
    version_file = ROOT / "version_info.txt"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(ROOT / "recycle_cleaner.py"),
        mode,
        "--name",
        args.name,
        "--uac-admin",
        "--noconfirm",
        "--clean",
        "--add-data",
        f"{assets_dir}{os.pathsep}assets",
    ]

    if args.upx_dir:
        cmd += ["--upx-dir", str(Path(args.upx_dir))]

    if not args.console:
        cmd.append("--noconsole")

    if args.icon:
        icon = Path(args.icon)
        if not icon.exists():
            raise FileNotFoundError(f"Icon not found: {icon}")
        cmd += ["--icon", str(icon)]
    elif (assets_dir / "logo.ico").exists():
        cmd += ["--icon", str(assets_dir / "logo.ico")]

    if version_file.exists():
        cmd += ["--version-file", str(version_file)]

    subprocess.run(cmd, check=True, cwd=ROOT)

    exe_path = dist / f"{args.name}.exe"
    if exe_path.exists():
        target = ROOT / exe_path.name
        shutil.copy2(exe_path, target)
        print(f"[OK] Built: {target}")
    else:
        print("[WARN] Build finished, but exe not found in dist/.")


if __name__ == "__main__":
    run()
