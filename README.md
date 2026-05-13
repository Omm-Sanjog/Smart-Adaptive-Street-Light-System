```text
███████╗███╗   ███╗ █████╗ ██████╗ ████████╗
██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝
███████╗██╔████╔██║███████║██████╔╝   ██║
╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║
███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║
╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝

███████╗████████╗██████╗ ███████╗███████╗████████╗
██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝
███████╗   ██║   ██████╔╝█████╗  █████╗     ██║
╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══╝     ██║
███████║   ██║   ██║  ██║███████╗███████╗   ██║
╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝

██╗     ██╗ ██████╗ ██╗  ██╗████████╗
██║     ██║██╔════╝ ██║  ██║╚══██╔══╝
██║     ██║██║  ███╗███████║   ██║
██║     ██║██║   ██║██╔══██║   ██║
███████╗██║╚██████╔╝██║  ██║   ██║
╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝

💡 SMART STREETLIGHT 💡
ESP32 • LoRa • IoT • Energy Monitoring
```

# Smart Adaptive Street Light System

## Overview

The Smart Adaptive Street Light System is an Internet of Things (IoT)-based intelligent street lighting solution designed to improve energy efficiency, enable remote monitoring, and provide adaptive lighting control using sensors and wireless communication.

This project uses an ESP32 microcontroller as the main controller and integrates multiple modules such as LoRa communication, motion sensing, day/night detection, AC dimming control, relay switching, and energy monitoring.

The system automatically controls the brightness of a street light based on environmental conditions and human or vehicle movement. It also transmits real-time operational and energy consumption data to a central monitoring station using LoRa communication.

---

# Features

* Automatic day and night detection
* Motion-based adaptive brightness control
* AC lamp dimming using TRIAC dimmer
* Complete relay-based power control
* Real-time voltage, current, and power monitoring
* Long-range LoRa wireless communication
* Node ID and location-based identification
* CSV data logging
* WebSocket-based real-time dashboard support
* Modular ESP32 firmware architecture
* Expandable for multi-node smart city deployments

---

# System Architecture

The project consists of two major sections:

## 1. Street Light Node (Transmitter)

This is the actual smart street light unit installed on the field.

### Functions:

* Detects day or night using LDR sensor
* Detects nearby movement using microwave radar sensor
* Controls streetlight brightness dynamically
* Measures electrical parameters using energy meter
* Transmits data to ground station through LoRa

---

## 2. Ground Station (Receiver)

The ground station receives data from all street light nodes and forwards it to the monitoring software.

### Functions:

* Receives LoRa packets
* Displays incoming node data
* Sends serial data to Python backend
* Supports dashboard integration
* Logs data into CSV files

---

# Components Used

| Component                        | Purpose                          |
| -------------------------------- | -------------------------------- |
| ESP32                            | Main microcontroller             |
| SX1278 LoRa Module (433MHz)      | Wireless communication           |
| LDR Sensor                       | Day/Night detection              |
| RCWL-0516 Microwave Radar Sensor | Motion detection                 |
| PZEM-004T Energy Meter           | Voltage/current/power monitoring |
| TRIAC AC Dimmer Module           | Lamp brightness control          |
| 5V 30A Relay Module              | Master ON/OFF control            |
| AC Lamp                          | Street light load                |
| Python Backend                   | Data logging and dashboard       |

---

# Working Principle

## Daytime Operation

* LDR detects daylight
* Relay turns OFF the lighting system
* Lamp remains OFF
* Power consumption is minimized

---

## Nighttime Operation

* LDR detects darkness
* Relay enables the lighting system
* Motion sensor starts monitoring movement

### No Motion Detected

* Lamp brightness reduced to minimum level
* Energy consumption decreases

### Motion Detected

* Lamp brightness increased to maximum level
* Improves visibility and safety

---

# Energy Monitoring

The PZEM-004T module measures:

* Voltage
* Current
* Power
* Estimated energy consumption

This information is transmitted to the ground station and stored for analysis.

---

# LoRa Communication

The system uses SX1278 LoRa modules operating at 433MHz.

Each streetlight node periodically transmits:

* Node ID
* Location
* Day/Night status
* Motion status
* Brightness percentage
* Voltage
* Current
* Power
* RSSI signal strength

Example transmitted packet:

```text
ID:SL-01,Loc:KIIT_GATE_1,N:1,M:0,B:30,V:230.5,I:0.45,P:103,RSSI:-72
```

---

# Software Architecture

## ESP32 Firmware

The firmware is written in modular format.

### Main Functions:

* Sensor reading
* Relay control
* Dimmer control
* Energy monitoring
* LoRa transmission
* Packet generation

---

## Python Backend

The Python application acts as:

* Serial logger
* WebSocket bridge
* CSV data logger
* Dashboard communication layer

### Features:

* Automatic COM port detection
* Real-time packet parsing
* CSV logging into data.csv
* Dashboard communication using WebSockets
* Real-time energy calculation

