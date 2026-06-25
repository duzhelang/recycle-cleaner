from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
RECYCLE_CLEANER_PY = ROOT / "recycle_cleaner.py"
VERSION_INFO_TXT = ROOT / "version_info.txt"
ISS_FILE = ROOT / "installer" / "RecycleCleaner.iss"
DOCS_RELEASE = ROOT / "docs" / "release.md"


def read_version() -> str:
    raw = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not re.match(r"^\d+\.\d+\.\d+$", raw):
        print(f"[ERROR] VERSION format invalid: {raw!r}, expected X.Y.Z")
        sys.exit(1)
    return raw


def gen_version_info(version: str) -> str:
    parts = version.split(".")
    quad = f"({parts[0]}, {parts[1]}, {parts[2]}, 0)"
    return (
        "VSVersionInfo(\n"
        "  ffi=FixedFileInfo(\n"
        f"    filevers={quad},\n"
        f"    prodvers={quad},\n"
        "    mask=0x3f,\n"
        "    flags=0x0,\n"
        "    OS=0x40004,\n"
        "    fileType=0x1,\n"
        "    subtype=0x0,\n"
        "    date=(0, 0)\n"
        "  ),\n"
        "  kids=[\n"
        "    StringFileInfo(\n"
        "      [\n"
        "        StringTable(\n"
        "          '080404b0',\n"
        "          [\n"
        "            StringStruct('CompanyName', 'Recycle Cleaner'),\n"
        "            StringStruct('FileDescription', 'Recycle Cleaner Tool'),\n"
        f"            StringStruct('FileVersion', '{version}.0'),\n"
        "            StringStruct('InternalName', 'RecycleCleaner'),\n"
        "            StringStruct('OriginalFilename', 'RecycleCleaner.exe'),\n"
        "            StringStruct('ProductName', 'Recycle Cleaner'),\n"
        f"            StringStruct('ProductVersion', '{version}.0'),\n"
        "          ]\n"
        "        )\n"
        "      ]\n"
        "    ),\n"
        "    VarFileInfo([VarStruct('Translation', [2052, 1200])])\n"
        "  ]\n"
        ")\n"
    )


def update_version_info(version: str) -> bool:
    content = gen_version_info(version)
    old = VERSION_INFO_TXT.read_text(encoding="utf-8") if VERSION_INFO_TXT.exists() else ""
    if old == content:
        return False
    VERSION_INFO_TXT.write_text(content, encoding="utf-8")
    return True


def update_recycle_cleaner_py(version: str) -> bool:
    text = RECYCLE_CLEANER_PY.read_text(encoding="utf-8")
    new_text = re.sub(
        r'^(APP_VERSION\s*=\s*)"[^"]*"',
        f'\\1"{version}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if new_text == text:
        return False
    RECYCLE_CLEANER_PY.write_text(new_text, encoding="utf-8")
    return True


def update_iss(version: str) -> bool:
    text = ISS_FILE.read_text(encoding="utf-8")
    original = text
    text = re.sub(r"^(AppVersion=).*$", f"\\g<1>{version}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^(AppVerName=).*$", f"\\g<1>Recycle Cleaner {version}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^(VersionInfoVersion=).*$", f"\\g<1>{version}.0", text, count=1, flags=re.MULTILINE)
    if text == original:
        return False
    ISS_FILE.write_text(text, encoding="utf-8")
    return True


def update_docs_release(version: str) -> bool:
    text = DOCS_RELEASE.read_text(encoding="utf-8")
    new_text = re.sub(
        r"^(- 应用版本：).*$",
        f"\\g<1>{version}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if new_text == text:
        return False
    DOCS_RELEASE.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    version = read_version()
    print(f"[INFO] Syncing version: {version}")
    changed = []
    if update_version_info(version):
        changed.append("version_info.txt")
    if update_recycle_cleaner_py(version):
        changed.append("recycle_cleaner.py")
    if update_iss(version):
        changed.append("RecycleCleaner.iss")
    if update_docs_release(version):
        changed.append("docs/release.md")
    if changed:
        print(f"[OK] Updated: {', '.join(changed)}")
    else:
        print("[OK] All files already up to date.")


if __name__ == "__main__":
    main()
