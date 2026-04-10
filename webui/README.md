# webui — Firmware Builder Web UI

Browser interface for building xiaozhi-esp32 firmware without touching the terminal.

## What it does

- Select build mode: **Hardcoded** (OTA URL points to local Sibilla server) or **Dynamic** (upstream default)
- Override the OTA URL for hardcoded builds
- Choose display language from all supported locales
- Stream `idf.py build` output live in the browser
- Download the compiled `.bin` files when the build finishes

## Usage

```bash
# From project root, with ESP-IDF already activated
python3 webui/server.py
# Open http://localhost:5000
```

See [SETUP.md](SETUP.md) for prerequisites and first-time setup.
