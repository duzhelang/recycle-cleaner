from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
DIST = ROOT / "dist"
OUTPUT = ROOT / "output"
RELEASE_DIR = ROOT / "release"

SIGN_TOOL = os.environ.get("SIGNTOOL_PATH", "signtool")
SIGN_CERT = os.environ.get("SIGN_CERT_PATH", "")
SIGN_PASS = os.environ.get("SIGN_CERT_PASS", "")
SIGN_TIMESTAMP = os.environ.get("SIGN_TIMESTAMP_URL", "http://timestamp.digicert.com")


def read_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def run_step(name: str, cmd: list[str], cwd: Path | None = None) -> bool:
    print(f"\n{'='*60}")
    print(f"[STEP] {name}")
    print(f"  CMD: {' '.join(cmd)}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=cwd or ROOT)
    if result.returncode != 0:
        print(f"[FAIL] {name} (exit code {result.returncode})")
        return False
    print(f"[OK] {name}")
    return True


def sign_file(path: Path) -> bool:
    if not SIGN_CERT:
        print(f"[SKIP] Signing (no SIGN_CERT_PATH): {path.name}")
        return True
    if not path.exists():
        print(f"[SKIP] File not found for signing: {path}")
        return True
    cmd = [
        SIGN_TOOL, "sign",
        "/f", SIGN_CERT,
        "/tr", SIGN_TIMESTAMP,
        "/td", "sha256",
        "/fd", "sha256",
    ]
    if SIGN_PASS:
        cmd += ["/p", SIGN_PASS]
    cmd.append(str(path))
    print(f"[SIGN] {path.name}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"[WARN] Signing failed for {path.name}")
        return False
    print(f"[OK] Signed: {path.name}")
    return True


def find_iscc() -> str | None:
    get_iscc = ROOT / "get_iscc.ps1"
    if get_iscc.exists():
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                 "-File", str(get_iscc)],
                capture_output=True, text=True, timeout=30,
            )
            for line in result.stdout.strip().splitlines():
                if line.startswith("FOUND|"):
                    return line.split("|", 1)[1].strip()
        except Exception:
            pass

    candidates = [
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Inno Setup 6" / "ISCC.exe",
        ROOT / "tools" / "InnoSetup" / "ISCC.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def build_exe() -> Path | None:
    ok = run_step("Build EXE", [sys.executable, "build.py", "--name", "RecycleCleaner", "--onefile"])
    if not ok:
        return None
    exe = ROOT / "RecycleCleaner.exe"
    return exe if exe.exists() else None


def build_installer() -> Path | None:
    iscc = find_iscc()
    if not iscc:
        print("[WARN] Inno Setup not found, skipping installer build")
        return None
    iss = ROOT / "installer" / "RecycleCleaner.iss"
    ok = run_step("Build Installer", [iscc, str(iss)])
    if not ok:
        return None
    installer = ROOT / "installer" / "Output" / "RecycleCleaner_Setup.exe"
    return installer if installer.exists() else None


def create_zip(version: str, exe: Path) -> Path:
    RELEASE_DIR.mkdir(exist_ok=True)
    zip_path = RELEASE_DIR / f"RecycleCleaner_v{version}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe, exe.name)
        for name in ["README_RELEASE.txt", "run.bat"]:
            p = ROOT / name
            if p.exists():
                zf.write(p, p.name)
    print(f"[OK] Zip: {zip_path}")
    return zip_path


def collect_artifacts(version: str, exe: Path | None, installer: Path | None, zip_path: Path) -> list[Path]:
    RELEASE_DIR.mkdir(exist_ok=True)
    artifacts = [zip_path]
    if exe:
        dest = RELEASE_DIR / exe.name
        shutil.copy2(exe, dest)
        artifacts.append(dest)
    if installer:
        dest = RELEASE_DIR / f"RecycleCleaner_Setup_v{version}.exe"
        shutil.copy2(installer, dest)
        artifacts.append(dest)
    return artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and package Recycle Cleaner for release")
    parser.add_argument("--skip-build", action="store_true", help="Skip exe build, use existing RecycleCleaner.exe")
    parser.add_argument("--skip-installer", action="store_true", help="Skip installer build")
    parser.add_argument("--skip-sign", action="store_true", help="Skip code signing")
    parser.add_argument("--skip-sync", action="store_true", help="Skip version sync")
    args = parser.parse_args()

    version = read_version()
    print(f"[INFO] Release version: {version}")

    if not args.skip_sync:
        run_step("Sync Version", [sys.executable, "sync_version.py"])

    exe = ROOT / "RecycleCleaner.exe"
    if not args.skip_build:
        built = build_exe()
        if built:
            exe = built
        elif not exe.exists():
            print("[ERROR] Build failed and no existing exe found")
            sys.exit(1)

    if not exe.exists():
        print("[ERROR] RecycleCleaner.exe not found")
        sys.exit(1)

    if not args.skip_sign:
        sign_file(exe)

    installer = None
    if not args.skip_installer:
        installer = build_installer()
        if installer and not args.skip_sign:
            sign_file(installer)

    zip_path = create_zip(version, exe)

    artifacts = collect_artifacts(version, exe, installer, zip_path)

    print(f"\n{'='*60}")
    print("[RELEASE COMPLETE]")
    print(f"  Version: {version}")
    print(f"  Artifacts:")
    for a in artifacts:
        print(f"    {a}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
