"""
Fetch weather information from web and turn on/off AllSky dew heater
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import http.client
import json
import math

import RPi.GPIO as GPIO

CONFIG = configparser.ConfigParser()
CONFIG.read('/etc/allsky-heater.conf')


def kelvin_to_celsius(kelvin: float) -> float:
    """
    convert degrees Kelvin to Celsius

    param: 
    """
    return kelvin - 273.15

def get_frost_point_c(t_air_c: float, dew_point_c: float) -> float:
    """
    Compute the frost point in degrees Celsius

    :param t_air_c: current ambient temperature in degrees Celsius
    :param dew_point_c: current dew point in degrees Celsius
    :return: the frost point in degrees Celsius 
    """
    dew_point_k = 273.15 + dew_point_c
    t_air_k = 273.15 + t_air_c
    frost_point_k = dew_point_k - t_air_k + 2671.02 / (
        (2954.61 / t_air_k) + 2.193665 * math.log(t_air_k) - 13.3448
    )
    return frost_point_k - 273.15


def get_dew_point_c(t_air_c: float, rel_humidity: float) -> float:
    """
    Compute the dew point in degrees Celsius

    :param t_air_c: current ambient temperature in degrees Celsius
    :param rel_humidity: relative humidity in %
    :return: the dew point in degrees Celsius
    """
    A = 17.27
    B = 237.7
    alpha = ((A * t_air_c) / (B + t_air_c)) + math.log(rel_humidity/100.0)
    return (B * alpha) / (A - alpha)

def fetch_weather_info(latitude: float, longitude: float, api_key: str) -> dict:
    """
    Fetch current weather information for a location

    param latitude: AllSky camera location latitude
    param longitude: AllSky camera location longitude
    param api_key: openweathermap.org API key
    return: openweathermap.org data
    """
    try:
        conn = http.client.HTTPSConnection("api.openweathermap.org")
        conn.request("GET", f"/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}")
        response = conn.getresponse()

        if response.status == 200:
            data = response.read().decode("utf-8")
            json_data = json.loads(data)  # Parse the JSON data
            return json_data
        print(f"Error: could not fetch weather info {response.status} {response.reason}")
    finally:
        conn.close()
    return None

def get_temp_and_humidity(latitude: float, longitude: float, api_key: str) -> tuple[float, float]:
    """
    Get the current temperature and relative humidity

    param latitude: AllSky camera location latitude
    param longitude: AllSky camera location longitude
    param api_key: openweathermap.org API key
    return: current Celsius temperature and relative humidity
    """
    data = fetch_weather_info(latitude, longitude, api_key)
    return kelvin_to_celsius(data["main"]["temp"]), data["main"]["humidity"]

def switch_heater(pin: int, state: bool) -> None:
    """
    Set GPIO pin of Raspberry Pi to high or low

    param pin: GPIO pin number that is connected to the relais
    param state: true turns heater on, false turns heater off
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, state)

def calculate_heater_state(temp_celsius, rel_humidity, temp_margin) -> bool:
    """
    Calculate if the heater should be turned off or on based on current temperature and humidity

    param temp_celsius: current temperature in degrees Celsius
    param rel_humidity: current relative humidity
    param temp_margin: margin above current temperature which should turn on the heater
    return: state of heater
    """
    dew_point = get_dew_point_c(temp_celsius, rel_humidity)
    frost_point = get_frost_point_c(temp_celsius, dew_point)

    if temp_celsius - temp_margin < dew_point or temp_celsius - temp_margin < frost_point:
        return True
    return False

def __main__(latitude: float, longitude: float, api_key: str, pin: int, temp_margin: float):
    """
    main program loop
    """
    temp_celsius, rel_humidity = get_temp_and_humidity(latitude, longitude, api_key)
    heater_state = calculate_heater_state(temp_celsius, rel_humidity, temp_margin)
    switch_heater(pin, heater_state)

__main__(
    float(CONFIG["DEFAULT"]["LATITUDE"]),
    float(CONFIG["DEFAULT"]["LONGITUDE"]),
    CONFIG["DEFAULT"]["OPENWEATHERMAP_API_KEY"],
    CONFIG["DEFAULT"]["RELAIS_PIN"],
    CONFIG["DEFAULT"]["TEMP_MARGIN"]
)