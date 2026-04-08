# TODO — xiaozhi-esp32 custom

## FASE 1 — Server Sibilla
- [ ] Modificare `main/Kconfig.projbuild` — CONFIG_OTA_URL = http://192.168.1.69:8003/xiaozhi/ota/
- [ ] Build test (idf.py build)
- [ ] Commit: `feat: point to Sibilla OTA server`
- [ ] **OPZIONALE (FASE 1B)**: Aggiungere NVS override in `main/ota.cc`
  * Namespace: "wifi", Key: "ota_url" (≤15 caratteri ✓)
  * Se presente in NVS, usa quello; altrimenti fallback CONFIG_OTA_URL
  * Commit: `feat: NVS override for OTA URL`

## FASE 2 — Display GC9A01
- [ ] Verificare offset `DISPLAY_OFFSET_X/Y` in `main/boards/sp-esp32-s3-1.28-box/config.h`
- [ ] Verificare init commands custom in `main/boards/sp-esp32-s3-1.28-box/sp-esp32-s3-1.28-box.cc`
- [ ] Test hardware (flash + monitor)
- [ ] Fix orario sync (NTP + timezone)

## FASE 3 — Lingua italiana
- [ ] Attivare CONFIG_LANGUAGE_IT_IT in sdkconfig.defaults
- [ ] Verificare `main/assets/locales/it-IT/language.json` (completezza stringhe)
- [ ] Build test
