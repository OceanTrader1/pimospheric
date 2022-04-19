""" adv_reading.py """

import board
from adafruit_bme280 import basic as adafruit_bme280
from metpy.units import units
from metpy.calc import dewpoint_from_relative_humidity

def main():
    i2c = board.I2C()
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

    # Assign sea level pressure for altitude calculation
    bme280.sea_level_pressure = 1013.25 # Sea level pressure in millibars (Mb)

    # Assign variables
    temperature = bme280.temperature    # measured in celsius
    humidity = bme280.humidity          # measured in %, relative humidity
    pressure = bme280.pressure          # measured in hectopascals, hPa
    altitude = bme280.altitude          # measured in meters
    degree_symbol = "\u00b0"

    # Unit conversions
    temperature = [temperature] * units.degC
    pressure = [pressure] * units.hPa
    humidity = [humidity] * units.percent
    altitude = altitude * units.meters

    # calculations
    dewpoint = dewpoint_from_relative_humidity(
        temperature,
        humidity,
    )

    print(
        f"Temperature: {temperature.to('degF').m[0]:0.2f}{degree_symbol}F",
        f"Humidity: {humidity.m[0]:0.2f}%",
        f"Pressure: {pressure.to('mbar').m[0]:0.2f}mb",
        f"Altitude: {altitude:0.2f}",
        f"Dew Point: {dewpoint.to('degF').m[0]:0.2f}{degree_symbol}F",
        sep="\n"
    )

if __name__ == "__main__":
    main()

