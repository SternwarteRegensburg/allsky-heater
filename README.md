# About

This project manages a dew heater for a Raspberry Pi based AllSky camera.

A systemd timer based Python script fetches the current weather information from openeathermap.org, calculates the
[dew and frost](https://gist.github.com/sourceperl/45587ea99ff123745428) point, and then turns a heater on or off.

You need to register an account at [https://openweathermap.org](https://home.openweathermap.org/users/sign_up) and
retrieve an [API key](https://home.openweathermap.org/api_keys).

This project is [MIT licensed](LICENSE).

# Hardware Setup

The hardware setup is similar to [hdiessner/Allskycam-heating](https://github.com/hdiessner/Allskycam-heating).

# Installation

1. Install the `python-rpi.gpio` package:

   ```bash
   sudo apt install python-rpi.gpio
   ```

1. Clone this repository and cd into the new directory:
   
   ```bash
   git clone https://github.com/SternwarteRegensburg/allsky-heater.git
   cd allsky-heater
   ```

1. Copy the `allsky-heater.service` and `allsky-heater.timer` from the [systemd](./systemd) directory to
   `/etc/systemd/system`:

   ```bash
   sudo cp ./systemd/* /etc/systemd/system
   ```

1. Copy the main program into a bin directory:

   ```bash
   sudo cp allsky-heater.py /usr/local/bin
   ```

1. Copy the config file to `/etc/`, then adjust the settings to your needs. You need to enter your API key.
   
   ```bash
   sudo cp allsky-heater.conf /etc/
   sudo nano /etc/allsky-heater.conf
   ```

1. Reload the systemd config and enable the timer:
   
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable allsky-heater.timer
   sudo systemctl start allsky-heater.timer
   ```
