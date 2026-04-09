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
- [ ] FASE 1: `main/Kconfig.projbuild` — CONFIG_OTA_URL default su Sibilla

## 📋 Backlog
- [ ] interfaccia web per configuratore build
- [ ] FASE 3: Documentazione README.md
- [ ] Display offset/calibrazione (verificare empiricamente)
- [ ] ASR italiano su Sibilla (problema trascrizione in inglese)
- [ ] gestione pulsanti / sleep screen
- [ ] gestione SD
- [ ] implementazione immagini come Spotpear 
- [ ] NVS override server URL (chiave da definire)
- [ ] Secondo device (futuro)
