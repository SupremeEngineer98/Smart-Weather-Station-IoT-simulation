# This module creates a single shared MQTTBroker instance that is imported
# by  publisher.py and subscriber.py, allowing them to communicate
# through the same in-process message bus!
#
# Design pattern: Singleton
#   By instantiating MQTTBroker() at module level, Python's import system
#   guarantees that both threads receive the same object's reference!
#   This ensures that subscriptions registered by the subscriber are visible
#   to the publisher when it calls publish(), replicating the behaviour of a
#   real network broker!
#
# In a real IoT system this file would not exist. In contrast, both ESP32 devices
# would connect independently to an external MQTT broker over Wi-Fi!
# Here it serves as the simulation equivalent of that network broker!
#
# Usage:
#   from broker import shared_broker!
#   shared_broker.publish("sensors/data", payload, qos=1)!
#   shared_broker.subscribe("sensors/data", callback_function)!

from mqtt_broker import MQTTBroker #this is a custom library that I developed in order to simulate the mqtt broker!


#single shared instance used by both publisher and subscriber!
# both threads reference the same object, enabling in-process message passing!
shared_broker = MQTTBroker()