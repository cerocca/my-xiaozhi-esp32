# Changelog — my-xiaozhi-esp32 custom

## [session] — 2026-04-14 (SD card + timezone fix)
### Added
- SD card SPI support in `sp-esp32-s3-1.28-box.cc`:
  `InitializeSDcardSpi()` on SPI2_HOST (display on SPI3_HOST — separate buses).
  Pins: CLK=GPIO17, MOSI=GPIO18, MISO=GPIO21, CS=GPIO13.
  Mount point `/sdcard`, `format_if_mount_failed = false`.
  State stored in `is_sdcard_found_`, mount failure is graceful.
- SD card defines added to `config.h`:
  `SD_DATA0`, `SD_CLK`, `SD_CMD`, `SD_CS`, `SD_MOUNT_POINT`, `SD_SPI_HOST`.

### Fixed
- `ota.cc`: device clock no longer set to Beijing time.
  Root cause: the code was adding `timezone_offset: 480` (UTC+8) to the UTC timestamp
  before `settimeofday`, shifting the clock 8 hours forward.
  Fix: clock set to pure UTC + `setenv("TZ", "CET-1CEST,M3.5.0,M10.5.0/3", 1)`
  to handle CET/CEST (Italy DST) automatically via libc.
  `localtime()` in the display now correctly converts UTC → Italian local time with DST.

## [session] — 2026-04-13 (display fix)
### Fixed
- `lcd_display.cc`: identified `CONFIG_USE_MULTILINE_CHAT_MESSAGE` sub-branch
  as the active branch for our board (not `#else`/DEFAULT-SINGLE)
- `bottom_bar_` now shown correctly in `SetChatMessage()`:
  was created with `LV_OBJ_FLAG_HIDDEN` and never made visible
- `bottom_bar_` repositioned for 240×240 round display:
  width `LV_HOR_RES * 0.75` (180px), align `BOTTOM_MID` offset `-44px`
- `chat_message_label_` width changed to `LV_PCT(100)` (relative to parent)
- Removed premature `lv_obj_update_layout()` call from `SetChatMessage()`
- Initial text set to `" "` instead of `""` to ensure `height=line_height`
  at the first flex pass

### Added
- `InitializeIot()` in `sp-esp32-s3-1.28-box.cc` with MCP tools:
  `self.speaker.get_volume`, `self.speaker.set_volume`,
  `self.screen.get_brightness`, `self.screen.set_brightness`
- `ESP_LOGI(TAG, "DoToolCall: %s")` in `McpServer::DoToolCall()` for debug

### Fixed
- `InitializeIot()` cleared: removed 4 tools redundant with those from
  `AddCommonTools()` (`self.speaker.set_volume` duplicated
  `self.audio_speaker.set_volume`; `self.screen.set_brightness` had
  identical name → dead code with `std::find_if` first-match)
- `[&board]` dangling reference in `AddCommonTools()` → `[b = &board]`

### Debug MCP tools
- Confirmed the device correctly exposes tools to the server via MCP:
  `tools/list` received, `GetToolsList` sends 11 tools including
  `self.audio_speaker.set_volume` and `self.screen.set_brightness`
- `DoToolCall` never called → issue is server/LLM side, not firmware
- Added temporary diagnostic logs in `ParseMessage()` and `GetToolsList()`
  for future debug sessions (pattern documented in CLAUDE.md)

### Pending
- IoT Tools: tools correctly exposed by the device, LLM does not invoke them
  (server-side issue, not firmware)
- SD card: not implemented, deferred to next session

## [session] — 2026-04-11 (wake word & esp-web-tools analysis)
### Analysis
- Active wake word: "Nihao Xiaozhi" (`CONFIG_SR_WN_WN9_NIHAOXIAOZHI_TTS=y`)
- Available without training: Hi ESP, Alexa, Jarvis, Sophia,
  Hey Willow, Mycroft, Computer, Hi M5, Hey Wanda + ~20 Chinese variants
