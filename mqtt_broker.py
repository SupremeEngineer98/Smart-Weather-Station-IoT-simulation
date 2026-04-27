# This module is simulating an MQTT broker entirely in Python, without any real
# network communication or external MQTT server!
#

# This simulation preserves the publish/subscribe
# architecture of a real IoT system within a single Python environment!
#
# Supported functionality:
#   1. subscribe(topic, callback) - registers a callback on a given topic!
#   2. publish(topic, message, qos) - delivers a message to all subscribers!
#   3. QoS 0 - fire and forget: message delivered once, no retry on failure!
#   4. QoS 1 - at least once: message retried up to 3 times on failure,
#              with a 0.5 second delay between each attempt!
#
# In a real IoT deployment this file would be replaced by a physical MQTT
# broker running on a server or cloud platform, with ESP32
# devices connecting over Wi-Fi using the MicroPython umqtt library!

import time#importing the time module!

class MQTTBroker:
       
    #Simulating an MQTT publish/subscribe message broker with QoS support!

    #Maintaining an internal dictionary mapping topic strings to lists of
    #registered callback functions!
    #When a message is published to a topic,all registered callbacks are invoked with the topic and message payload!
    

     # Supports two QoS levels:
     # - QoS 0 (fire and forget): delivers the message once with no retry!
     # - QoS 1 (at least once): retries delivery up to 3 times on failure,
     #  with a 0.5 second delay between attempts!

   # Attributes:
        #subscribers (dict): Maps topic strings to lists of callback functions.
                            

    def __init__(self):
        
        #Initialising the broker with an empty subscribers dictionary!

        #The dictionary is populated dynamically as clients call subscribe()!
        #Each key is a topic string and each value is a list of callbacks!
        
        self.subscribers = {}

    def subscribe(self, topic, callback):
          
        #Registering a callback function to receive messages on the given topic!

        #If the topic does not yet exist in the subscribers dictionary, a new
        #empty list is created for it, before appending the callback!
        # Multiple callbacks can be registered on the same topic and all will be invoked on each publish!
               

        #Args:
            #topic (str): The MQTT topic to subscribe to!
            #callback (callable): Function to call when a message is published
                                 #to the topic. Must accept (topic, message) arguments!
        
        if topic not in self.subscribers:
            self.subscribers[topic] = []

        self.subscribers[topic].append(callback)
        print("Subscriber added to topic:", topic)

    def publish(self, topic, message, qos=1):
         
     #Publishing a message to a topic and invoking all registered callbacks!

       # Delivering behaviour depends on the QoS level:
       #   - QoS 0: attempts delivery once; any exception is caught and logged
       #            but no retry is made!
        #  - QoS 1: retries delivery up to 3 times if the callback raises an
        #           exception, with a 0.5 second delay between attempts
        #           logs a failure message if all 3 attempts are exhausted!

       # Args:
       #     topic (str): The MQTT topic to publish to!
       #     message (dict): The sensor payload to deliver to all subscribers!
       #     qos (int): Quality of Service level. 0 = fire and forget,
       #                1 = at least once delivery. Defaults to 1!
        

        print(f"Publishing to topic '{topic}' with QoS={qos}")

        #checking if any subscribers exist for this topic
        if topic not in self.subscribers:
            print("No subscribers for topic:", topic)
            return

        for callback in self.subscribers[topic]:

            if qos == 0:
                #QoS 0: attempt delivery once, no retry!
                try:
                    callback(topic, message)
                except Exception as e:
                    print(f"QoS 0 delivery failed: {e}")

            elif qos == 1:
                #QoS 1: retry up to 3 times until delivery succeeds!
                delivered = False
                for attempt in range(1, 4):
                    try:
                        callback(topic, message)
                        delivered = True
                        print(f"QoS 1 delivered on attempt {attempt}")
                        break
                    except Exception as e:
                        print(f"QoS 1 attempt {attempt}/3 failed: {e}")
                        time.sleep(0.5) # short delay before retry

                if not delivered:
                    print(f"QoS 1 delivery failed after 3 attempts on topic '{topic}'")


# standalone test - runs only when this file is executed directly!
# this test tests both QoS 0 and QoS 1 delivery with a simple callback!
if __name__ == "__main__":

    def test_callback(topic, message):
        print("Message received from topic:", topic)
        print("Data:", message)

    broker = MQTTBroker()

    broker.subscribe("sensors/data", test_callback)

    #testing QoS 0
    print("\n-- QoS 0 Test --")
    broker.publish("sensors/data", {"temperature": 24.5, "humidity": 58, "ldr": 70}, qos=0)

    # testing QoS 1 - at least once delivery
    print("\n-- QoS 1 Test --")
    broker.publish("sensors/data", {"temperature": 25.0, "humidity": 60, "ldr": 75}, qos=1)

