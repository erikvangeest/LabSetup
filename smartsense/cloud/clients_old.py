# Standard library imports


# Third party imports
import paho.mqtt.client as mqtt
from elasticsearch import Elasticsearch

# Project imports

BROKER_IP = 'lionite-server'
BROKER_PORT = 1883

class MQTTClient():
    def __init__(self, ebox_id, logger=None) -> None:
        self.logger = logger
        self.EBOX_ID = ebox_id
        self.init_mqtt()


    def init_mqtt(self):
        self.client = mqtt.Client(client_id=self.EBOX_ID)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def connect(self):
        self.client.connect(BROKER_IP, BROKER_PORT, 60)
        if self.logger:
            self.logger.success(f"Connected to broker at {BROKER_IP}:{BROKER_PORT}")

    def upload(self, frame):
        self.client.publish(f"smartcloud/{self.EBOX_ID}/data", frame)
        if self.logger:
            self.logger.info(f"Uploaded frame to {BROKER_IP}:{BROKER_PORT}")

    def disconnect(self):
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if self.logger:
            self.logger.success(f"Connected to broker at {BROKER_IP}:{BROKER_PORT}")

    def on_disconnect(self, client, userdata, rc):
        if self.logger:
            self.logger.warning(f"Disconnected from {BROKER_IP}:{BROKER_PORT}")

def get_data(start, end, size=100):
    # Connect to Elasticsearch
    es = Elasticsearch("http://192.168.193.1:9200")

    # Define the query
    query = {
        "query": {
            "range": {
                "@timestamp": {
                    "gte": start,
                    "lte": end
                }
            }
        },
        "size": size,
    }

    # Replace 'your_index_name' with the name of your actual index
    response = es.search(index="smartcloud-data", body=query)

    print(response["hits"]["total"]["value"])
    measurements = []
    for hit in response['hits']['hits']:
        measurements.append(hit["_source"])
    # Print the response

    return measurements


if __name__ == "__main__":
    data = get_data("2024-02-16T00:00:00Z", "2024-02-16T23:59:59Z")