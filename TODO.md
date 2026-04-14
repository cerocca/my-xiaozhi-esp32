# TODO — my-xiaozhi-esp32

## 🔴 In corso

- [x] **Display fix** — testo chat visibile su display circolare ✅

## 🔧 Ongoing — Hardware
(solo analisi e implementazione futura, no action immediata)

- [ ] Volume: aggiungere handler nella board (`sp-esp32-s3-1.28-box.cc`). Pattern: `main/boards/magiclick-2p5/magiclick_2p5_board.cc`
- [ ] Power button: mappare secondo pulsante fisico nella board. Pattern: `doit-s3-aibox.cc`
- [x] SD card: implementata su SPI2_HOST. Pin: CLK=17, CMD=18, D0=21, CS=13. Mount point `/sdcard`. Fallimento graceful. ✅

## 🔵 Futuro
- [ ] **IoT Tools**: il LLM risponde verbalmente senza invocare i tool MCP
  (volume, luminosità e qualsiasi altro tool).
  Causa: problema lato server — il device espone correttamente i tool via MCP
  (confermato da log: `tools/list` ricevuto, `GetToolsList` invia 11 tool
  incluso `self.audio_speaker.set_volume`) ma il LLM non li invoca.
  `DoToolCall` mai chiamato → fix in corso lato server.
- [ ] **Traduzione documentazione in inglese**:
  `CLAUDE.md`, `TODO.md`, `CHANGELOG.md`, `SETUP.md` sono in italiano.
  Valutare se tradurre in inglese per compatibilità con contributori
  esterni e standard open source.
- [x] **Fix orario sballato**: `ota.cc` ignorava il `timezone_offset` del server (UTC+8)
  aggiungendolo al timestamp UTC → clock impostato all'ora di Pechino.
  Fix: clock impostato a UTC puro + `setenv("TZ", "CET-1CEST,...")` per DST italiano automatico. ✅
- [ ] **esp-web-tools**: integra flash via browser nella WebUI.
  Richiede: endpoint `/manifest.json` in `server.py`, web component
  in `index.html`, verifica offset da partition table.
  Limite: solo localhost (non LAN) senza HTTPS.
  Stima: 2-3 ore.
- [ ] **Wake word**: cambiare da "Nihao Xiaozhi" a wake word
  più adatta (es. "Sophia" `CONFIG_SR_WN_WN9_SOPHIA_TTS=y`).
  Modifica: 1 riga in `sdkconfig.defaults.esp32s3` + `rm sdkconfig` + rebuild.
- [ ] **IoT Things**: `InitializeIot()` con `CreateThing("Speaker")` e
  `CreateThing("Screen")` in `sp-esp32-s3-1.28-box.cc`
- [ ] GitHub Actions: build in cloud da WebUI → download binari compilati
- [ ] Cleanup repo: rimuovere docs originali non più usati e sdkconfig.defaults per target non rilevanti (esp32, esp32c3, esp32c5, esp32c6, esp32p4)
