# Monitoring Your air quality with the Raspberry Pi Pico W

## What are we going to do?
Together with you, I want to build an air quality monitor to gather different parameters. To know whether I have to air my room or not I need to know the current humidity level and the carbon dioxide concentration. So my device has to be able to measure those. I want to collect, store and visualize the gathered data centralized. In the future, I want to do this by sending all the data to my homeserver, where I can use software like InfluxDB and Grafana. Last but not least I want to get notified, whenever the humidity or the CO2 exceeds a certain threshold. This could be done by mail (using Grafana Alerts) or even better by push notification (using Home Assistant). There are a few other improvements I might implement later like a small display, a battery pack, and a 3D-printed case to bring it all together.

## About the Raspberry Pi Pico
The Raspberry Pi Pico is a low-cost, high-performance microcontroller board. There are two different versions: the normal Pico and the Pico W, which comes with built in wlan. It comes with a rich peripheral set, including SPI, I2C, and eight Programmable I/O (PIO) state machines for custom peripheral support. You can use C or [MicroPython](https://micropython.org/) (an implementation of Python 3) to program it. All this makes it the perfect match for all kinds of small hobby projects like this.

##  About the sensors
I am using three sensors to gather all the data I need:

DHT11: This sensor measures temperature and humidity. Although less accurate than the DHT22, it is cost-effective and reliable for basic environmental monitoring.

MQ9: This sensor is used for detecting carbon monoxide (CO) and combustible gases. It provides gas concentration values, which are valuable for analyzing air quality.

MQ135: This sensor is excellent for measuring air quality by detecting gases like ammonia (NH3), sulfur (S), benzene, smoke, and other harmful chemicals. It is particularly useful for obtaining a general air quality index.

By combining these sensors, we can measure temperature, humidity, detect harmful gases, and assess overall air quality in the environment.


## 1. DHT11 (Temperature & Humidity Sensor):
Pins:

VCC: Connect to 5V on the microcontroller.

GND: Connect to the ground (GND).

Data: Connect to a digital input pin (e.g., D2). Use a 10k pull-up resistor between Data and VCC.

##  2. MQ9 (Gas Sensor for CO & Combustible Gases):
Pins:

VCC: Connect to 5V on the microcontroller.

GND: Connect to the ground (GND).

AO (Analog Output): Connect to an analog input pin (e.g., A0) for gas concentration measurements.

DO (Digital Output): Optionally connect to a digital pin if you want threshold-based output (set using the onboard potentiometer).

##  3. MQ135 (Air Quality Sensor):
Pins:

VCC: Connect to 5V on the microcontroller.

GND: Connect to the ground (GND).

AO (Analog Output): Connect to another analog input pin (e.g., A1) for gas concentration readings.

DO (Digital Output): Optionally connect to a digital pin for threshold-based output.

# The code
Create a new file called ‘main.py’ (it is important that you name it like this, otherwise CircuitPython won’t find it) and copy the code into it. As soon as you save the file the code will be executed.
To check the outputs use Mu to open a serial connection. If you are on Linux you can also use minicom (‘sudo minicom -o -D /dev/ttyACM0’).
You can check if your sensors are working by simply blowing on them. This should raise the CO2 and TVOC readings.
