from sensor import ClimateSensor, SensorReadException
from database import create_climate_data, Database
import time, datetime

def main():
    sensor = ClimateSensor()
    db = Database('db.sqlite')

    while True:

        try:
            temperature, humidity = sensor.read()
            print(f'Read sensor {(temperature, humidity)} {datetime.datetime.now()}')
            data = create_climate_data(temperature, humidity)
            db.write(data)

            time.sleep(10 * 60)
        except SensorReadException:
            # ignore and try again later
            print(f'Failed to read sensor {datetime.datetime.now()}')
            time.sleep(60)


if __name__ == '__main__':
    main()
