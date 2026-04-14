# TODO — my-xiaozhi-esp32

## 🔧 Ongoing — Hardware
(analysis and future implementation only, no immediate action)

- [ ] Volume: add handler in the board file (`sp-esp32-s3-1.28-box.cc`). Pattern: `main/boards/magiclick-2p5/magiclick_2p5_board.cc`

## 🔵 Future
- [ ] **IoT Tools**: the LLM responds verbally without invoking MCP tools
  (volume, brightness, and any other tool).
  Cause: server-side issue — the device correctly exposes tools via MCP
  (confirmed by logs: `tools/list` received, `GetToolsList` sends 11 tools
  including `self.audio_speaker.set_volume`) but the LLM does not invoke them.
  `DoToolCall` never called → fix in progress on the server side.
- [ ] **esp-web-tools**: integrate browser-based flashing into the WebUI.
  Requires: `/manifest.json` endpoint in `server.py`, web component
  in `index.html`, verify offsets from partition table.
  Limitation: localhost only (not LAN) without HTTPS.
  Estimate: 2-3 hours.
- [ ] **Wake word**: change from "Nihao Xiaozhi" to a more suitable wake word
  (e.g. "Sophia" `CONFIG_SR_WN_WN9_SOPHIA_TTS=y`).
  Change: 1 line in `sdkconfig.defaults.esp32s3` + `rm sdkconfig` + rebuild.
- [ ] **IoT Things**: `InitializeIot()` with `CreateThing("Speaker")` and
  `CreateThing("Screen")` in `sp-esp32-s3-1.28-box.cc`
- [ ] GitHub Actions: cloud build from WebUI → download compiled binaries
- [ ] Repo cleanup: remove unused original docs and sdkconfig.defaults for irrelevant targets (esp32, esp32c3, esp32c5, esp32c6, esp32p4)
