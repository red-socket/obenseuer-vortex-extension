#!/usr/bin/env python3
"""Build the Nexus Mods release archive for the Obenseuer Vortex extension.

Usage:
    python3 -I tools/package.py            # release build
    python3 -I tools/package.py --draft    # local test build, skips the author check

Checks the rules from Nexus's "How to package a game extension" guide before
zipping, so a broken upload never reaches Vortex users:
  - index.js, info.json and gameart.png sit at the top level of the archive
  - info.json is valid JSON without a byte-order mark and has every field
  - version is MAJOR.MINOR.PATCH and has an entry in CHANGELOG.md
  - gameart.png is a 640x360 PNG of at most 1 MB

Writes dist/obenseuer-vortex-extension-<version>.zip.
"""
import argparse
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXT_DIR = ROOT / "extension"
DIST_DIR = ROOT / "dist"
CHANGELOG = ROOT / "CHANGELOG.md"

GAME_NAME = "Obenseuer"
NEXUS_GAME_ID = 6792
REQUIRED_FILES = ("index.js", "info.json", "gameart.png")
INFO_FIELDS = ("name", "author", "version", "description", "gameId")
PLACEHOLDER_AUTHOR = "YOUR_NEXUS_USERNAME"
ART_SIZE = (640, 360)
ART_MAX_BYTES = 1024 * 1024
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def check_info(errors, draft):
    raw = (EXT_DIR / "info.json").read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append("info.json starts with a UTF-8 byte-order mark; Vortex refuses to load it")
        raw = raw[3:]
    try:
        info = json.loads(raw.decode("utf-8"))
    except ValueError as err:
        errors.append(f"info.json is not valid JSON: {err}")
        return None

    for field in INFO_FIELDS:
        if field not in info or info[field] in ("", None):
            errors.append(f"info.json is missing '{field}'")
    if info.get("name") != GAME_NAME:
        errors.append(f"info.json name must be exactly '{GAME_NAME}' (the game's name on Nexus Mods)")
    if info.get("gameId") != NEXUS_GAME_ID:
        errors.append(f"info.json gameId must be the number {NEXUS_GAME_ID}")
    version = info.get("version", "")
    if not SEMVER.match(str(version)):
        errors.append(f"info.json version '{version}' is not MAJOR.MINOR.PATCH")
    if not draft and info.get("author") == PLACEHOLDER_AUTHOR:
        errors.append("info.json author is still the placeholder; set your Nexus username")
    return info


def check_changelog(errors, version):
    if not CHANGELOG.exists():
        errors.append("CHANGELOG.md is missing")
        return
    heading = re.compile(rf"^##\s*\[?{re.escape(version)}\]?(\s|$)", re.MULTILINE)
    if not heading.search(CHANGELOG.read_text(encoding="utf-8")):
        errors.append(f"CHANGELOG.md has no '## [{version}]' entry")


def check_art(errors):
    art = EXT_DIR / "gameart.png"
    data = art.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        errors.append("gameart.png is not a PNG file")
        return
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != ART_SIZE:
        errors.append(f"gameart.png is {width}x{height}; it must be {ART_SIZE[0]}x{ART_SIZE[1]}")
    if len(data) > ART_MAX_BYTES:
        errors.append(f"gameart.png is {len(data)} bytes; the limit is {ART_MAX_BYTES}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--draft", action="store_true", help="local test build: allow the placeholder author")
    args = parser.parse_args()

    errors = []
    missing = [name for name in REQUIRED_FILES if not (EXT_DIR / name).is_file()]
    for name in missing:
        errors.append(f"extension/{name} is missing")
    if missing:
        return fail(errors)

    info = check_info(errors, args.draft)
    if info is not None:
        check_changelog(errors, str(info.get("version", "")))
    check_art(errors)
    if errors:
        return fail(errors)

    version = info["version"]
    suffix = "-draft" if args.draft else ""
    DIST_DIR.mkdir(exist_ok=True)
    out = DIST_DIR / f"obenseuer-vortex-extension-{version}{suffix}.zip"
    files = sorted(p for p in EXT_DIR.rglob("*") if p.is_file())
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            # Fixed timestamp so rebuilding the same sources gives the same archive.
            entry = zipfile.ZipInfo(path.relative_to(EXT_DIR).as_posix(), date_time=(2020, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(entry, path.read_bytes())

    print(f"Wrote {out.relative_to(ROOT)} ({len(files)} files):")
    for path in files:
        print(f"  {path.relative_to(EXT_DIR).as_posix()}")
    print(f"Upload it on Nexus Mods with version {version}.")
    return 0


def fail(errors):
    print("Not packaged:", file=sys.stderr)
    for err in errors:
        print(f"  - {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
