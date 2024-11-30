# About

This project manages a dew heater for a Raspberry Pi based AllSky camera.

A systemd timer based Python script fetches the current weather information from openeathermap.org, calculates the
[dew and frost](https://gist.github.com/sourceperl/45587ea99ff123745428) point, and then turns a heater on or off.

This project is [MIT licensed](LICENSE).

# Hardware Setup

The hardware setup is similar to [hdiessner/Allskycam-heating](https://github.com/hdiessner/Allskycam-heating).

# Installation

1. Copy the `allsky-heater.service` and `allsky-heater.timer` from the [systemd](./systemd) directory to
   `/etc/systemd/system`:

   ```bash
   sudo cp ./systemd/* /etc/systemd/system
   ```

1. Copy the main program into a bin directory:

   ```bash
   sudo cp allsky-heater.py /usr/local/bin
   ```

1. Reload the systemd config and enable the timer:
   
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable allsky-heater.timer
   ```
