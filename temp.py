import paho.mqtt.client as mqtt

client = mqtt.Client(transport="websockets")
client.connect("100.104.63.87", 8083)  # Replace with actual WS port
