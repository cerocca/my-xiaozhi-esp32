# CLAUDE.md — xiaozhi-esp32 custom (Spotpear ESP32-S3)

## Progetto
Firmware custom per **Spotpear ESP32-S3-1.28-BOX** (N16R8, display rotondo GC9A01 1.28").
Basato su https://github.com/78/xiaozhi-esp32 — punta a server custom locale
invece di xiaozhi.me. Toolchain: ESP-IDF 5.4+, Mac, terminale.

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

# Scrivere un valore NVS via monitor (per test override server)
# Usare il menu di provisioning esistente o nvs_flash tool
```

---

## Session 1 Notes — Mapping Sibilla & Architecture Discovery

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

### ✅ Sibilla API — Mapping completo
- **OTA endpoint**: `http://192.168.1.69:8003/xiaozhi/ota/` (POST con Device-Id + Client-Id header)
- **WebSocket endpoint**: `ws://192.168.1.69:8000/xiaozhi/v1/` (inviato da Sibilla in risposta OTA)
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
- Il fork v2.2.4 è il punto di partenza migliore per Sibilla custom
- Dettagli: vedere documento di confronto nella sessione precedente

### ⚠️ Gotcha scoperti
- NVS key max 15 caratteri (confirmed: "ota_url" = 7, "websocket_url" = 14, OK)
- Board config JSON è minimalista — logica vera è in config.h + .cc
- Timezone Sibilla: UTC+8 — verificare sincronizzazione NTP per Italia (device dovrebbe auto-sincronizzarsi via NTP ma timezone offset potrebbe essere obsoleto)
- Display offset: attualmente 0,0 in config.h — verificare empiricamente se serve tuning

---

## Pre-commit checklist

- [ ] **CLAUDE.md** aggiornato con learnings della sessione ← sempre primo
- [ ] **TODO.md** aggiornato (aggiungi/spunta task)
- [ ] **CHANGELOG.md** aggiornato con le modifiche fatte
- [ ] Verificare che `sdkconfig` non includa path locali da non committare
- [ ] Solo dopo conferma utente: `git add` e `git commit`

Formato commit: `feat:`, `fix:`, `docs:`, `refactor:` — ogni commit
deve rappresentare uno stato compilabile.
