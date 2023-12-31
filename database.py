from collections import namedtuple
import sqlite3
import unittest
import os
import tempfile
from datetime import datetime
import pprint


def parse_datetime(text):
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
    ]

    for date_format in formats:
        try:
            return datetime.strptime(text, date_format)
        except ValueError:
            pass

    raise ValueError(f"Could not parse the input string '{text}' into a datetime.")


ClimateData = namedtuple('ClimateData', ['temperature', 'humidity', 'timestamp'])


def create_climate_data(temperature: float, humidity: float, timestamp=None):
    if isinstance(timestamp, str):
        timestamp = parse_datetime(timestamp)
    elif not isinstance(timestamp, (datetime, type(None))):
        raise ValueError(f"Unsupported type for timestamp: {type(timestamp)}")

    return ClimateData(temperature=temperature, humidity=humidity, timestamp=timestamp)


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._tablename = 'climate'
        self._create_table()

    def __del__(self):
        self.conn.close()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self._tablename} (
                timestamp DATETIME,
                temperature FLOAT,
                humidity FLOAT
            )
        ''')

    def write(self, data: ClimateData):

        timestamp = data.timestamp or datetime.now()

        cursor = self.conn.cursor()
        cursor.execute(f'''
            INSERT INTO {self._tablename} (temperature, humidity, timestamp)
            VALUES (?, ?, ?)
        ''', (data.temperature, data.humidity, timestamp))
        self.conn.commit()

    def read(self, start=None, end=None):
        cursor = self.conn.cursor()
        if start and end:
            cursor.execute(f'''
                SELECT temperature, humidity, timestamp
                FROM {self._tablename}
                WHERE timestamp BETWEEN ? AND ?
            ''', (start, end))
        else:
            cursor.execute(f'''
                SELECT temperature, humidity, timestamp
                FROM {self._tablename}
            ''')

        rows = cursor.fetchall()
        return [create_climate_data(*row) for row in rows]


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary SQLite database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = Database(self.db_path)

    def tearDown(self):
        # Close and remove the temporary SQLite database
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_write_and_read(self):
        # Sample data
        data1 = create_climate_data(25.0, 50.0, datetime(2023, 9, 29, 10, 0))
        data2 = create_climate_data(26.0, 55.0, datetime(2023, 9, 29, 11, 0))

        # Write data to the database
        self.db.write(data1)
        self.db.write(data2)

        # Read the data
        result = self.db.read()
        pprint.pprint(result)

        # Ensure the data matches what was written
        self.assertEqual(result[0], data1)
        self.assertEqual(result[1], data2)

