#Simulating the second ESP32 device (subscriber node)!
#This logic simulates the second ESP32 device in the Smart Weather Station Prototype!.
#In a real hardware setup, this would run on a physical ESP32 that:
# 1. connects to the same Wi-Fi network as the publisher!
# 2. subscribes to the MQTT broker topic 'sensors/data'!
# 3. receives incoming sensor payloads and persists them to local storage!

# In this simulation, the subscriber shares the same in-process broker!
# object (broker.py) with the publisher, eliminating the need for a real!
# network connection while preserving the publish/subscribe architecture!
#
# Here's the follow data flow:
# Publisher (Thread 1) --> shared_broker --> Subscriber (Thread 2) --> sensor_data.csv!

import logging
from csv_logger import CSVLogger #csv_logger is a custom made library I developed in order to log the collected data into the csv file!
from broker import shared_broker  #broker library is a simulated library which is located inside the folder!

#configuring logging to display timestamped messages at INFO level and above!

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_subscriber():
    #entry point for subscirber's thread!

    #Instantiating a CSVLogger object which, upon initialisation, automatically
    #subscribes to the 'sensors/data' MQTT topic on the shared broker.
    #Once subscribed, every message published by the publisher triggers the
    #SVLogger.log_to_csv() callback, which appends the data to sensor_data.csv!

    #This function is designed to be launched as a daemon thread from main.py
    #and runs indefinitely, waiting for incoming MQTT messages!

    
    #In a real hardware this would correspond to the MicroPython main loop on
    #ESP32 Device B, listening on the MQTT topic over Wi-Fi!
    
   
    #instantiating CSVLogger - subscription to 'sensors/data' happens automatically
    # inside CSVLogger.__init__(), so no explicit subscribe call is needed here!
    csv_logger = CSVLogger(shared_broker, filename="sensor_data.csv")

    logging.info("Subscriber has just started. Logging data to 'sensor_data.csv'")
     #the subscriber remains alive as a daemon thread - no active loop is needed
     #because the broker calls log_to_csv() directly via callback on each publish