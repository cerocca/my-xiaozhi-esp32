# Setup — my-xiaozhi-esp32

Complete installation guide from scratch on macOS.

---

## 1. Prerequisites

Before starting, make sure you have the following:

**Git**
```bash
git --version
# If not installed: xcode-select --install
```

**Python 3**
```bash
python3 --version
# Must be 3.9 or later. Do NOT use `python` (points to Python 2 on macOS).
```

**USB drivers** — needed to communicate with the ESP32-S3 board over USB serial.
Install the one matching your board's USB chip (check the board or try both):
- **CP210x** (Silicon Labs): https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- **CH340** (WCH): https://www.wch-ic.com/downloads/CH341SER_MAC_ZIP.html

After installing, reboot your Mac before proceeding.

**Flask** (required for the WebUI only — skip if you only use the CLI):
```bash
pip3 install flask
```

---

## 2. Install ESP-IDF 5.5.2

ESP-IDF is the Espressif IoT Development Framework. Version 5.5.2 or later is required.

```bash
mkdir -p ~/esp
cd ~/esp
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
git checkout v5.5.2
git submodule update --init --recursive
./install.sh esp32s3
```

> **Note**: the `./install.sh esp32s3` step downloads the compiler toolchain and takes several minutes. Make sure you have a stable internet connection.

To verify the installation:
```bash
source ~/esp/esp-idf/export.sh
idf.py --version
# Should print: ESP-IDF v5.5.2
```

> **Important**: `source ~/esp/esp-idf/export.sh` must be run in **every new terminal session** before using `idf.py`. It is not permanent.

---

## 3. Clone this repo

```bash
git clone https://github.com/cerocca/my-xiaozhi-esp32.git
cd my-xiaozhi-esp32
```

---

## 4. First build

```bash
source ~/esp/esp-idf/export.sh
idf.py set-target esp32s3
python3 scripts/build_firmware.py --mode hardcoded
```

What this does:
- `idf.py set-target esp32s3` — configures the build system for the ESP32-S3 chip (required once per clean build directory)
- `python3 scripts/build_firmware.py --mode hardcoded` — builds the firmware with the custom server URL compiled in

The compiled firmware will be at `build/xiaozhi.bin`.

> **Tip**: if you get `idf.py: command not found`, you forgot to run `source ~/esp/esp-idf/export.sh` first.

---

## 5. Flash

Connect the board via USB, then find the serial port:
```bash
ls /dev/cu.*
```

With the board disconnected and then reconnected, note which new entry appears (typically `/dev/cu.usbserial-XXXX` or `/dev/cu.SLAB_USBtoUART`).

Flash the firmware:
```bash
idf.py -p /dev/cu.usbserial-XXXX flash
```

Replace `/dev/cu.usbserial-XXXX` with your actual port.

To flash and monitor output at the same time:
```bash
idf.py -p /dev/cu.usbserial-XXXX flash monitor
```

Press `Ctrl+]` to exit the monitor.

---

## 6. WebUI (alternative to CLI)

If you prefer a browser interface for building and downloading firmware, see:

**[webui/SETUP.md](webui/SETUP.md)**

The WebUI runs locally at `http://localhost:5001` and provides the same build options as the CLI, with live streaming output and one-click binary downloads.

---

## 7. First boot

On first power-on (or after flashing), the device has no WiFi credentials and enters **AP (Access Point) mode**:

1. On your Mac, connect to the WiFi network named `Xiaozhi-XXXX` (no password)
2. A captive portal should open automatically, or navigate to `http://192.168.4.1`
3. Select your home WiFi network and enter the password
4. Open the **Advanced** tab and set the OTA URL to your custom server (e.g. `http://YOUR_SERVER_IP:8003/xiaozhi/ota/`)
5. Save — the device will reboot and connect to your WiFi and your custom server

> **Note**: the OTA URL in the Advanced tab is saved to NVS and overrides the compiled-in default. If you built with `--mode hardcoded`, you can leave this field empty and the custom server URL is already in the firmware.
