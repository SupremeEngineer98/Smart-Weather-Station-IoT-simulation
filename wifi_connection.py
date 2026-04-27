# This module simulates the MicroPython network.WLAN interface that would run on a real ESP32 microcontroller!

# In a real hardware system this file would be replaced by MicroPython's
# built-in network module, where:
#   import network!
#   wlan = network.WLAN(network.STA_IF)!
#   wlan.active(True)!
#   wlan.connect('SSID', 'password')!
#
# Simulated functionality:
#   - scan_networks(): simulates Wi-Fi radio scan with 1 second delay!
#   - connect(ssid): simulates DHCP handshake with 1 second delay!
#   - connect_first_open(): auto-joins the first open network!
#   - is_connected(): returns current connection status!
#
# The publisher uses is_connected() to gate MQTT publishing, ensuring no
# messages are sent when the simulated network is unavailable!


##importing the time and random modules!
import time, random


##simulating the wifi-connection class!
class Wifi:
     
    #Simulating Wi-Fi connection management for the ESP32 microcontroller!

    #Mimics the network scanning, SSID connection and auto-join behaviour 
    #of a real ESP32 running MicroPython's network.WLAN interface!
    
    #All network operations include simulated delays to replicate real
    #connection latency and DHCP handshake timing!

    #Attributes:
        #connected_ssid (str or None): The SSID of the currently connected
                                      #network, or None if disconnected!
        #networks (list): A predefined list of (SSID, AuthType) tuples
                         #representing available Wi-Fi networks in range!
    
    
    def __init__(self):

       
        #Initialising the Wi-Fi manager in a disconnected state!

        #Setting up a predefined list of simulated available networks, each
        #represented as a tuple of SSID, AuthType. This is mirroring the output
        #of a real Wi-Fi scan on an ESP32 board!

        #The device starts disconnected (connected_ssid = None) and must
        #call connect() or connect_first_open() before publishing data!
        
        self.connected_ssid = None
        self.networks = [
            ("DCETLocalVOIP", "WPA2-PSK"),
            ("OpenNetwork", "Open"),
            ("HomeWiFi", "WPA-PSK"),
            ("Dei_CollegeWiFi", "Open"),
        ]

       
    def scan_networks(self):
         
        #Simulating a Wi-Fi radio scan for available networks!

        #Introducing a 1 second delay to mimic the time a real ESP32 takes
        #to scan available channels and collect beacon frames from nearby
        #access points! 
        # Printing and returns all discovered networks!

        #Returning:
            #list: A list of (SSID, AuthType) tuples representing all
                  #available networks found during the scan!
        
        print("Scanning to find Wi-Fi networks")
        time.sleep(1)  #simulating radio scan time
        for ssid, auth in self.networks:
            print(f"* {ssid} - Auth: {auth}")
        return self.networks
    

    def connect(self, ssid):#mocked method to simulate wi-fi connection functionality!
           
        #Attempts to connect to a specific Wi-Fi network by SSID!

        #Simulating the connection process including DHCP handshake with a
        #1 second delay!
        # Returning True on success, False if the SSID is not
        #found in the list of available networks!

        #Args:
            #ssid (str): The SSID of the network to connect to!

        #Returning:
            #bool: True if the connection was established successfully,
                  #False if the SSID was not found in the available networks!
        
        available_ssids = [net[0] for net in self.networks]
        if ssid in available_ssids:
            print(f"Connecting to Wi-Fi: {ssid} ...")
            time.sleep(1)#simulating scanning delay
            self.connected_ssid = ssid
            print(f"Connected to Wi-Fi: {ssid}")
            return True
        else:
            print(f"SSID {ssid} not found!")
            return False
        


    def connect_first_open(self):##simulating the process where the broker connects to the first open network!
         
           
       # Connecting to the first open  network!

       #  Iterating through the list of available networks and attempting to connect
       #  to the first one with an 'Open' authentication type!
       #  This is mirroring the auto-join behaviour of a real ESP32 in an environment with open access points!
       

       # Returning:
           # bool: True if an open network was found and connected successfully,
                 # False if no open networks are available!
        
        for ssid, auth in self.networks:
            if auth.lower() == "open":
                return self.connect(ssid)
        print("No open networks found.")
        return False

    def is_connected(self):
         
       # Returning the current Wi-Fi connection status.

        #Used by the publisher to gate MQTT publishing!
        # Messages are only sent when this method returns True, preventing publish attempts
        #when the simulated network connection has been lost!
        

        #Returning:
            #bool: True if currently associated with a network, False otherwise!
        
        return self.connected_ssid is not None
        


# standalone test - runs only when this file is executed directly!
# simulating a full scan and auto-connection to the first open network!
if __name__ == "__main__":
    wifi = Wifi()
    wifi.scan_networks()
    wifi.connect_first_open()##simulating a connection into an open network!