#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_firmware.py — Build xiaozhi-esp32 firmware in hardcoded or dynamic server mode.

Usage:
    python scripts/build_firmware.py --mode hardcoded
    python scripts/build_firmware.py --mode dynamic

Modes:
    hardcoded  — OTA URL points to local Sibilla server (192.168.1.69)
    dynamic    — OTA URL uses upstream default (api.tenclass.net)

Both modes enable CONFIG_LANGUAGE_IT_IT.

The script DOES NOT flash the device. Run idf.py build flash manually after
verifying the output binary in scripts/firmware_outputs/.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODES = {
    "hardcoded": {
        "ota_url": "http://192.168.1.69:8003/xiaozhi/ota/",
        "output_bin": "firmware_hardcoded.bin",
    },
    "dynamic": {
        "ota_url": "https://api.tenclass.net/xiaozhi/ota/",
        "output_bin": "firmware_dynamic.bin",
    },
}

# Temporary override file placed in project root (idf.py working dir)
OVERRIDE_FILENAME = "sdkconfig.defaults.build_override"

# sdkconfig.defaults files processed in order; override goes last to win
SDKCONFIG_CHAIN = [
    "sdkconfig.defaults",
    "sdkconfig.defaults.esp32s3",
    OVERRIDE_FILENAME,
]

OUTPUT_SUBDIR = Path("scripts") / "firmware_outputs"

# Project root = parent directory of this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------


def check_idf_in_path() -> None:
    if shutil.which("idf.py") is None:
        print(
            "ERROR: idf.py not found in PATH.\n"
            "Activate the toolchain first:\n"
            "  source ~/esp/esp-idf/export.sh",
            file=sys.stderr,
        )
        sys.exit(1)


def write_override(ota_url: str) -> Path:
    override_path = PROJECT_ROOT / OVERRIDE_FILENAME
    content = (
        f'CONFIG_OTA_URL="{ota_url}"\n'
        "CONFIG_LANGUAGE_IT_IT=y\n"
    )
    override_path.write_text(content, encoding="utf-8")
    print(f"[build_firmware] Override written: {override_path.name}")
    print(f"  CONFIG_OTA_URL={ota_url}")
    print("  CONFIG_LANGUAGE_IT_IT=y")
    return override_path


def get_current_target() -> "str | None":
    cmake_cache = PROJECT_ROOT / "build" / "CMakeCache.txt"
    if not cmake_cache.exists():
        return None
    for line in cmake_cache.read_text(encoding="utf-8").splitlines():
        if line.startswith("IDF_TARGET:STRING="):
            return line.split("=", 1)[1].strip()
    return None


def run_build() -> int:
    sdkconfig_defaults = ";".join(SDKCONFIG_CHAIN)
    env = os.environ.copy()
    env["SDKCONFIG_DEFAULTS"] = sdkconfig_defaults

    current_target = get_current_target()
    if current_target != "esp32s3":
        print(
            f"[build_firmware] Current target: {current_target!r} → running: idf.py set-target esp32s3"
        )
        result = subprocess.run(
            ["idf.py", "set-target", "esp32s3"],
            env=env,
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            return result.returncode
    else:
        print("[build_firmware] Target already esp32s3, skipping set-target.")

    print(f"[build_firmware] SDKCONFIG_DEFAULTS={sdkconfig_defaults}")
    print(f"[build_firmware] Working dir: {PROJECT_ROOT}")
    print("[build_firmware] Running: idf.py build")

    result = subprocess.run(
        ["idf.py", "build"],
        env=env,
        cwd=PROJECT_ROOT,
    )
    return result.returncode


def copy_output(output_bin: str) -> None:
    src = PROJECT_ROOT / "build" / "xiaozhi.bin"
    if not src.exists():
        print(
            f"ERROR: Build artifact not found: {src}\n"
            "The binary name may differ — check build/ directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    output_dir = PROJECT_ROOT / OUTPUT_SUBDIR
    output_dir.mkdir(parents=True, exist_ok=True)
    dst = output_dir / output_bin
    shutil.copy2(src, dst)
    print(f"[build_firmware] Firmware saved: {dst.relative_to(PROJECT_ROOT)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build xiaozhi-esp32 firmware with a specific server configuration.\n\n"
            "  hardcoded  — Sibilla local server (192.168.1.69)\n"
            "  dynamic    — upstream default (api.tenclass.net)\n\n"
            "Both modes enable Italian language (CONFIG_LANGUAGE_IT_IT)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=list(MODES.keys()),
        metavar="MODE",
        help="Build mode: hardcoded | dynamic  (required)",
    )
    args = parser.parse_args()

    mode_cfg = MODES[args.mode]
    print(f"[build_firmware] Mode: {args.mode}")

    check_idf_in_path()

    override_path = write_override(mode_cfg["ota_url"])
    try:
        returncode = run_build()
    finally:
        if override_path.exists():
            override_path.unlink()
            print(f"[build_firmware] Override removed: {override_path.name}")

    if returncode != 0:
        print(
            f"ERROR: idf.py build failed (return code {returncode}).",
            file=sys.stderr,
        )
        sys.exit(returncode)

    copy_output(mode_cfg["output_bin"])
    print("[build_firmware] Done.")


if __name__ == "__main__":
    main()
