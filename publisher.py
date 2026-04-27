# This module simulates the first ESP32 device in the IoT architecture!
# Were I using a real hardware setup, this would run as the main script on a physical!
# ESP32 connected to the following sensors:
#   - LDR: light intensity measurement!
#   - VEML6070: UV radiation measurement!
#   - BME680: temperature, humidity, atmospheric pressure and gas resistance!
#
# Responsibilities:
#   1. Establish a simulated Wi-Fi connection before any data transmission!
#   2. Read all sensor values every  second via Sensor.read_all_sensors()!
#   3. Publish each reading to the shared MQTT broker on topic 'sensors/data'!
#      using QoS 1 to guarantee at-least-once message delivery!
#   4. Monitor Wi-Fi connectivity before each publish and skip if disconnected!
#   5. Handle sensor read errors gracefully without crashing the main loop!
#
# Data flow:
#   Sensor --> read_all_sensors() --> shared_broker.publish() --> Subscriber!!


#importing all the required modules!
import time
import logging
from sensors import Sensor #sensor's library is a custom made library I developed in order to simulate sensor's functionality. It's located inside the folder!
from wifi_connection import Wifi #wifi_connection's library is a custom made library I developed in order to simulate connection into a wifi. It's located inside the folder!
from broker import shared_broker #broker library is a simulated library which is located inside the folder!

#configuring logging to display timestamped messages at INFO level and above!

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_publisher():
    
   #Entry point for the publisher thread!

   #Simulating the main loop of ESP32 Device A. First establishing a Wi-Fi
   #connection by scanning for and joining the first available open network.
   #If  connection fails, the publisher will immediately exit to prevent
   #publishing to a broker without network access!

    #Upon successful connection,  an infinite loop starts that:
      #- reads all sensor values every 1 second!
      #- verifies Wi-Fi connectivity before each publish!
      #- publishes the payload to 'sensors/data' with QoS 1!
      #- handles sensor read exceptions without terminating the loop!

    #This function is designed to be launched as a daemon thread from main.py!
    #In real hardware environment this would correspond to the MicroPython main loop on
    #a physical ESP32 board!
    

    #Wi-Fi Connection!
    # scanning for available networks and connecting to the first open access point,
    # mirroring the auto-join behaviour of a real ESP32 in an unknown environment!

    wifi = Wifi()
    wifi.connect_first_open()
    
     #aborting if Wi-Fi connection was not established,
     #as publishing without connectivity would silently fail!
    if not wifi.is_connected():
        logging.error("Publisher: WiFi connection failed. Exiting.")
        return


    
    #Sensor Initialisation Phase
    # instantiating the Sensor object which sets the simulation start time
    # used as the reference for the daily sine wave cycle!
    sensor = Sensor()
    logging.info("Publisher started. Reading sensors every 1 second...")

 #Main Publishing Loop!
    try:
        while True:
            
             # reading all sensor values from the simulated sensors
             # wrapped in try/except to handle unexpected read failures
             # without terminating the entire publisher thread!
            try:
                data = sensor.read_all_sensors()
            except Exception as e:
                logging.error(f"Publisher: Sensor read failed: {e}")
                continue #skiping this iteration and it will retry again next second!

            #only publish if wifi is still connected!
            # using QoS 1 to ensure at-least-once delivery to the broker!
            if wifi.is_connected():
                # publishing with QoS 1 to ensure at-least-once delivery,
                # the broker will retry up to 3 times if delivery fail!
                shared_broker.publish("sensors/data", data, qos=1)
            else:
                logging.warning("Publisher: WiFi lost. Skipping publish.")

            time.sleep(1)# 1 second interval to satisfy assignment's requirements!

    except KeyboardInterrupt:
        logging.info("Publisher stopped.")