# TODO — my-xiaozhi-esp32 custom

## ✅ Completato
- [x] Mapping architettura xiaozhi-esp32 e Sibilla API
- [x] Confronto repo Spotpear ufficiale — nessuna sync necessaria
- [x] Build tool `scripts/build_firmware.py` (hardcoded/dynamic)
- [x] Fix `image_to_jpeg.h` per ESP-IDF 5.5
- [x] Board config `sp-esp32-s3-1.28-box` selezionata correttamente
- [x] Display GC9A01 acceso, lingua italiana
- [x] Connessione a Sibilla verificata end-to-end

## 🔄 In corso
- [ ] capire i sdkconfig.defaults sulla root del repo se possono essere rimossi

## ✅ Completato (aggiornamento 2026-04-10)
- [x] FASE 1: `CONFIG_OTA_URL` — URL default in Kconfig è `tenclass.net` ma viene sovrascritto correttamente da `build_firmware.py --mode hardcoded`. Nessuna modifica necessaria al sorgente.
- [x] Verificato provisioning WiFi via AP: tab "Advanced" include già campo OTA URL, funzionante, nessuna modifica necessaria
- [x] WebUI completata: `webui/` con server Flask porta 5001, `index.html`, `Start/Stop/Status .command`, `README.md`, `SETUP.md`

## 📋 Backlog
### Hardware (solo analisi, no action)
- [ ] **Volume**: handler nella board `sp-esp32-s3-1.28-box.cc`. Pattern: `main/boards/magiclick-2p5/magiclick_2p5_board.cc`
- [ ] **Power button**: mappare secondo pulsante fisico nella board. Pattern: `doit-s3-aibox.cc`
- [ ] **SD card** su SPI. Pin: CLK=17, CMD=18, D0=21, CS=13. Pattern: `main/boards/xingzhi-abs-2.0/xingzhi-abs-2.0.cc`. Note: assente nel firmware Spotpear originale, solo progetto Arduino separato

### Futuro
- [ ] **GitHub Actions**: build in cloud da WebUI → download binari compilati
