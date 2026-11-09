from elasticsearch import Elasticsearch
import json
from datetime import datetime
from datetime import datetime
import pytz

BROKER_IP = '100.104.63.87'  # Elasticsearch IP
BROKER_PORT = 9200           # not used, but retained for structure
ELASTIC_INDEX = 'smartcloud-storage'  # Elasticsearch index name
ELASTIC_USERNAME = 'smartsense'  # leave None if no auth
ELASTIC_PASSWORD = '6Bi5em&#Ph%1*r'

class MQTTClient():
    def __init__(self, ebox_id, logger=None) -> None:
        self.logger = logger
        self.EBOX_ID = ebox_id
        self.index = ELASTIC_INDEX

        # Connect to Elasticsearch
        if ELASTIC_USERNAME and ELASTIC_PASSWORD:
            self.client = Elasticsearch(
                f"http://{BROKER_IP}:{BROKER_PORT}",
                basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
            )
        else:
            self.client = Elasticsearch(f"http://{BROKER_IP}:{BROKER_PORT}")

    def connect(self):
        if self.logger:
            self.logger.success(f"Connected to Elasticsearch at {BROKER_IP}:{BROKER_PORT}")

    def upload(self, frame):
        try:
            if isinstance(frame, str):
                frame = json.loads(frame)

            # Add timestamp if missing
            if "@timestamp" not in frame:
                # Use Amsterdam timezone for timestamp
                ams_tz = pytz.timezone("Europe/Amsterdam")
                frame["@timestamp"] = datetime.now(ams_tz).isoformat()

            result = self.client.index(index=self.index, document=frame)
            if self.logger:
                self.logger.info(f"Uploaded frame to Elasticsearch: {result['_id']}")
        except Exception as e:
            print(f"Failed to upload to Elasticsearch: {e}")

    def disconnect(self):
        if self.logger:
            self.logger.info(f"Disconnected from Elasticsearch at {BROKER_IP}:{BROKER_PORT}")
