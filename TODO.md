# TODO — my-xiaozhi-esp32

## 🔵 Backlog

### Upstream sync — fix pendenti
- [ ] Cherry-pick GPIO_NUM_NC crash fix (commit `280b2ff`) —
      verificare prima se `LAMP_GPIO` o `BUILTIN_LED_GPIO = GPIO_NUM_NC`
      nella config Spotpear (`main/boards/spotpear-esp32s3-lcd-1_54/config.h`)
- [ ] Aggiornamento dipendenze upstream: `esp_codec_dev ~1.5.6`, `lvgl ~9.5.0` —
      sessione dedicata; verificare compatibilità con `lcd_display.cc` custom
      (Spotpear flex layout, round display path) prima di procedere

### Display modes & Button 2
- [ ] Button 2 mapping — follow `doit-s3-aibox.cc` pattern (`OnClick`/`OnDoubleClick`/`OnLongPress`)
- [ ] GIF standby screen — replace sleeping emoji with GIF from SD card
      (`gif_controller_` already in `LcdDisplay`, gifdec decoder available)
- [ ] Wallpaper/slideshow switch — build from scratch, no existing base
- [ ] SD card read test — verify real file read after mount

## 🔵 Future
- [ ] **esp-web-tools**: integrate browser-based flashing into the WebUI.
  Requires: `/manifest.json` endpoint in `server.py`, web component
  in `index.html`, verify offsets from partition table.
  Limitation: localhost only (not LAN) without HTTPS.
  Estimate: 2-3 hours.
- [ ] **Wake word**: change from "Nihao Xiaozhi" to a more suitable wake word
  (e.g. "Sophia" `CONFIG_SR_WN_WN9_SOPHIA_TTS=y`).
  Change: 1 line in `sdkconfig.defaults.esp32s3` + `rm sdkconfig` + rebuild.
- [ ] GitHub Actions: cloud build from WebUI → download compiled binaries
- [ ] Repo cleanup: remove unused original docs and sdkconfig.defaults for irrelevant targets (esp32, esp32c3, esp32c5, esp32c6, esp32p4)
