""" basic_reading.py """

import board
from adafruit_bme280 import basic as adafruit_bme280

def main():
    i2c = board.I2C()
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)

if __name__ == "__main__":
    main()
