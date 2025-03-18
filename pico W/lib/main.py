import network
import machine
import utime
import dht
from machine import I2C, Pin, ADC
from microdot import Microdot, Response
from ssd1306 import SSD1306_I2C
import urequests  # For sending data to ThingSpeak
import uasyncio as asyncio
import os

# Wi-Fi connection function
def connect_to_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Connecting to the network...")
        sta_if.active(True)
        sta_if.connect("YUGAN", "12345678")  # Replace with your Wi-Fi credentials

        # Wait for the connection and check if it gets connected
        attempt = 0
        while not sta_if.isconnected() and attempt < 10:  # Max 10 attempts
            attempt += 1
            utime.sleep(1)
            print(f"Attempting to connect... ({attempt}/10)")

        if not sta_if.isconnected():
            print("Failed to connect to Wi-Fi.")
            return False  # Return False if connection fails
        else:
            print("Connected to Wi-Fi!")
            print("IP address:", sta_if.ifconfig()[0])  # Prints the IP address
            return True  # Return True if connection is successful
    else:
        print("Already connected to Wi-Fi")
        print("IP address:", sta_if.ifconfig()[0])
        return True  # Return True if already connected

# Initialize I2C and OLED Display
def initialize_i2c():
    try:
        i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
        devices = i2c.scan()
        print("I2C devices found:", devices)
        if not devices:
            raise OSError("No I2C devices found!")
        oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)
        oled.fill(0)
        oled.text("Initialized!", 0, 0)
        oled.show()
        return oled
    except Exception as e:
        print(f"I2C initialization failed: {e}")
        return None

# Sensor reading functions
mq9 = ADC(Pin(26))  # MQ9 sensor connected to GPIO26
mq135 = ADC(Pin(27))  # MQ135 sensor connected to GPIO27
dht11 = dht.DHT11(Pin(2))  # Using GPIO2 for DHT11

# MQ9 Sensor reading function
def read_mq9():
    try:
        value = mq9.read_u16()
        voltage = value * 3.3 / 65535  # Convert the ADC value to a voltage
        print(f"MQ9 Voltage: {voltage}")
        return voltage
    except Exception as e:
        print(f"Error reading MQ9 sensor: {e}")
        return 0  # Return 0 if error

# MQ135 Sensor reading function
def read_mq135():
    try:
        value = mq135.read_u16()
        voltage = value * 5 / 65535  # Convert the ADC value to a voltage
        print(f"MQ135 Voltage: {voltage}")
        return voltage
    except Exception as e:
        print(f"Error reading MQ135 sensor: {e}")
        return 0  # Return 0 if error

# DHT11 Sensor reading function
def read_dht11():
    try:
        dht11.measure()  # Measure temperature and humidity
        temperature = dht11.temperature()  # Temperature in Celsius
        humidity = dht11.humidity()  # Humidity in percentage
        print(f"Temperature: {temperature}°C, Humidity: {humidity}%")
        return temperature, humidity
    except Exception as e:
        print(f"Error reading DHT11 sensor: {e}")
        return 0, 0  # Return default values if error

# Function to send data to ThingSpeak
def send_data_to_thingspeak(temp, hum, mq9_voltage, mq135_voltage):
    # ThingSpeak API Key and URL
    THINGSPEAK_API_KEY = "CENTGSODDSEPT8GE"  # Replace with your ThingSpeak API key
    THINGSPEAK_URL = "https://api.thingspeak.com/update"
    
    payload = {
        "api_key": THINGSPEAK_API_KEY,
        "field1": temp,
        "field2": hum,
        "field3": mq9_voltage,
        "field4": mq135_voltage
    }
    
    try:
        response = urequests.post(THINGSPEAK_URL, data=payload)
        print(f"Data sent to ThingSpeak: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"Error sending data to ThingSpeak: {e}")

# Microdot Web Server
app = Microdot()

@app.route('/')
async def index(request):
    temp, hum = read_dht11()  # Read DHT11 sensor data
    mq9_voltage = read_mq9()  # Read MQ9 sensor data
    mq135_voltage = read_mq135()  # Read MQ135 sensor data
    
    # Send data to ThingSpeak
    send_data_to_thingspeak(temp, hum, mq9_voltage, mq135_voltage)

    # Check for None values and provide default text if they are None
    if temp == 0 or hum == 0:
        temp = "Sensor Error"
        hum = "Sensor Error"

    if mq9_voltage == 0:
        mq9_voltage = "Sensor Error"

    if mq135_voltage == 0:
        mq135_voltage = "Sensor Error"

    # Read the index.html template file
    try:
        with open('index.html', 'r') as file:
            html = file.read()
        
        # Replace placeholders with actual data
        html = html.replace("{{ temp }}", str(temp))
        html = html.replace("{{ hum }}", str(hum))
        html = html.replace("{{ mq9_voltage }}", str(mq9_voltage))
        html = html.replace("{{ mq135_voltage }}", str(mq135_voltage))
        
        # Return the HTML response with correct content type
        response = Response(html)
        response.headers['Content-Type'] = 'text/html'
        return response
    
    except Exception as e:
        print(f"Error reading the index.html file: {e}")
        return Response("Error loading page", content_type="text/html")

# Main Execution
# Ensure the Wi-Fi connection is established first
if connect_to_wifi():
    oled = initialize_i2c()  # Initialize I2C and OLED display if Wi-Fi is connected
    if oled:
        oled.fill(0)
        oled.text("Web Server Ready", 0, 0)
        oled.show()
    print("Starting web server on 0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)  # Run the web server after Wi-Fi connection is successful
else:
    print("Exiting: Wi-Fi connection failed.")
