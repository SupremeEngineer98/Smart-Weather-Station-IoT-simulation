
# Entry point for the Smart Weather Station Prototype!

# This file is the main entry point for the IoT simulation system!
# It uses Python's threading module to simulate two separate ESP32 devices
# running concurrently on the same machine:

# Thread 1 - Publisher  : reads sensor values every second and publishes
#                           them to the shared MQTT broker!
# Thread 2 - Subscriber : receives MQTT messages and writes each reading
#                         to sensor_data.csv via CSVLogger!

# Simulated architecture:
#   ESP32 Device A (publisher) --> Wi-Fi --> MQTT Broker --> Wi-Fi --> ESP32 Device B (subscriber)!
#
# In this simulation both threads share the same in-process broker object
# defined in broker.py, instead of a real network broker!
#
# Both threads are launched as daemon threads (daemon=True), meaning they
# will terminate automatically when the main thread exits, preventing
# orphaned background processes!
#
# Usage:
#  Start: py main.py!
#   Stop: Ctrl+C!

##importing all the required libraries/modules!
import threading
import logging
from publisher import run_publisher #publisher library is the custom made library I developed in order to mimic publisher's functionality. It's located inside the folder!
from subscriber import run_subscriber #subscriber library is the custom made library I developed in order to mimic psubscriber 's functionality. It's located inside the folder!


#configuring logging to display timestamped messages at INFO level and above!
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():

     
    #Initialises and launches the Smart Weather Station simulation!

    #Starts the subscriber thread first to ensure it is ready and listening
    #on the MQTT topic before the publisher begins sending data!
    # This mirrors the correct startup sequence of a real IoT system, where the consumer
    #node must be active before the producer starts transmitting!

    #Both threads run as daemon threads so they stop automatically when the
    #main thread exits!
    # The main thread is kept alive with an infinite loop
    #that blocks until the user interrupts execution with Ctrl+C!
    
     
    logging.info("Smart Weather Station System Starting")
    

    # Starting Subscriber First!
    # the subscriber must be ready and subscribed to 'sensors/data' before
    # the publisher starts sending, to avoid missing the first messages!
    
    subscriber_thread = threading.Thread(target=run_subscriber, name="Subscriber", daemon=True)
    subscriber_thread.start()
    logging.info("Subscriber thread started.")

    #Starting Publisher
    #a small implicit delay exists because subscriber_thread.start() returns
    # only after the thread has been initialised and CSVLogger has subscribed#
    publisher_thread = threading.Thread(target=run_publisher, name="Publisher", daemon=True)
    publisher_thread.start()
    logging.info("Publisher thread started.")

    #Retaining the Main Thread Alive!
    # daemon=True means both threads stop automatically when main() exits,
    # so the main thread must remain alive for the system to keep running!
    try:
        while True:
            pass #blocking the main thread indefinitely until KeyboardInterrupt!
    except KeyboardInterrupt:
        logging.info(" System stopped")

if __name__ == "__main__":
    main()