- No Italian wake word in the Espressif catalogue
- Custom wake word possible via Espressif platform (training required)
- esp-web-tools (esphome/esp-web-tools): feasible in the WebUI,
  limitations: Chrome/Edge only, localhost only without HTTPS

## [session] — 2026-04-11
### Analysis
- Full comparison Spotpear original vs fork across all hardware features
- SD card: confirmed absent in all ESP-IDF firmware for this board
- SD pins confirmed from Arduino demo: CLK=17, CMD=18, D0=21, CS=13
- IoT Things (Speaker+Screen): present in Spotpear, absent in the fork

### In progress
- Display fix: migrating `#else` branch in `lcd_display.cc` to Spotpear layout
  with `content_` flex column — `chat_message_label_` and `emoji_box_` inside `content_`,
  `bottom_bar_` hidden. Chat text disappeared after flash, debug needed.

### Fixed
- Side padding on `status_bar_` for round screen (79px) — confirmed working
- `top_bar_` and `status_bar_` offset +20px downward — boot text visible

## [session] — 2026-04-10 (docs cleanup)
### Changed
- `README.md`: title → "My xiaozhi esp32 firmware"; removed references to custom server IP → generic placeholder; added link to `SETUP.md` in first text block
- `SETUP.md`: removed hardcoded IP references in First boot section → generic placeholder
- `CLAUDE.md`: removed out-of-place server references outside the dedicated infrastructure section
- `TODO.md`, `CHANGELOG.md`: removed server-specific references

## [session] — 2026-04-10
### Added
- `SETUP.md` with full installation guide from scratch on macOS (ESP-IDF, clone, build, flash, first boot)
- `README.md`: link to `SETUP.md` in Getting started section; replaced inline images with centred `<img>` tags; new `## Images` section; removed `README_ja.md` and `README_zh.md`; original `README.md` renamed to `README_original.md`

### Analysis
- Analysed Spotpear original and Arduino fork sources (`spotpear_original`, `spotpear_SDcard`)
- Closed PHASE 1 (`CONFIG_OTA_URL`): default URL in Kconfig is `tenclass.net` but correctly overridden by `build_firmware.py --mode hardcoded`; no source changes needed
- Full hardware check: SD card, volume, power button, touch
- SD card pins mapped from Spotpear Arduino sources: CLK=17, CMD=18, D0=21, CS=13
- Identified implementation patterns for volume and buttons in upstream repo (`magiclick-2p5`, `doit-s3-aibox`, `xingzhi-abs-2.0`)
- Confirmed: SD card absent in original Spotpear ESP-IDF firmware, present only in separate Arduino project
- Confirmed WiFi AP provisioning: OTA URL field already present in Advanced tab (`wifi_configuration_ap.cc`), no changes needed

### Added
- Full WebUI in `webui/`: Flask server (port 5001), HTML interface with SSE streaming, `Start/Stop/Status .command` scripts, `README.md` and `SETUP.md` documentation
- `webui/logs/` added to `.gitignore`

## [v2.2.4-custom-0.2] — 2026-04-09
### Added
- Board config `sp-esp32-s3-1.28-box` in `sdkconfig.defaults.esp32s3`
- Custom server infrastructure documented in CLAUDE.md

### Fixed
- Build tool now automatically sets target esp32s3
- `.claude/` excluded from git tracking
- Upstream tags removed from local repo

## [v2.2.4-custom-0.1] — 2026-04-09
### Added
- `scripts/build_firmware.py` with hardcoded and dynamic modes
- `scripts/firmware_outputs/` in .gitignore
- CLAUDE.md: ESP-IDF 5.5 gotchas, S3 target

### Fixed
- `image_to_jpeg.h`: removed ESP32-S3 condition for `linux/videodev2.h`
  (not available in ESP-IDF 5.5 toolchain)
- Added `# -*- coding: utf-8 -*-` to build_firmware.py
