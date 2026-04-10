#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webui/server.py — Web UI server for building xiaozhi-esp32 firmware.

Run from the project root after activating ESP-IDF:
    source ~/esp/esp-idf/export.sh
    python3 webui/server.py

Then open http://localhost:5001
"""

import json
import os
import queue
import re
import shutil
import subprocess
import threading
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request, send_file

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEBUI_DIR = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "build"

OVERRIDE_FILENAME = "sdkconfig.defaults.build_override"
SDKCONFIG_CHAIN = [
    "sdkconfig.defaults",
    "sdkconfig.defaults.esp32s3",
    OVERRIDE_FILENAME,
]

# ---------------------------------------------------------------------------
# Build modes — mirror of build_firmware.py MODES
# ---------------------------------------------------------------------------

MODES = {
    "hardcoded": "http://192.168.1.69:8003/xiaozhi/ota/",
    "dynamic": "https://api.tenclass.net/xiaozhi/ota/",
}

# ---------------------------------------------------------------------------
# Languages — must match Kconfig.projbuild choices exactly
# ---------------------------------------------------------------------------

LANGUAGES = [
    ("it-IT",  "Italian"),
    ("zh-CN",  "Chinese (Simplified)"),
    ("zh-TW",  "Chinese (Traditional)"),
    ("en-US",  "English"),
    ("ja-JP",  "Japanese"),
    ("ko-KR",  "Korean"),
    ("de-DE",  "German"),
    ("fr-FR",  "French"),
    ("es-ES",  "Spanish"),
    ("pt-PT",  "Portuguese"),
    ("ru-RU",  "Russian"),
    ("ar-SA",  "Arabic"),
    ("hi-IN",  "Hindi"),
    ("pl-PL",  "Polish"),
    ("cs-CZ",  "Czech"),
    ("fi-FI",  "Finnish"),
    ("tr-TR",  "Turkish"),
    ("nl-NL",  "Dutch"),
    ("sv-SE",  "Swedish"),
    ("nb-NO",  "Norwegian"),
    ("da-DK",  "Danish"),
    ("id-ID",  "Indonesian"),
    ("uk-UA",  "Ukrainian"),
    ("ro-RO",  "Romanian"),
    ("bg-BG",  "Bulgarian"),
    ("ca-ES",  "Catalan"),
    ("el-GR",  "Greek"),
    ("fa-IR",  "Persian"),
    ("fil-PH", "Filipino"),
    ("he-IL",  "Hebrew"),
    ("hr-HR",  "Croatian"),
    ("hu-HU",  "Hungarian"),
    ("ms-MY",  "Malay"),
    ("sk-SK",  "Slovak"),
    ("sl-SI",  "Slovenian"),
    ("sr-RS",  "Serbian"),
    ("th-TH",  "Thai"),
    ("vi-VN",  "Vietnamese"),
]

_VALID_LANGUAGES = {code for code, _ in LANGUAGES}

# Strip ANSI escape codes from build output before sending to browser
_ANSI_RE = re.compile(r"\x1b(?:\[[0-9;]*[A-Za-z]|[^[])")

# ---------------------------------------------------------------------------
# Build state — protected by _build_lock
# ---------------------------------------------------------------------------

_build_lock = threading.Lock()
_build_active = False
_output_q: queue.Queue = queue.Queue()

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/")
def index():
    content = (WEBUI_DIR / "index.html").read_text(encoding="utf-8")
    return content, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/languages")
def get_languages():
    return jsonify([{"code": c, "name": n} for c, n in LANGUAGES])


@app.route("/build", methods=["POST"])
def build():
    global _build_active

    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "hardcoded")
    ota_url = (data.get("ota_url") or "").strip()
    language = data.get("language", "it-IT")

    if mode not in MODES:
        return jsonify({"error": f"Invalid mode: {mode!r}"}), 400
    if language not in _VALID_LANGUAGES:
        return jsonify({"error": f"Invalid language: {language!r}"}), 400

    # Use mode default if custom OTA URL not provided
    if not ota_url:
        ota_url = MODES[mode]

    with _build_lock:
        if _build_active:
            return jsonify({"error": "Build already in progress"}), 409
        _build_active = True
        # Clear stale queue entries from previous build
        while not _output_q.empty():
            try:
                _output_q.get_nowait()
            except queue.Empty:
                break

    threading.Thread(
        target=_build_thread,
        args=(mode, ota_url, language),
        daemon=True,
    ).start()

    return jsonify({"status": "started"}), 202


@app.route("/events")
def events():
    """Server-Sent Events stream — one JSON object per data line."""

    def generate():
        while True:
            try:
                item = _output_q.get(timeout=20)
            except queue.Empty:
                # Keepalive comment — prevents proxy/browser timeout
                yield ": keepalive\n\n"
                continue
            yield f"data: {json.dumps(item)}\n\n"
            if item.get("type") in ("done", "error"):
                break

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering if proxied
        },
    )


@app.route("/binaries")
def binaries():
    """List downloadable build artifacts."""
    if not BUILD_DIR.exists():
        return jsonify([])

    result = []
    candidates = [
        ("xiaozhi.bin",                    "xiaozhi.bin"),
        ("ota_data_initial.bin",           "ota_data_initial.bin"),
        ("bootloader/bootloader.bin",      "bootloader.bin"),
        ("partition_table/partition-table.bin", "partition-table.bin"),
    ]
    for rel_path, display_name in candidates:
        p = BUILD_DIR / rel_path
        if p.exists():
            result.append({
                "name": display_name,
                "path": rel_path,
                "size": p.stat().st_size,
            })
    return jsonify(result)


@app.route("/download/<path:filename>")
def download(filename):
    """Download a build artifact — path traversal protected."""
    target = (BUILD_DIR / filename).resolve()
    if not str(target).startswith(str(BUILD_DIR.resolve())):
        abort(403)
    if not target.exists():
        abort(404)
    return send_file(target, as_attachment=True)


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------

def _put(item: dict) -> None:
    _output_q.put(item)


def _log(text: str) -> None:
    _put({"type": "log", "text": _ANSI_RE.sub("", text)})


def _lang_to_config(code: str) -> str:
    """Convert 'it-IT' → 'CONFIG_LANGUAGE_IT_IT'."""
    return "CONFIG_LANGUAGE_" + code.replace("-", "_").upper()


def _get_cmake_target() -> "str | None":
    cmake_cache = BUILD_DIR / "CMakeCache.txt"
    if not cmake_cache.exists():
        return None
    for line in cmake_cache.read_text(encoding="utf-8").splitlines():
        if line.startswith("IDF_TARGET:STRING="):
            return line.split("=", 1)[1].strip()
    return None


def _stream_command(cmd: list, env: dict) -> int:
    """Run cmd, streaming each output line into _output_q. Returns exit code."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        cwd=PROJECT_ROOT,
        text=True,
        bufsize=1,
    )
    for line in proc.stdout:
        _log(line.rstrip())
    proc.wait()
    return proc.returncode


