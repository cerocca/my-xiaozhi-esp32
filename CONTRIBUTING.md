# Contributing

This document covers the technical information needed to build, modify, and contribute to this firmware.

---

## Project overview

Custom firmware for the **Spotpear ESP32-S3-1.28-BOX** (N16R8 — 16 MB flash, 8 MB PSRAM), based on [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) v2.2.4.

- **Toolchain**: ESP-IDF 5.5.2 or later (5.4 is not compatible)
- **Target chip**: ESP32-S3
- **Display**: GC9A01 1.28" round LCD, 240×240
- **Language**: C++ (ESP-IDF component model)

---

## Repository structure

| Path | Description |
|------|-------------|
| `main/` | Firmware source — application logic, board drivers, display, assets |
| `main/boards/sp-esp32-s3-1.28-box/` | Board-specific code: `config.h` (pins, display params), `sp-esp32-s3-1.28-box.cc` (init logic) |
| `main/display/lvgl_display/` | LVGL display layer, including `gif/` (gifdec decoder) and `jpg/` |
| `main/assets/locales/` | Locale strings — `language.json` per language, compiled to `lang_config.h` at build time |
| `sdkconfig.defaults` | Shared sdkconfig defaults |
| `sdkconfig.defaults.esp32s3` | ESP32-S3-specific sdkconfig overrides (board type, language, features) |
| `scripts/` | Build tools — `build_firmware.py` for hardcoded/dynamic server builds |
| `partitions/` | Partition table definitions |

---

## Build instructions

```bash
# Activate ESP-IDF toolchain (required in every new terminal)
source ~/esp/esp-idf/export.sh

# Build (standard)
idf.py build

# Clean rebuild from scratch
idf.py fullclean && idf.py build

# Set chip target (first build, or after fullclean)
idf.py set-target esp32s3

# Build with custom server URL hardcoded
python3 scripts/build_firmware.py --mode hardcoded

# Build with dynamic server (upstream default)
python3 scripts/build_firmware.py --mode dynamic

# Explore Kconfig options
idf.py menuconfig
```

> **CMake note**: after adding new `.c` files, run `idf.py reconfigure` before `idf.py build`.

> **Mac note**: always use `python3`, not `python` — macOS system `python` points to Python 2.7.

> **ESP-IDF source + pipe**: never pipe `source ~/esp/esp-idf/export.sh` — the `source` runs in a subshell and PATH changes are lost. Use instead:
> ```bash
> zsh -c 'source ~/esp/esp-idf/export.sh > /dev/null 2>&1 && idf.py build'
> ```

---

## Board-specific technical notes

### GC9A01 display

- The active display branch is **MULTILINE** (`CONFIG_USE_MULTILINE_CHAT_MESSAGE=y`).
  The `#else` (DEFAULT-SINGLE) branch is never compiled for this board.
- Display offset is defined in `config.h` (`DISPLAY_OFFSET_X/Y`). Any geometry fixes
  belong there, not in the generic driver.
- Custom init registers (0x62, 0x63, 0x36, 0xC3, 0xC4) are already implemented
  in `sp-esp32-s3-1.28-box.cc`.

### NVS key length

NVS keys must not exceed **15 characters** (ESP-IDF hard limit).

### sdkconfig vs sdkconfig.defaults

- `sdkconfig` is generated — do not commit it unless necessary.
- Persistent config changes go in `sdkconfig.defaults` or `sdkconfig.defaults.esp32s3`.
- Board type is selected via `CONFIG_BOARD_TYPE_*` in `sdkconfig.defaults.esp32s3`.
  Without this, the build defaults to `bread-compact-wifi`.

### Upstream git tags

Upstream tags (`v1.x`, `v2.x`) must not be pushed to this fork.
To clean them locally:
```bash
git tag | grep -v "custom" | xargs git tag -d
```

---

## Known gotcha

### `image_to_jpeg.h` with ESP-IDF 5.5

The original condition included `|| defined(CONFIG_IDF_TARGET_ESP32S3)` which pulled in
`<linux/videodev2.h>` — an S3-incompatible header from the P4-only `esp_video` component.
**Fix applied**: the S3 clause was removed. S3 now uses the manual `#define` fallback in
the `#else` branch. File: `main/display/lvgl_display/jpg/image_to_jpeg.h`.

### ESP32-S3 target not set automatically

If `build/` does not exist or contains a different target, `idf.py build` defaults to `esp32`.
`scripts/build_firmware.py` handles this automatically by reading `build/CMakeCache.txt`
and running `idf.py set-target esp32s3` if needed.

---

## Hardware feature status

### SD card (SPI)

Implemented on SPI2_HOST (display uses SPI3_HOST — separate buses).

| Signal | GPIO |
|--------|------|
| CLK    | 17   |
| MOSI   | 18   |
| MISO   | 21   |
| CS     | 13   |

Mount point: `/sdcard`. Failure is graceful (`is_sdcard_found_ = false`), the device continues normally.

### Button 2

Not currently mapped. To add a second button, follow the pattern in
`main/boards/doit-s3-aibox/doit_s3_aibox.cc`: declare a `Button` member and register
`OnClick()` / `OnDoubleClick()` / `OnLongPress()` callbacks.

### GIF playback

Full infrastructure is available. `LcdDisplay` has a `std::unique_ptr<LvglGif> gif_controller_`
(`lcd_display.h:32`) backed by the custom **gifdec** decoder
(`main/display/lvgl_display/gif/`). LVGL's own GIF support (`CONFIG_LV_USE_GIF`) is
disabled — gifdec is used instead. Already in use by `otto-robot` and `electron-bot` boards.

---

## Commit format

```
feat:     new feature
fix:      bug fix
docs:     documentation only
refactor: code change with no functional effect
```

Every commit must represent a **compilable state**.
