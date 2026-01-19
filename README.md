DigitalSTROM VDC Home Assistant integration

Installation (developer):

1. Copy the `custom_components/digitalstrom_vdc` folder into your Home Assistant `config/custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via Settings → Devices & Services → Add Integration → `DigitalSTROM VDC` and enter the TCP port to listen on.

Note: the integration always binds to the Home Assistant host (localhost / 127.0.0.1); you only need to provide the port.

Development notes:
- This repository contains a minimal scaffold: `manifest.json`, `config_flow.py`, `sensor.py` and core files.
- Implement actual device communication inside `sensor.py` (or other platforms).
