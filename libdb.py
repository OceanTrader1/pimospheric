"""
libdb.py 

Library for database connection to weather sensor module/
"""

from os.path import exists as file_exists
from datetime import datetime
import sqlite3
from sqlite3 import Error 

from pandas import DataFrame, read_sql_query
from loguru import logger as log

log_filename = datetime.now().strftime("%D").replace("/","-")
log.add(f"pimospheric_{log_filename}.log", level="DEBUG", rotation="100 MB")
try:
    log.remove(0) # Comment to hide console output
except ValueError:
    log.debug("Handler already removed")

class Database():

    def __init__(self, db="db.sqlite3"):
        self.db = db
        self.conn = None
        self.table = "data"
        self.data = {
            "date": "",
            "temperature": 0,
            "humidity": 0,
            "pressure": 0,
            "altitude": 0,
            "dew_point": 0,
        }
        # If no database file exists, create the file
        # and the table headers for the database.
        if not file_exists(self.db):
            self.create_table()


    def __repr__(self):
        pass


    def __str__(self):
        pass


    def _connect(self) -> None:
        """
        Create connection to SQLite database. If no file exists, 
        create database file.

        Arguments:
            - db: str - Name of sqlite3 database
        
        Excepts:
            - Error: sqlite3.Error
        """
        file_created = False
        if not file_exists(self.db):
            log.debug(f'Filename "{self.db}" not found. File will be created.')
            file_created = True
        try:
            self.conn = sqlite3.connect(self.db)
            log.debug(f"sqlite version: {sqlite3.version}")
        except Error as err:
            log.debug(err)
        else:
            log.debug("Connection successful")
            if file_created:
                log.debug(f'Filename {self.db} created successfully.')


    def _create_table_stmt(self) -> str:
        """ Statement for creating TABLE in sqlite3"""
        statement = \
            f"CREATE TABLE {self.table}" \
            f"(date text, temperature int, humidity int, pressure int, " \
            f"altitude int, dew_point int)"

        return statement


    def _create_table(self) -> None:
        """ Create table in SQLite database. """
        if not self.conn:
            log.debug("No connection to database. Unable to create table.")
            return
        cur = self.conn.cursor()
        stmt = self._create_table_stmt()
        try:
            cur.execute(stmt)
            log.debug(f"Created table {self.table} successfully")
        except Error as err:
            log.debug(f"error: {err} - Unable to create table.")


    def _insert_stmt(self) -> str:
        """ Statement for inserting data in TABLE """
        values = ','.join([str(value) for key, value in self.data.items()])
        statement = \
            f"INSERT INTO {self.table}" \
            f"(date, temperature, humidity, pressure, altitude, dew_point) " \
            "VALUES('{}', {}, {}, {}, {}, {})".format(
                self.data["date"],
                self.data["temperature"],
                self.data["humidity"],
                self.data["pressure"],
                self.data["altitude"],
                self.data["dew_point"]
            )

        return statement


    def _insert(self):
        """ Insert data into table"""
        try:
            stmt = self._insert_stmt()
            self.conn.execute(stmt)
            log.debug(f"Inserted into table {self.table}")
            log.debug("{}".format(
                ', '.join(str(key) + ': ' + str(value) \
                    for key, value in self.data.items())
                )
            )
        except Error as err:
            log.debug(f"error: {err}: Unable to insert data.")
            log.debug(f"Offending statement: {stmt}")


    def _close(self):
        """ Close connection """
        if self.conn:
            try:
                self.conn.close()
            except Error as err:
                log.debug("Unable to close connection")
            else:
                log.debug("Connection closed successfully")
        else:
            log.debug("Error. No connection.")

    def _commit(self):
        if not self.conn:
            log.debug("No connection. Unable to commit.")
            return
        
        try:
            self.conn.commit()
        except Error as err:
            log.debug("error: {err}\nUnable to commit")


    def _read(self):
        try:
            with sqlite3.connect(self.db) as db:
                data = read_sql_query(f"SELECT * from {self.table}", db)
                log.debug(f"Read data from table")
        except Error as err:
            log.debug("Unable to read from table")
        return data

    def connect(self) -> None:
        """ Create connection to SQLite database. """
        self._connect()


    def close(self) -> None:
        """ Close connection to SQLite database. """
        self._close()


    def commit(self) -> None:
        self._commit()


    def create_table(self) -> None:
        """ Create table in SQLite database. """
        self.connect()
        self._create_table()
        self.close()


    def insert(self, *,
        date, temperature, humidity, 
        pressure, altitude, dew_point) -> None:
        """ Insert data into TABLE 
        
        Arguments:
            - date: str - datetime.datetime.isoformat
            - temperature: int
            - humidity: int
            - pressure: int
            - altitude: int
            - dew_point: int

        """
        self.connect()

        # Assign data
        self.data["date"] = date
        self.data["temperature"] = temperature
        self.data["humidity"] = humidity
        self.data["pressure"] = pressure
        self.data["altitude"] = altitude
        self.data["dew_point"] = dew_point
        # Insert data
        self._insert()
        # Save to database
        self.commit()
        self.close()
    
    def read(self) -> DataFrame:
        """
        Reads data from database file and returns
        as a pandas DataFrame class
        
        Returns:
            - pandas.DataFrame
        """

        return DataFrame(data=self._read())
