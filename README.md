# Smart Weather Station (IoT Simulation)

## Overview
The Smart Weather Station is a Python-based IoT simulation system that emulates real-world environmental data collection using virtual sensors. The system simulates an end-to-end IoT pipeline, including data generation, MQTT-like communication, storage, and real-time visualization through an interactive Streamlit dashboard.

Due to the absence of physical hardware, the entire system is implemented in Python within a simulated environment in VS Code.

---

## System Architecture
The system simulates a typical IoT architecture:

- Virtual sensors generate environmental data (temperature, humidity, light, UV, gas resistance, pressure)
- Data is published through a simulated MQTT broker
- Data is stored in a CSV file
- A Streamlit dashboard visualizes the data in real-time

To simulate real-world concurrency, Python threading is used to represent multiple devices communicating simultaneously.

---

## Features

### Sensor Simulation
- Temperature, humidity, light intensity (LDR), UV radiation, gas resistance, and atmospheric pressure
- Realistic data generation using sinusoidal patterns
- Random noise for natural variation
- Occasional spikes (5% probability) to simulate environmental anomalies

---

### Communication System
- Simulated MQTT broker with publish/subscribe architecture
- QoS 0: fire-and-forget delivery
- QoS 1: guaranteed delivery with retry mechanism
- WiFi connection simulation before publishing

---

### Data Storage
- All sensor data stored in `sensor_data.csv`
- Timestamped entries for each measurement
- Thread-safe logging using `threading.Lock`

---

### Dashboard (Streamlit)
Interactive visualization dashboard with:

- Line charts with threshold alerts
- Histograms with limit indicators
- Boxplots for statistical distribution
- Scatter plots with selectable axes
- Gauge indicators for real-time values
- Rolling average trend analysis
- Raw data table view
- Date filtering based on available data

---

## Sensor Thresholds

| Sensor | Threshold |
|--------|----------|
| Temperature | 30°C |
| Humidity | 80% |
| UV Index | 600 mW/cm² |
| Light (LDR) | 90/100 |
| Pressure | 1020 hPa |
| Gas Resistance | 20,000 Ω |

---

## Project Structure

- `sensors.py` → Virtual sensor simulation
- `wifi_connection.py` → WiFi connection simulation
- `mqtt_broker.py` → MQTT broker with QoS support
- `broker.py` → Shared broker instance
- `publisher.py` → Sensor data publisher
- `subscriber.py` → Data receiver and logger
- `csv_logger.py` → CSV data storage handler
- `main.py` → System execution (multi-threaded simulation)
- `prototype_dashboard.py` → Streamlit visualization dashboard

---

## How to Run

### 1. Install dependencies
```bash
py -m pip install streamlit numpy pandas matplotlib plotly
Run the main script first to start sensor data generation and collection: py main.py
Open a new terminal and run: py -m streamlit run prototype_dashboard.py