# ---------------------------------------------------------------------------
# Build thread
# ---------------------------------------------------------------------------

def _build_thread(mode: str, ota_url: str, language: str) -> None:
    global _build_active
    override = PROJECT_ROOT / OVERRIDE_FILENAME
    try:
        _do_build(mode, ota_url, language, override)
    except Exception as exc:
        _put({"type": "error", "message": f"Unexpected error: {exc}"})
    finally:
        if override.exists():
            override.unlink()
            _log(f"[webui] Removed {OVERRIDE_FILENAME}")
        with _build_lock:
            _build_active = False


def _do_build(mode: str, ota_url: str, language: str, override: Path) -> None:
    _log(f"[webui] Mode:     {mode}")
    _log(f"[webui] OTA URL:  {ota_url}")
    _log(f"[webui] Language: {language}")

    if shutil.which("idf.py") is None:
        _put({
            "type": "error",
            "message": "idf.py not found in PATH — run: source ~/esp/esp-idf/export.sh",
        })
        return

    # Write override file
    lang_config = _lang_to_config(language)
    override.write_text(
        f'CONFIG_OTA_URL="{ota_url}"\n{lang_config}=y\n',
        encoding="utf-8",
    )
    _log(f"[webui] Override: CONFIG_OTA_URL={ota_url}")
    _log(f"[webui] Override: {lang_config}=y")

    env = os.environ.copy()
    env["SDKCONFIG_DEFAULTS"] = ";".join(SDKCONFIG_CHAIN)

    # Set target if needed
    current_target = _get_cmake_target()
    if current_target != "esp32s3":
        _log(f"[webui] Current target: {current_target!r} — running: idf.py set-target esp32s3")
        rc = _stream_command(["idf.py", "set-target", "esp32s3"], env)
        if rc != 0:
            _put({"type": "done", "success": False, "returncode": rc, "binaries": []})
            return
    else:
        _log("[webui] Target already esp32s3")

    _log(f"[webui] SDKCONFIG_DEFAULTS={env['SDKCONFIG_DEFAULTS']}")
    _log("[webui] Running: idf.py build")

    rc = _stream_command(["idf.py", "build"], env)

    if rc != 0:
        _put({"type": "done", "success": False, "returncode": rc, "binaries": []})
        return

    # Collect available binaries
    bins = []
    for rel_path in [
        "xiaozhi.bin",
        "ota_data_initial.bin",
        "bootloader/bootloader.bin",
        "partition_table/partition-table.bin",
    ]:
        if (BUILD_DIR / rel_path).exists():
            bins.append(rel_path)

    _log("[webui] Build complete!")
    _put({"type": "done", "success": True, "returncode": 0, "binaries": bins})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"[webui] Project root: {PROJECT_ROOT}")
    print(f"[webui] Build dir:    {BUILD_DIR}")
    print("[webui] Open http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
