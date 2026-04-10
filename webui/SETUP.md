# Setup — webui Firmware Builder

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python 3 | 3.9+ | `python3 --version` |
| Flask | any recent | `pip3 install flask` |
| ESP-IDF | 5.5.2+ | must be activated in the same shell |

## First-time install

```bash
pip3 install flask
```

No other Python dependencies are required.

## Starting the server

Open a terminal in the project root, activate ESP-IDF, then launch the server:

```bash
source ~/esp/esp-idf/export.sh
python3 webui/server.py
```

The server listens on `http://localhost:5000` (or `http://<your-ip>:5000` from
another machine on the same network).

## Build flow

1. Open `http://localhost:5000` in a browser
2. Choose **Hardcoded** or **Dynamic** mode
3. If Hardcoded: verify or change the OTA URL (default: `http://192.168.1.69:8003/xiaozhi/ota/`)
4. Select language (default: Italian)
5. Click **Build Firmware**
6. Build output streams live in the console area
7. When done, download links appear for:
   - `xiaozhi.bin` — main application firmware
   - `bootloader.bin` — bootloader
   - `partition-table.bin` — partition table
   - `ota_data_initial.bin` — OTA data partition

## Flashing (manual, after download)

```bash
source ~/esp/esp-idf/export.sh
idf.py -p /dev/cu.usbserial-XXXX flash
# or flash specific binaries:
esptool.py --port /dev/cu.usbserial-XXXX write_flash \
  0x0     bootloader.bin \
  0x8000  partition-table.bin \
  0xd000  ota_data_initial.bin \
  0x10000 xiaozhi.bin
```

## Notes

- Only one build can run at a time. A second request while building returns HTTP 409.
- The server writes a temporary `sdkconfig.defaults.build_override` in the project
  root during the build and removes it when done (or on error).
- If `idf.py` is not in PATH the build will fail immediately with a clear error in
  the browser console — re-activate ESP-IDF and reload the page.
