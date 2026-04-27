# This module simulates the data collection behaviour of three physical sensors
# that would be attached to a real ESP32 microcontroller:!
#
#   1.LDR (Light Dependent Resistor) - measures ambient light intensity (0-100)!
#   2.VEML6070 - measures UV radiation index (0-800)!
#   3.BME680 - measures temperature, humidity, atmospheric pressure and gas resistance!
#
# Since no physical hardware is available, all sensor readings are generated
# through a simulation process using sine waves, random noise and occasional spikes to
# produce realistic, time-varying data that mirrors real environmental conditions!
#
# Simulation techniques used:
#   - Sine wave (daily cycle): models the natural rise and fall of temperature
#     and light intensity over a 24-hour period!
#   - Random noise: simulates the small measurement variance inherent in all
#     physical sensors due to electrical interference and environmental factors!
#   - Random spikes (5% probability): simulates sudden pollution or VOC
#     (Volatile Organic Compound) detection events in gas resistance readings!
#
# In a real hardware setup this file would be replaced by MicroPython
# drivers that read directly from the sensor hardware via I2C or ADC pins!



##importing modules!
import random
import math
import time

##simulated sensor class!
class Sensor:
    
    #Simulating all sensors attached to the ESP32 microcontroller!

   #Generating realistic sensor data using sine waves to model daily cycles,
   #random noise to simulate physical sensor variance, and occasional spikes
   #to represent environmental events such as pollution or VOC detection!

    #Attributes:
        #start_time (float): Unix timestamp recorded at instantiation, used
                            #as the reference point for the LDR daily cycle simulation!
    

    def __init__(self):
         
        #Initialising the Sensor simulation!

        #Recording the current time as start_time, which serves as the reference
        #point for calculating elapsed minutes in the LDR sine wave cycle!
        #This ensures the simulation starts from a consistent phase regardless
        #of the actual time of day!
        

        #recording start time to  use as a reference for the daily cycle simulation!
        self.start_time = time.time()

    def read_ldr(self):
      
        #Simulating an LDR (Light Dependent Resistor) light intensity reading!

        #Producing a smoothly varying value between 0 and 100 using a sine wave
        #based on elapsed minutes since instantiation, with small random noise
        #added to simulate real sensor variance!

        #Returns:
            #int: Light intensity value in the range 0-100, where 0 = darkness
                 #and 100 = maximum light intensity!
        
       t = (time.time() - self.start_time)/60 #scaling time in minutes!
       base = 50 + 40 * math.sin(t)# adding sine wave in range of 10-90
       noise = random.randint(-5, 5)#small random noise for realism!
       return max(0, min(100, int(base + noise)))
    
    def read_veml6070(self):
       
        #Simulating a VEML6070 UV radiation sensor reading!

        #Modeling the natural day/night UV cycle: high UV values during daylight
        #hours and near-zero values at night, reflecting the
        #behaviour of a real UV sensor exposed to sunlight!

        #Returns:
            #int: UV intensity value in arbitrary sensor units!
                 #Range: 100-800 during daylight, 0-50 at night!
        

        #produces high values through the day and lower through the night!
        hour = (time.time() / 3600) % 24
        if 6 <= hour <= 18:
            base = random.randint(100, 800) #high UV during daylight hours
        else:
            base = random.randint(0, 50)#minimal UV at night (sensor noise floor)
        return base
    
    def read_bme680(self):
      
        #Simulating a BME680 environmental sensor reading!

        #All four parameters follow a 24-hour sine wave cycle with added
        #random noise to simulate real environmental variation:

         # - Temperature: peaks in the afternoon, lowest before dawn!
         # - Humidity: inversely correlated with temperature !
         # - Pressure: gentle diurnal variation around 1012 hPa!
         # - Gas resistance: random baseline with a 5% chance of a downward spike
         #   simulating a VOC (Volatile Organic Compound) or pollution event!

        #Returns:
            #dict: A dictionary containing the following keys and values:
              #  - 'temperature' (float): Temperature in Celsius!
              #  - 'humidity' (float): Relative humidity percentage!
              #- 'pressure' (float): Atmospheric pressure in hPa!
              #- 'gas_resistance' (float): Gas resistance in Ohms!
        

        hour = (time.time() / 3600) % 24
        phase = (hour / 24) * 2 * math.pi#converting hour to radians for sine wav!
        temperature = 21 + 7 * math.sin(phase) + random.uniform(-0.7, 0.7)
        humidity = 60 - 12 * math.sin(phase) + random.uniform(-3, 3) #inverse of temperature!
        pressure = 1012 + 3 * math.sin(phase) + random.uniform(-2, 2)

        gas = 15000 + random.uniform(-3000, 3000)
        if random.random() < 0.05:
            #5% posibility of a downward spike simulating a pollution/VOC event!
            gas -= random.uniform(5000, 10000)

        return {
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "pressure": round(pressure, 2),
            "gas_resistance": round(gas, 2)
        }
    
    def read_all_sensors(self):
         
        #Reading all three sensors and merging the results into a single dictionary!

        #Calling read_ldr(), read_veml6070() and read_bme680() and combining their
        #outputs into one flat dictionary ready for MQTT publishing, CSV logging
        #or dashboard visualisation!

        #Returning:
            #dict: A dictionary with the following keys:
                #- 'ldr' (int): Light intensity (0-100)!
                #- 'uv' (int): UV radiation level (0-800)!
                #- 'temperature' (float): Temperature in Celsius!
                #- 'humidity' (float): Relative humidity percentage!
                # - 'pressure' (float): Atmospheric pressure in hPa!
                #- 'gas_resistance' (float): Gas resistance in Ohms!
            
        return {
            "ldr": self.read_ldr(),
            "uv": self.read_veml6070(),
            **self.read_bme680()#unpacking BME680 dictionary directly into the result!
        }
     
   
   
   
# standalone test - runs only when this file is executed directly!
# reading all sensors 5 times at 1 second intervals and prints the output!
if __name__ == "__main__":
    sim = Sensor()
    for _ in range(5):
        data = sim.read_all_sensors()
        print(data)
        time.sleep(1)
