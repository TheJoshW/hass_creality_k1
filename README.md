# Home Assistant Creality K1 / K1 Max Integration

This is a custom component for [Home Assistant](https://www.home-assistant.io/) to integrate with Creality K1 Max 3D printers. It communicates directly with the printer over your local network using its WebSocket API (port 9999), providing sensors and controls without relying on the Creality Cloud.

## Features

* **Real-time Monitoring:**
    * Printer State (Printing, Idle, Paused, Complete, Failed, etc.)
    * Nozzle Temperature (Current & Target)
    * Heated Bed Temperature (Current & Target)
    * Chamber Temperature (if reported by the printer)
    * Print Progress (%)
    * Print Job Time / Remaining Time
    * Current Layer / Total Layers
    * Fan Speeds (%)
    * LED Light Status
    * And can add other sensors exposed by the WebSocket API.
* **Controls:**
    * Turn LED Light On/Off.
    * Control Fan Speeds (Model Fan, Case/Back Fan, Side/Auxiliary Fan) via percentage. (Uses `M106` GCODE commands).
* **Local Control:** Communicates directly via the local network WebSocket.

## Requirements

* Home Assistant instance.
* Creality K1 or K1 Max printer connected to your local network.
* Network connectivity between your Home Assistant instance and the printer.
* The IP address of your printer.

## Installation

### Method 1: Manual Installation

1.  **Download the Code:** Download the `custom_components/creality_k1` folder from this repository (e.g., download the ZIP and extract it, or use git clone). Make sure you have the folder containing `__init__.py`, `manifest.json`, `sensor.py`, `switch.py`, `fan.py`, etc.
2.  **Copy to Home Assistant:**
    * Connect to your Home Assistant configuration directory (often via Samba, SSH, or the File editor add-on).
    * Navigate to the `custom_components` folder. If it doesn't exist, create it.
    * Copy the entire `custom_components/creality_k1` folder (the one you downloaded/cloned) into the `custom_components` directory.
    * Your final path should look like `config/custom_component/creality_k1/`.
3.  **Restart Home Assistant:** Restart your Home Assistant instance. (Settings > System > Restart).

## Configuration

Once installed and after restarting Home Assistant:

1.  Go to **Settings** > **Devices & Services**.
2.  Click the **+ Add Integration** button in the bottom right corner.
3.  Search for "**Creality K1**".
4.  Select the integration.
5.  You will be prompted to enter the **IP Address** of your Creality K1 / K1 Max printer.
6.  Click **Submit**.

The integration will attempt to connect to your printer via WebSocket. If successful, it will add the device and its associated entities to Home Assistant.

## Entities Provided

This integration creates several entities, typically prefixed with the name you gave the device during setup (e.g., `fan.k1_model_fan`). Key entities include:

* **Fans (`fan.`):**
    * Model Fan (with percentage control)
    * Case Fan (with percentage control)
    * Side Fan (with percentage control)
* **Switch (`switch.`):**
    * LED Light
* **Sensors (`sensor.`):**
    * Printer Status (e.g., Idle, Printing, Paused)
    * Nozzle Temperature
    * Nozzle Target Temperature
    * Bed Temperature
    * Bed Target Temperature
    * Chamber/Box Temperature (if available)
    * Print Progress
    * Print Job Time
    * Print Remaining Time
    * Current Layer
    * Total Layers
    * ... and can add potentially others depending on printer reports.

## Troubleshooting / Notes

* **Connection Issues:** Ensure your printer is powered on, connected to the network, and that the IP address entered during configuration is correct. Check for firewall rules blocking traffic between Home Assistant and the printer (specifically WebSocket traffic on port 9999).
* **Fan Control:** Fan percentage is controlled by sending `M106 P<index> S<0-255>` GCODE commands via the WebSocket. `Pct` values reported by the printer reflect status but are not used for direct control.
* **Firmware Differences:** Printer behavior and available data might vary slightly depending on the firmware version installed on your K1 / K1 Max.

## Disclaimer

This is a custom integration and is not officially supported by Home Assistant or Creality. Use at your own risk.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/hurricaneb/hass_creality_k1).

## License

GPL-3.0 license