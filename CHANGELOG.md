# Changelog — my-xiaozhi-esp32 custom

## [session] — 2026-04-11
### Analisi
- Confronto completo Spotpear original vs fork su tutte le feature hardware
- SD card: confermata assenza in tutti i firmware ESP-IDF per questa board
- Pin SD confermati da Arduino demo: CLK=17, CMD=18, D0=21, CS=13
- IoT Things (Speaker+Screen): presente in Spotpear, assente nel fork

### In corso
- Display fix: migrazione branch `#else` `lcd_display.cc` al layout Spotpear
  con `content_` flex column — `chat_message_label_` e `emoji_box_` dentro `content_`,
  `bottom_bar_` hidden. Testo chat sparito dopo flash, debug necessario.

### Fixed
- Padding laterale `status_bar_` per schermo rotondo (79px) — confermato funzionante
- Offset `top_bar_` e `status_bar_` +20px verso il basso — testo boot visibile

## [session] — 2026-04-10 (docs cleanup)
### Changed
- `README.md`: titolo → "My xiaozhi esp32 firmware"; rimossi riferimenti a "Sibilla" → "custom server"; aggiunto link a `SETUP.md` nel primo blocco di testo
- `SETUP.md`: rimossi riferimenti a "Sibilla" e all'IP hardcoded nella sezione First boot → placeholder generico
- `CLAUDE.md`: rimossi riferimenti a "Sibilla" fuori dalla sezione "Sibilla — Infrastruttura"
- `TODO.md`, `CHANGELOG.md`: rimossi riferimenti a "Sibilla"

## [session] — 2026-04-10
### Aggiunto
- `SETUP.md` con istruzioni di installazione da zero su macOS (ESP-IDF, clone, build, flash, first boot)
- `README.md`: link a `SETUP.md` nella sezione Getting started; sostituzione immagini inline con `<img>` centrati; nuova sezione `## Images`; rimossi `README_ja.md` e `README_zh.md`; `README.md` originale rinominato in `README_original.md`

### Analisi
- Analisi sorgenti Spotpear originale e fork Arduino (`spotpear_original`, `spotpear_SDcard`)
- Chiusa FASE 1 (`CONFIG_OTA_URL`): URL default in Kconfig è `tenclass.net` ma viene sovrascritto correttamente da `build_firmware.py --mode hardcoded`; nessuna modifica necessaria al sorgente
- Check hardware completo: SD card, volume, power button, touch
- Mappati pin SD card da sorgenti Arduino Spotpear: CLK=17, CMD=18, D0=21, CS=13
- Identificati pattern di implementazione per volume e pulsanti nel repo upstream (`magiclick-2p5`, `doit-s3-aibox`, `xingzhi-abs-2.0`)
- Verificato: SD card assente nel firmware Spotpear originale (ESP-IDF), presente solo nel progetto Arduino separato
- Verificato provisioning WiFi via AP: campo OTA URL già presente nel tab Advanced (`wifi_configuration_ap.cc`), nessuna modifica necessaria

### Aggiunto
- WebUI completa in `webui/`: server Flask (porta 5001), interfaccia HTML con streaming SSE, script `Start/Stop/Status .command`, documentazione `README.md` e `SETUP.md`
- `webui/logs/` aggiunto a `.gitignore`

## [v2.2.4-custom-0.2] — 2026-04-09
### Added
- Board config `sp-esp32-s3-1.28-box` in `sdkconfig.defaults.esp32s3`
- Infrastruttura server custom documentata in CLAUDE.md

### Fixed
- Build tool ora imposta automaticamente target esp32s3
- `.claude/` escluso dal tracking git
- Tag upstream rimossi dal repo locale

## [v2.2.4-custom-0.1] — 2026-04-09
### Added
- `scripts/build_firmware.py` con modalità hardcoded e dynamic
- `scripts/firmware_outputs/` in .gitignore
- CLAUDE.md: gotcha ESP-IDF 5.5, target S3

### Fixed
- `image_to_jpeg.h`: rimossa condizione ESP32-S3 per `linux/videodev2.h`
  (non disponibile nel toolchain ESP-IDF 5.5)
- Aggiunto `# -*- coding: utf-8 -*-` a build_firmware.py
