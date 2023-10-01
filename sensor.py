import time
import board
import adafruit_dht

class SensorReadException(Exception):
    pass

class ClimateSensor:

    def __init__(self):
        # Initial the dht device, with data pin connected to:
        self._dhtDevice = adafruit_dht.DHT22(board.D4)

    def read(self):
        tries = 0
        while tries < 10:
            tries = tries + 1
            try:
                # Print the values to the serial port
                temperature_c = self._dhtDevice.temperature
                #temperature_f = temperature_c * (9 / 5) + 32
                humidity = self._dhtDevice.humidity

                return (temperature_c, humidity)

            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                time.sleep(2.0)

            except Exception as error:
                self._dhtDevice.exit()
                raise error

        raise SensorReadException(f'Unable to read sensor after {tries} tries')


if __name__ == '__main__':
    sensor = ClimateSensor()
    temperature, humidity = sensor.read()
    print(f'Temperature={temperature}C,  Humidity={humidity}%')
