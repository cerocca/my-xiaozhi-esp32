# Changelog — my-xiaozhi-esp32 custom

## [v2.2.4-custom-0.2] — 2026-04-09
### Added
- Board config `sp-esp32-s3-1.28-box` in `sdkconfig.defaults.esp32s3`
- Infrastruttura Sibilla documentata in CLAUDE.md

### Fixed
- Build tool ora imposta automaticamente target esp32s3
- `.claude/` escluso dal tracking git
- Tag upstream rimossi dal repo locale

## [v2.2.4-custom-0.1] — 2026-04-09
### Added
- `scripts/build_firmware.py` con modalità hardcoded (Sibilla) e dynamic
- `scripts/firmware_outputs/` in .gitignore
- CLAUDE.md: gotcha ESP-IDF 5.5, target S3

### Fixed
- `image_to_jpeg.h`: rimossa condizione ESP32-S3 per `linux/videodev2.h`
  (non disponibile nel toolchain ESP-IDF 5.5)
- Aggiunto `# -*- coding: utf-8 -*-` a build_firmware.py
