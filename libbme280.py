"""
libbme280.py 

Continuously takes the measurements/readings of
temperature, pressure, humidity, altitude, and dewpoint (by calculation)
and records the information in a database. 

Recording interval is set to take measurements every (5) second(s).
"""

import time
from datetime import datetime

import board
from adafruit_bme280 import basic as adafruit_bme280
from metpy.units import units
from metpy.calc import dewpoint_from_relative_humidity

from libdb import Database

class BME280SENSOR():
    
    def __init__(self):
        self.i2c = board.I2C()
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
        self.database = Database()
        self.set_sea_level_pressure(1013.25)
        self.temperature = None     # measured in celsius
        self.humidity = None        # measured in %, relative humidity
        self.pressure = None        # measured in hectopascals, hPa
        self.altitude = None        # measured in meters
        self.time = None            # in ISOFORMAT
        self.degree_symbol = "\u00b0"
        

    def _read(self):
        """ Collect readings from bme280 sensors"""
        self.temperature = self.bme280.temperature
        self.humidity = self.bme280.humidity
        self.pressure = self.bme280.pressure
        self.altitude = self.bme280.altitude

        # Unit conversions
        self.temperature = [self.temperature] * units.degC
        self.pressure = [self.pressure] * units.hPa
        self.humidity = [self.humidity] * units.percent
        self.altitude = self.altitude * units.meters

        # calculations
        self.dewpoint = dewpoint_from_relative_humidity(
            self.temperature,
            self.humidity,
        )

        # time
        self.time = datetime.now().isoformat()


    def _write(self):
        """ Write data collected to database """
        self.database.insert(
                date=self.time,
                temperature=self.temperature.m[0],
                humidity=self.humidity.m[0],
                pressure=self.pressure.to('mbar').m[0],
                altitude=self.altitude.m,
                dew_point=self.dewpoint.m[0]
            )

    def update(self):
        self._read()    # collect sensor data then
        self._write()   # write to database


    def show_data(self):
        """ A nice to have service to print the data to console.
        Useful for debugging """
        print(
            f"Time:\t{self.time}"
            f"Temperature:\t{self.temperature.to('degF').m[0]:0.2f}{self.degree_symbol}F",
            f"Humidity:\t{self.humidity.m[0]:0.2f}%",
            f"Pressure:\t{self.pressure.to('mbar').m[0]:0.2f}mb",
            f"Altitude:\t{self.altitude.m:0.2f} meters",
            f"Dew Point:\t{self.dewpoint.to('degF').m[0]:0.2f}{self.degree_symbol}F",
            sep="\n"
        )


    def set_sea_level_pressure(self, pressure):
        """ Assign sea level pressure for altitude calculation.
        
        Arguments:
            - pressure: int  Sea level pressure in hectopascals (hPa)
        """
        self.bme280.sea_level_pressure = pressure

