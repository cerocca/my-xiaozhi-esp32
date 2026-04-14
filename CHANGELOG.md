# Changelog — my-xiaozhi-esp32 custom

## [session] — 2026-04-14 (SD card + timezone fix)
### Added
- SD card SPI support in `sp-esp32-s3-1.28-box.cc`:
  `InitializeSDcardSpi()` su SPI2_HOST (display su SPI3_HOST — bus separati).
  Pin: CLK=GPIO17, MOSI=GPIO18, MISO=GPIO21, CS=GPIO13.
  Mount point `/sdcard`, `format_if_mount_failed = false`.
  Stato salvato in `is_sdcard_found_`, mount failure graceful.
- Defines SD card aggiunti in `config.h`:
  `SD_DATA0`, `SD_CLK`, `SD_CMD`, `SD_CS`, `SD_MOUNT_POINT`, `SD_SPI_HOST`.

### Fixed
- `ota.cc`: orario del device non più impostato all'ora di Pechino.
  Root cause: il codice aggiungeva `timezone_offset: 480` (UTC+8) al timestamp UTC
  prima di `settimeofday`, spostando il clock di 8 ore in avanti.
  Fix: clock impostato a UTC puro + `setenv("TZ", "CET-1CEST,M3.5.0,M10.5.0/3", 1)`
  per gestire CET/CEST (DST Italia) automaticamente via libc.
  `localtime()` nel display converte ora UTC → ora italiana con DST corretto.

## [session] — 2026-04-13 (display fix)
### Fixed
- `lcd_display.cc`: identificato sub-branch `CONFIG_USE_MULTILINE_CHAT_MESSAGE`
  come branch attivo per la nostra board (non `#else`/DEFAULT-SINGLE)
- `bottom_bar_` ora mostrato correttamente in `SetChatMessage()`:
  era creato con `LV_OBJ_FLAG_HIDDEN` e mai reso visibile
- `bottom_bar_` riposizionato per display circolare 240×240:
  width `LV_HOR_RES * 0.75` (180px), align `BOTTOM_MID` offset `-44px`
- `chat_message_label_` width cambiato a `LV_PCT(100)` (relativo al parent)
- Rimosso `lv_obj_update_layout()` prematuro da `SetChatMessage()`
- Testo iniziale `" "` invece di `""` per garantire `height=line_height`
  al primo flex pass
### Added
- `InitializeIot()` in `sp-esp32-s3-1.28-box.cc` con MCP tools:
  `self.speaker.get_volume`, `self.speaker.set_volume`,
  `self.screen.get_brightness`, `self.screen.set_brightness`
- `ESP_LOGI(TAG, "DoToolCall: %s")` in `McpServer::DoToolCall()` per debug

### Fixed
- `InitializeIot()` svuotata: rimossi i 4 tool ridondanti con quelli
  di `AddCommonTools()` (`self.speaker.set_volume` duplicava
  `self.audio_speaker.set_volume`; `self.screen.set_brightness` aveva
  nome identico → dead code con `std::find_if` first-match)
- `[&board]` dangling reference in `AddCommonTools()` → `[b = &board]`

### Debug MCP tools
- Confermato che il device espone correttamente i tool al server via MCP:
  `tools/list` ricevuto, `GetToolsList` invia 11 tool tra cui
  `self.audio_speaker.set_volume` e `self.screen.set_brightness`
- `DoToolCall` mai chiamato → problema lato server/LLM, non firmware
- Aggiunti log diagnostici temporanei in `ParseMessage()` e `GetToolsList()`
  per future sessioni di debug (pattern documentato in CLAUDE.md)

### In sospeso
- IoT Tools: tool esposti correttamente dal device, LLM non li invoca
  (problema lato server, non firmware)
- SD card: non implementata, rimandata alla prossima sessione

## [session] — 2026-04-11 (wake word & esp-web-tools analysis)
### Analisi
- Wake word attiva: "Nihao Xiaozhi" (`CONFIG_SR_WN_WN9_NIHAOXIAOZHI_TTS=y`)
- Disponibili senza training: Hi ESP, Alexa, Jarvis, Sophia,
  Hey Willow, Mycroft, Computer, Hi M5, Hey Wanda + ~20 varianti cinesi
- Nessuna wake word italiana nel catalogo Espressif
- Wake word custom possibile via piattaforma Espressif (training richiesto)
- esp-web-tools (esphome/esp-web-tools): fattibile nella WebUI,
  limiti: solo Chrome/Edge, solo localhost senza HTTPS

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
