# TODO — my-xiaozhi-esp32

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
