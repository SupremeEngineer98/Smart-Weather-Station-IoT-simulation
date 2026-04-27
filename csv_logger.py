# This module is responsible for persisting sensor data received via MQTT
# to a local csv file!
# It's subscribing to the 'sensors/data' topic on the
# shared broker and writes each incoming message as a timestamped row!
#
# csv file format:
#   timestamp, ldr, uv, temperature, humidity, pressure, gas_resistance!
#
# features:
#   1. Automatic header creation on first write!
#   2. Thread-safe file access using threading.Lock() to prevent data!
#     corruption when multiple threads attempt simultaneous writes!
#   3. Human-readable timestamps (dd Month YYYY - HH:MM:SS)!
#   4. Mirrors the behaviour of a data logging node on a real ESP32!
#
# In a real hardware's system this logic would run on ESP32 Device B,
# receiving MQTT messages over Wi-Fi and writing to onboard flash storage!
import csv
import os 
import time
from datetime import datetime
from mqtt_broker import MQTTBroker#importing the mocked class mqttbroker. the mqtt_broker's file is inside the folder!
import threading 


from sensors import Sensor#importing the mocked Sensor class!

#creating the class which will be responsible to log data into the csv file!
class CSVLogger:

    # MQTT-driven CSV data logger!
    # Subscribing to the 'sensors/data' MQTT topic upon initialisation and
    # automatically writing each received sensor payload as a timestamped row
    # to the specified csv file!

    # Thread safety is enforced via a threading.Lock(), ensuring that
    # concurrent write attempts from multiple threads do not corrupt the file!

    # Attributes:
    #   1. filename (str): Path to the output CSV file!
    #   2. broker (MQTTBroker): Reference to the shared broker instance!
    #   3. lock (threading.Lock): Mutex used to serialise file write operations!

    def __init__(self, broker, filename="sensor_data.csv"):

        # Initialising the CSVLogger and registering the logging callback!
        # Storing the broker reference and output filename, creating the
        # threading lock, and immediately subscribing to 'sensors/data' so
        # that logging begins as soon as the first message is published!

        # Args:
        #   1. broker (MQTTBroker): The shared broker instance to subscribe to!
        #   2. filename (str): Output CSV file path. Defaults to 'sensor_data.csv'!

        self.filename = filename
        self.broker = broker

        # threading.Lock() ensures only one thread writes to the file at a time,
        # preventing race conditions and potential data corruption!
        self.lock = threading.Lock()

        # subscribing to the topic - log_to_csv will be called automatically
        # by the broker each time a message is published!
        self.broker.subscribe("sensors/data", self.log_to_csv)

    def log_to_csv(self, topic, message):

        # Callback invoked automatically by the broker on each published message!
        # Appending a single timestamped row to the csv file in a thread-safe manner!
        # If the file does not yet exist, writes the header row first
        # to ensure a correctly formatted CSV output!

        # Args:
        #   topic (str): The MQTT topic the message was published to!
        #   message (dict): Sensor payload containing keys: ldr, uv,
        #                   temperature, humidity, pressure, gas_resistance!

        # acquiring the lock before ALL file operations - both the existence check
        # AND the file write must happen inside the same lock to guarantee
        # thread safety and prevent the "I/O operation on closed file" error!
        with self.lock:

            # checking inside the lock whether the file already exists,
            # so the header is only written once on initial file creation!
            file_exists = os.path.isfile(self.filename)

            # opening the file in append mode INSIDE the lock to keep all
            # file operations atomic - open, write and close happen together!
            with open(self.filename, mode="a", newline="") as file:

                fieldnames = [
                    "timestamp",
                    "ldr",
                    "uv",
                    "temperature",
                    "humidity",
                    "pressure",
                    "gas_resistance"
                ]

                # using DictWriter for structured, named-column csv output!
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                # writing header only when creating the file for the first time!
                if not file_exists:
                    writer.writeheader()

                # building the row with a human-readable timestamp and values from all sensors
                # using .get() to safely handle any missing keys in the payload!
                row = {
                    "timestamp": datetime.now().strftime("%d %B %Y - %H:%M:%S"),
                    "ldr": message.get("ldr"),
                    "uv": message.get("uv"),
                    "temperature": message.get("temperature"),
                    "humidity": message.get("humidity"),
                    "pressure": message.get("pressure"),
                    "gas_resistance": message.get("gas_resistance")
                }

                # writing the completed row to the CSV file!
                writer.writerow(row)

        print(f"[CSVLogger] Data saved to '{self.filename}'")


# Standalone test - runs only when this file is executed directly!
# Publishes 5 simulated sensor readings and verifies CSV output!
if __name__ == "__main__":

    broker = MQTTBroker()
    logger = CSVLogger(broker)
    sensor = Sensor()

    print("Running standalone CSV logger test (5 readings)...")
    for _ in range(5):
        data = sensor.read_all_sensors()
        # publishing with QoS 1 to guarantee at-least-once delivery!
        broker.publish("sensors/data", data, qos=1)
        time.sleep(1)

    



