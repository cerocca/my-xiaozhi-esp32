# CLAUDE.md — xiaozhi-esp32 custom (Spotpear ESP32-S3)

## Progetto
Firmware custom per **Spotpear ESP32-S3-1.28-BOX** (N16R8, display rotondo GC9A01 1.28").
Basato su https://github.com/78/xiaozhi-esp32 — punta a server custom locale
invece di xiaozhi.me. Toolchain: ESP-IDF 5.5.2+, Mac, terminale.

Build:
```bash
source ~/esp/esp-idf/export.sh   # ogni nuovo terminale
idf.py build
```

> **CMake note**: quando si aggiungono nuovi file `.c`, eseguire
> `idf.py reconfigure` prima di `idf.py build`.

---

## Workflow

**Flash e monitor: sempre eseguiti manualmente dall'utente, non da Claude Code.**
Salvo istruzione esplicita, Claude Code si ferma a `idf.py build`.

Comandi di riferimento (solo documentazione):
```bash
source ~/esp/esp-idf/export.sh
idf.py build flash
idf.py -p /dev/cu.usbserial-XXXX monitor
```

---

## Architettura decisa

- **Server**: URL server custom hardcoded come default nel firmware.
  Override via NVS se presente (chiave NVS: da definire durante sviluppo).
  Non dipende da xiaozhi.me in alcun modo.
- **Display**: nuova board config `main/boards/spotpear_s3_1_28.json`
  seguendo il pattern JSON già esistente nel repo.
- **WiFi provisioning**: riutilizzare il meccanismo esistente nel codebase,
  senza modifiche alla logica di provisioning.

---

## Regole core

1. **Seguire sempre i pattern già esistenti nel codebase** — board config JSON,
   NVS per config, stessa struttura dei file esistenti.
2. **Indicare sempre il percorso esatto** di ogni file creato o modificato.
3. **Non toccare la logica WiFi/provisioning** esistente.
4. **Non toccare** la logica audio, MCP, ASR/TTS — salvo istruzione esplicita.
5. **Preservare tutta la funzionalità esistente** a ogni iterazione,
   salvo istruzione esplicita.
6. **Pianificare prima di scrivere codice**: descrivere brevemente l'approccio,
   identificare i file coinvolti, poi implementare.
7. Ogni funzione deve avere uno scopo singolo e chiaro.
8. Gestire sempre gli errori esplicitamente (no silent failures).
9. **Aggiornare CLAUDE.md** a fine sessione con gotcha scoperti, pattern
   confermati, o decisioni architetturali prese — prima del commit.

---

## Note tecniche e gotcha

- **Display GC9A01**: problema noto di offset su schermo rotondo 1.28".
  Il fix va nella board config JSON, non nel driver generico.
- **NVS key length**: mai superare 15 caratteri per le chiavi NVS
  (limite ESP-IDF).
- **sdkconfig vs sdkconfig.defaults**: modifiche persistenti vanno in
  `sdkconfig.defaults`. `sdkconfig` è generato — non committarlo se
  non necessario.
- **Board target**: ESP32-S3, chip N16R8 (16MB flash, 8MB PSRAM).
  Verificare che `sdkconfig.defaults.esp32s3` sia allineato.
- **ESP-IDF versione minima 5.5.2**: ESP-IDF 5.4 non è compatibile.
  Dopo aggiornamento a 5.5, reinstallare l'ambiente Python da terminale pulito:
  ```bash
  rm -rf ~/.espressif/python_env/idf5.4_py3.14_env
  cd ~/esp/esp-idf && ./install.sh
  ```
- **Target ESP32-S3 non impostato automaticamente**: se `build/` non esiste o
  contiene un target diverso, `idf.py build` usa `esp32` come default.
  `scripts/build_firmware.py` gestisce questo automaticamente leggendo
  `build/CMakeCache.txt` e lanciando `idf.py set-target esp32s3` se necessario.
- **Bug `image_to_jpeg.h` con ESP-IDF 5.5**: la condizione originale
  `#if defined(CONFIG_IDF_TARGET_ESP32P4) || defined(CONFIG_IDF_TARGET_ESP32S3)`
  includeva `<linux/videodev2.h>` anche per S3, ma quell'header non esiste nel
  toolchain S3 (appartiene al componente `esp_video` di P4 only).
  Fix locale applicato: rimossa la clausola `|| defined(CONFIG_IDF_TARGET_ESP32S3)` —
  S3 usa ora i `#define` manuali nel ramo `#else`.
  File: `main/display/lvgl_display/jpg/image_to_jpeg.h`.
- **`python` vs `python3` su Mac**: su macOS `python` punta a Python 2.7 (system).
  Usare sempre `python3` per lanciare gli script del progetto.
  Comando corretto: `python3 scripts/build_firmware.py --mode hardcoded`
- **Board selection via Kconfig**: la board viene selezionata tramite `CONFIG_BOARD_TYPE_*`.
  Il valore va impostato in `sdkconfig.defaults.esp32s3`. Senza questo, il build
  sceglie `bread-compact-wifi` come default.
- **Tag upstream in locale**: i tag upstream (`v1.x`, `v2.x`) non vanno pushati.
  Per pulirli: `git tag | grep -v "custom" | xargs git tag -d`
- **Versione firmware**: hardcodata in `CMakeLists.txt` alla riga
  `set(PROJECT_VER "2.2.5")`. Non dipende da `git describe`.
- **Provisioning WiFi via AP — OTA URL già configurabile**: durante il
  provisioning AP, il tab "Advanced" della pagina web del device permette
  già di inserire un Custom OTA URL. Viene salvato in NVS namespace "wifi",
  chiave "ota_url". ota.cc lo legge e sovrascrive CONFIG_OTA_URL (Kconfig).
  Se assente, usa il default compilato. Meccanismo completo, nessuna modifica
  necessaria. File: `managed_components/78__esp-wifi-connect/wifi_configuration_ap.cc`
- **WebUI — porta 5001**: la WebUI Flask gira su porta 5001 (non 5000,
  occupata da AirPlay Receiver su Mac). Script: `webui/Start WebUI.command`,
  `webui/Stop WebUI.command`, `webui/Status WebUI.command`.
- **SD card — pin noti, non implementata**: slot SD fisico presente sulla
  board. Pin da Arduino Spotpear: CLK=17, CMD=18, D0=21, CS=13. Pattern
  ESP-IDF disponibile in `main/boards/xingzhi-abs-2.0/`. Non implementata
  nel firmware xiaozhi originale per questa board.
- **Contributors GitHub**: il repo eredita tutti i contributor del repo
  upstream 78/xiaozhi-esp32. Claude Code firma i commit con le credenziali
  git locali dell'utente, non con identità propria.
- **sdkconfig e sdkconfig.old**: già in `.gitignore`, non committare.
  Solo `sdkconfig.defaults` e `sdkconfig.defaults.esp32s3` sono rilevanti
  per questo progetto.
- **lv_obj_set_y / lv_obj_align su bottom_bar_ non funzionano**:
  durante SetupUI() LVGL resetta le coordinate al primo layout pass.
  Workaround: usare layout flex (`content_`) invece di posizionamento manuale.
- **lv_obj_get_y restituisce 0 durante SetupUI()**: LVGL calcola le
  coordinate in modo lazy — `lv_obj_get_y` può restituire 0 finché non
  è avvenuto il primo layout pass. Non usare `get_y` per verifiche
  durante la costruzione dei widget.
- **Display branch attivo per la nostra board: MULTILINE** (non SINGLE/ELSE).
  `CONFIG_USE_MULTILINE_CHAT_MESSAGE=y` è nel `sdkconfig` generato — persiste
  tra i build. Il sub-branch `#else` (DEFAULT-SINGLE) non viene mai compilato.
  Per verificare: aggiungere `ESP_LOGI` all'inizio di ogni branch e flashare.
- **Bug display fix — root cause**: `bottom_bar_` creato con
  `lv_obj_add_flag(bottom_bar_, LV_OBJ_FLAG_HIDDEN)` ("hide until content")
  ma `SetChatMessage()` non lo mostrava mai. Fix: aggiungere
  `lv_obj_remove_flag(bottom_bar_, LV_OBJ_FLAG_HIDDEN)` prima di
  `lv_obj_align` nel blocco `#if CONFIG_USE_MULTILINE_CHAT_MESSAGE`.
- **Display circolare 240×240 — posizionamento bottom_bar_**: a y=196
  (offset -44px dal bordo) la corda è ~186px > 180px (LV_HOR_RES*0.75).
  Valori corretti: `lv_obj_set_width(bottom_bar_, LV_HOR_RES * 0.75)` +
  `lv_obj_align(bottom_bar_, LV_ALIGN_BOTTOM_MID, 0, -44)`.
  Usare `LV_PCT(100)` per la larghezza di `chat_message_label_` (si adatta al parent).
- **lv_obj_update_layout() in SetChatMessage() è controproducente**: LVGL
  ricalcola automaticamente il layout al prossimo render tick quando il testo
  cambia. Chiamarlo esplicitamente dopo `lv_label_set_text` può eseguire il
  layout prima che il label abbia ricalcolato le proprie dimensioni — risultato:
  posizione stale. Non aggiungere chiamate manuali a `lv_obj_update_layout`.
- **Testo iniziale " " invece di ""**: i label con `LV_LABEL_LONG_WRAP` e
  testo vuoto `""` possono avere `height=0` al primo flex pass. Il flex engine
  "congela" la posizione a h=0, rendendo il testo invisibile anche dopo
  `SetChatMessage()`. Usare `" "` (spazio) come testo iniziale garantisce
  `height=line_height` dal primo layout pass.
- **Debug tool MCP — `DoToolCall` log**: aggiungere
  `ESP_LOGI(TAG, "DoToolCall: %s", tool_name.c_str())` all'inizio di
  `McpServer::DoToolCall()` in `mcp_server.cc`. Se non appare nel monitor
  quando si chiede di cambiare volume/luminosità, il LLM non sta invocando
  i tool — problema nel system prompt del server, non nel firmware.
- **Debug tool MCP — `ParseMessage` log**: aggiungere
  `ESP_LOGI(TAG, "ParseMessage: method=%s", method->valuestring)` in
  `McpServer::ParseMessage()` dopo aver estratto `method_str`. Permette
  di verificare se il server invia `initialize` e `tools/list` dopo l'hello.
  Se nessun messaggio appare → il server non avvia l'handshake MCP.
- **Debug tool MCP — `GetToolsList` log**: aggiungere in `GetToolsList()`
  prima del loop: `ESP_LOGI(TAG, "GetToolsList: total=%d", (int)tools_.size())`
  e per ogni tool `ESP_LOGI(TAG, "GetToolsList: tool=%s", t->name().c_str())`.
  Se `tools/list` arriva e `GetToolsList` mostra tool corretti ma
  `DoToolCall` non appare mai → il problema è lato server/LLM, non firmware.
- **`InitializeIot()` — non duplicare tool di `AddCommonTools()`**:
  registrare in `InitializeIot()` tool con lo stesso nome o la stessa
  funzione di quelli comuni causa conflitti e confonde il LLM.
  Tool già disponibili via `AddCommonTools()`:
  `self.audio_speaker.set_volume`, `self.screen.set_brightness`,
  `self.screen.set_theme`, `self.get_device_status`.
  `InitializeIot()` deve contenere solo tool board-specifici non coperti
  da quelli comuni.
- **`InitializeIot()` per Spotpear S3 1.28 — lasciare vuota**: tutti i tool
  utili (volume, luminosità, status, tema) sono già esposti da `AddCommonTools()`.
  Non aggiungere nulla in `InitializeIot()` per questa board.

---

## Sibilla — Infrastruttura

- **Host**: sibilla (IP fisso LAN: `192.168.1.69`)
- **Deploy**: Docker container via docker-compose
- **Directory**: `/home/ciru/xiaozhi-esp32-lightserver`
- **Image**: `ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest`
- **Container**: `xiaozhi-esp32-server`
- **Porte**: `8000` (WebSocket `/xiaozhi/v1/`), `8003` (OTA `/xiaozhi/ota/`)
- **Log**: `docker logs xiaozhi-esp32-server -f`
- **Avvio**: `cd /home/ciru/xiaozhi-esp32-lightserver && docker compose up -d`

---

## Struttura rilevante del repo
xiaozhi-esp32/
├── CLAUDE.md
├── CMakeLists.txt
├── sdkconfig.defaults
├── sdkconfig.defaults.esp32s3      ← configurazione chip target
├── main/
│   ├── boards/                     ← board config JSON (pattern da seguire)
│   │   └── spotpear_s3_1_28.json  ← DA CREARE
│   ├── application.cc              ← logica principale
│   └── ...
├── partitions/
└── scripts/

> Esplorare `main/boards/` all'inizio di ogni sessione per verificare
> i pattern JSON esistenti prima di creare nuovi file.

---

## Comandi utili

```bash
# Attivare toolchain (ogni nuovo terminale)
source ~/esp/esp-idf/export.sh

# Build
idf.py build

# Pulire e rebuilare da zero
idf.py fullclean && idf.py build

# Impostare target chip (prima volta o dopo fullclean)
idf.py set-target esp32s3

# Menuconfig (esplora opzioni sdkconfig)
idf.py menuconfig

# Build firmware con server hardcoded (custom server)
python3 scripts/build_firmware.py --mode hardcoded

# Build firmware con server dinamico (upstream default)
python3 scripts/build_firmware.py --mode dynamic

# Scrivere un valore NVS via monitor (per test override server)
# Usare il menu di provisioning esistente o nvs_flash tool
```

---

## Session 1 Notes — Architecture & Server Discovery

### ✅ Architettura xiaozhi-esp32 confermata
- **Board**: `main/boards/sp-esp32-s3-1.28-box/` esiste già (non va creata)
  * `config.h` — pin + display params (DISPLAY_OFFSET_X/Y, DISPLAY_MIRROR_X, ecc.)
  * `config.json` — chip target + sdkconfig overrides
  * `sp-esp32-s3-1.28-box.cc` — logica board completa (GC9A01 init, ES8311, CST816D)
- **Driver GC9A01**: già implementato con init commands custom (registri 0x62, 0x63, 0x36, 0xC3, 0xC4)
- **Testi UI**: gestiti da `main/assets/locales/<lang>/language.json` (zero hardcoding)
  * Pipeline build-time: language.json → scripts/gen_lang.py → lang_config.h
  * Lingua selezionata a compile-time via CONFIG_LANGUAGE_*
  * `it-IT/language.json` esiste già — basta attivare CONFIG_LANGUAGE_IT_IT

### ✅ Flusso server confermato
1. Firmware legge `CONFIG_OTA_URL` (default in Kconfig.projbuild)
2. Contatta OTA server → riceve JSON con `websocket.url`
3. Salva in NVS namespace "websocket", key "url"
4. WebSocket protocol legge da NVS e connette
5. **NVS namespaces**: "websocket" (url, token, version), "wifi" (ota_url), "mqtt" (endpoint, client_id, username, password, publish_topic), "system" (uuid)

### ✅ Custom Server API — Mapping completo
- **OTA endpoint**: `http://192.168.1.69:8003/xiaozhi/ota/` (POST con Device-Id + Client-Id header)
- **WebSocket endpoint**: `ws://192.168.1.69:8000/xiaozhi/v1/` (inviato dal server in risposta OTA)
- **Risposta OTA JSON**:
```json
  {
    "server_time": { "timestamp": 1775664956975, "timezone_offset": 480 },
    "firmware": { "version": "0.9.9", "url": "" },
    "websocket": { "url": "ws://192.168.1.69:8000/xiaozhi/v1/", "token": "" }
  }
```
- **Auth**: Disabilitata (token: "")
- **Protocollo**: WebSocket puro (non MQTT)
- **Compatibilità**: 100% — nessuna modifica al protocollo necessaria

### 🎯 File da modificare (vedere TODO.md per dettagli)
- FASE 1: `main/Kconfig.projbuild` (CONFIG_OTA_URL)
- FASE 1B (opzionale): `main/ota.cc` (NVS override)
- FASE 2: `main/boards/sp-esp32-s3-1.28-box/config.h` + `sp-esp32-s3-1.28-box.cc` (se necessario)
- FASE 3: `sdkconfig.defaults` (CONFIG_LANGUAGE_IT_IT)

### ✅ Confronto con Spotpear ufficiale (Repo upstream)
- **Repo 1 (tuo)** è più avanzato e robusto di Repo 2 (Spotpear wiki)
- Differenze critiche mappate (GC9A01 registri, partition table, bug fixes)
- **Conclusione**: Nessuna sincronizzazione da Spotpear necessaria
- Il fork v2.2.4 è il punto di partenza migliore per il custom server
- Dettagli: vedere documento di confronto nella sessione precedente

### ⚠️ Gotcha scoperti
- NVS key max 15 caratteri (confirmed: "ota_url" = 7, "websocket_url" = 14, OK)
- Board config JSON è minimalista — logica vera è in config.h + .cc
- Timezone server: UTC+8 — verificare sincronizzazione NTP per Italia (device dovrebbe auto-sincronizzarsi via NTP ma timezone offset potrebbe essere obsoleto)
- Display offset: attualmente 0,0 in config.h — verificare empiricamente se serve tuning

---

## Session 2 Notes — Display fix & analisi comparativa

### ✅ Analisi comparativa Spotpear vs fork
- Fork superiore su: touch CST816D, GC9A01 init, battery/power management,
  deep sleep, WiFi config mode
- Spotpear superiore su: IoT Things (Speaker+Screen) — unica feature mancante
- SD card: assente in tutti i firmware ESP-IDF, solo demo Arduino separato
  (pin confermati: CLK=17, CMD=18, D0=21, CS=13)

### ✅ Display fix — root cause identificata
- Spotpear: `chat_message_label_` in `content_` flex al centro (Y≈120, corda 240px)
- Fork originale: `chat_message_label_` in `bottom_bar_` a Y=208 (corda ~163px)
- `lv_obj_align` e `lv_obj_set_y` ignorati da LVGL durante SetupUI()
- Fix applicato: padding laterale `status_bar_` (79px) ✅
- Fix applicato: offset `top_bar_` e `status_bar_` +20px verso il basso ✅
- Fix in corso: migrazione a layout `content_` flex — testo sparito, da debuggare

### 🎯 Prossima sessione
- Debug `SetChatMessage()` con nuovo layout `content_`
- IoT Things: `InitializeIot()` con `Speaker` + `Screen`
- SD card SPI

---

## Pre-commit checklist

- [ ] **CLAUDE.md** aggiornato con learnings della sessione ← sempre primo
- [ ] **TODO.md** aggiornato (aggiungi/spunta task)
- [ ] **CHANGELOG.md** aggiornato con le modifiche fatte
- [ ] Verificare che `sdkconfig` non includa path locali da non committare
- [ ] Verificare che `.claude/` non sia tracciato da git (`git status` non deve mostrarlo)
- [ ] Solo dopo conferma utente: `git add` e `git commit`

Formato commit: `feat:`, `fix:`, `docs:`, `refactor:` — ogni commit
deve rappresentare uno stato compilabile.
