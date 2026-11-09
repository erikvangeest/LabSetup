from smartsense.cloud.clients import MQTTClient

database = MQTTClient("EBOX_LS_09122024")  # try adding host, port if possible

try:
    print("Connecting...")
    print("MQTTClient config:", database.__dict__)
    print("Client host:", database.client._host)
    print("Client port:", database.client._port)

    database.connect()
    print("Connected!")
    database.disconnect()
except Exception as e:
    print("Connection failed:", e)