---

# Folder Structure

````text
Smart-Adaptive-Street-Light-System/
│
├── Analysis_Report/
│   ├── analysis_charts.png
│   └── analysis_report.txt
│
├── Main/
│   ├── analysis.py
│   ├── data.csv
│   ├── logger.py
│   └── streetlight_dashboard.html
│
├── Streetlight/
│   ├── Final_Codes/
│   │   ├── Dashboard/
│   │   │   ├── analysis.py
│   │   │   ├── data.csv
│   │   │   ├── logger.py
│   │   │   └── streetlight_dashboard.html
│   │   │
│   │   ├── Receiver/
│   │   │   └── receiver_code.ino
│   │   │
│   │   └── Transmitter/
│   │       └── transmitter_code.ino
│   │
│   └── Testing_Codes/
│       ├── LDR_Test/
│       ├── Motion_Test/
│       ├── LoRa_Test/
│       ├── Relay_Test/
│       └── PZEM_Test/
│
├── Smart Streetlight_Dashboard V2.html
├── LICENSE
└── README.md
```text
Smart-Street-Light/
│
├── transmitter/
│   └── transmitter_code.ino
│
├── receiver/
│   └── receiver_code.ino
│
├── python_backend/
│   ├── logger.py
│   ├── dashboard.html
│   ├── data.csv
│   └── requirements.txt
│
├── diagrams/
│   ├── circuit_diagram.png
│   └── architecture.png
│
└── README.md
````

---

# Pin Connections

## ESP32 Connections

| Module               | ESP32 Pin |
| -------------------- | --------- |
| LDR Sensor           | GPIO 34   |
| Motion Sensor        | GPIO 27   |
| Relay Module         | GPIO 26   |
| TRIAC Dimmer         | GPIO 25   |
| Zero Cross Detection | GPIO 4    |
| PZEM TX              | GPIO 16   |
| PZEM RX              | GPIO 17   |
| LoRa NSS             | GPIO 5    |
| LoRa RST             | GPIO 14   |
| LoRa DIO0            | GPIO 2    |

---

# Required Libraries

## Arduino Libraries

Install the following libraries:

* LoRa by Sandeep Mistry
* PZEM004Tv30
* RBDdimmer

---

## Python Libraries

Install using:

```bash
pip install websockets pyserial pandas numpy matplotlib
```

---

# Communication Packet Format

The transmitter sends structured LoRa packets in the following format:

```text
ID:SL-01,Loc:KIIT_GATE_1,N:1,M:0,B:30,V:230.5,I:0.45,P:103,RSSI:-72
```

## Packet Fields

| Field | Meaning               |
| ----- | --------------------- |
| ID    | Node ID               |
| Loc   | Node location         |
| N     | Night status          |
| M     | Motion detection      |
| B     | Brightness percentage |
| V     | Voltage               |
| I     | Current               |
| P     | Power                 |
| RSSI  | Signal strength       |

---

# Dashboard and Data Analytics

The dashboard system provides:

* Live node monitoring
* Real-time power visualization
* CSV logging
* WebSocket communication
* Historical analysis support
* Automatic energy calculations

The analysis scripts generate:

* Energy usage trends
* Voltage/current graphs
* Power consumption charts
* Statistical reports

---

# Setup Instructions

## ESP32 Setup

1. Install Arduino IDE or PlatformIO
2. Install ESP32 board support
3. Install required libraries
4. Upload transmitter firmware to streetlight node
5. Upload receiver firmware to ground station ESP32

---

## Python Backend Setup

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows:

```bash
.\.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install websockets pyserial pandas numpy matplotlib
```

### Run Backend

```bash
python logger.py
```

---

# Dashboard Features

The dashboard can display:

* Live node status
* Motion activity
* Lamp brightness
* Voltage and current
* Power consumption
* Energy usage trends
* RSSI signal strength
* Real-time updates using WebSockets

---

# Future Improvements

Potential upgrades:

* Solar-powered streetlight integration
* GPS-based node mapping
* Cloud connectivity
* Mobile app integration
* AI-based traffic prediction
* Fault detection and maintenance alerts
* Automatic weather-based brightness control
* OTA firmware updates

---

# Applications

This project can be used in:

* Smart cities
* Campus lighting systems
* Industrial lighting
* Highway lighting
* Parking areas
* Remote village lighting
* Energy-saving public infrastructure

---

# Advantages

* Reduces electricity consumption
* Increases lamp lifespan
* Enables remote monitoring
* Improves maintenance efficiency
* Supports scalable deployments
* Provides intelligent lighting automation

---

# Safety Note

This project involves high-voltage AC components.

Please ensure:

* Proper insulation
* Safe wiring practices
* Isolated testing environment
* Correct grounding
* Caution while handling AC dimmer and relay modules

---

# License

This project is released under the MIT License.

---

# Author

Developed as an IoT-based Smart Adaptive Street Lighting System for energy-efficient and intelligent lighting applications.
