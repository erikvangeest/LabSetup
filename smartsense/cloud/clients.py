# ebox_mqtt_aws.py
import json
import ssl
import time
from collections import deque
from typing import Union
import paho.mqtt.client as mqtt

# ========= KEEPING YOUR SETTINGS =========
AWS_ENDPOINT = "a3b8gmog7fe5vl-ats.iot.eu-north-1.amazonaws.com"
AWS_PORT = 8883
AWS_CA = r"C:\Users\smart\Scripts\AmazonRootCA1.pem"
AWS_CERT = r"C:\Users\smart\Scripts\0cb6d58897ab2228f592cc5c0667b8b11233824d166ad10ee3a62ad63b955d81-certificate.pem.crt"
AWS_KEY = r"C:\Users\smart\Scripts\0cb6d58897ab2228f592cc5c0667b8b11233824d166ad10ee3a62ad63b955d81-private.pem.key"
TOPIC_TEMPLATE = "sensors/ethylene/{ebox_id}/frames"
KEEPALIVE = 60
# ========================================

# Reliability toggles
QOS = 1                     # PUBACK reliability
USE_PORT_443_ALPN = False   # set True if 8883 is blocked/flaky

class MQTTClient:
    """
    Same API:
      MQTTClient(ebox_id, logger=None)
      connect()
      upload(frame_json_or_dict)
      disconnect()
    Now with QoS1, retry, queue flush, and extensive logging.
    """

    def __init__(self, ebox_id: str, logger=None) -> None:
        self.logger = logger
        self.EBOX_ID = ebox_id
        self._topic = TOPIC_TEMPLATE.format(ebox_id=self.EBOX_ID)
        self._connected = False
        self._port = AWS_PORT
        self._pending = deque()  # payloads waiting to send
        self._init_client()

    def _log(self, level: str, msg: str):
        """Central log helper: logs to provided logger or prints."""
        if self.logger:
            if hasattr(self.logger, level):
                getattr(self.logger, level)(msg)
            else:
                self.logger.info(msg)
        else:
            print(f"[{level.upper()}] {msg}", flush=True)

    def _init_client(self):
        self._log("info", f"Initializing MQTT client for EBOX_ID={self.EBOX_ID}")
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.EBOX_ID, clean_session=True)
            self._log("debug", "Using Paho MQTT Callback API v2")
        except Exception:
            self.client = mqtt.Client(client_id=self.EBOX_ID, clean_session=True)
            self._log("warning", "Falling back to Paho MQTT Callback API v1")

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        # TLS context
        if USE_PORT_443_ALPN:
            self._log("info", "Setting up TLS for port 443 + ALPN")
            ctx = ssl.create_default_context()
            ctx.load_verify_locations(AWS_CA)
            ctx.load_cert_chain(certfile=AWS_CERT, keyfile=AWS_KEY)
            ctx.set_alpn_protocols(["x-amzn-mqtt-ca"])
            self.client.tls_set_context(ctx)
            self._port = 443
        else:
            self._log("info", "Setting up TLS for port 8883")
            self.client.tls_set(
                ca_certs=AWS_CA,
                certfile=AWS_CERT,
                keyfile=AWS_KEY,
                tls_version=ssl.PROTOCOL_TLS_CLIENT,
            )
            self._port = AWS_PORT

        # Robustness settings
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        self.client.max_inflight_messages_set(40)
        self.client.max_queued_messages_set(10000)
        try:
            self.client.queue_qos0_messages(True)
        except Exception:
            pass

    # ---------------- Public API ----------------
    def connect(self):
        if self._connected:
            self._log("debug", "connect() called but already connected")
            return
        self._log("info", f"Connecting to AWS IoT {AWS_ENDPOINT}:{self._port}")
        self.client.loop_start()  # ← FIXED: loop_start() now BEFORE connect()
        self.client.connect(AWS_ENDPOINT, self._port, keepalive=KEEPALIVE)

    def upload(self, frame: Union[str, dict]):
        payload = json.dumps(frame, separators=(",", ":")) if isinstance(frame, dict) else str(frame)
        self._log("debug", f"Preparing to publish payload size={len(payload)} bytes to topic={self._topic}")

        if not self._connected:
            self._log("warning", "Not connected: queuing message and forcing reconnect")
            self._pending.append(payload)
            self._try_reconnect()  # ← FIXED: actively try to reconnect instead of just queuing
            return

        for attempt in (1, 2):
            self._log("debug", f"Publish attempt {attempt} (QoS={QOS})")
            info = self.client.publish(self._topic, payload, qos=QOS)
            if info.rc == mqtt.MQTT_ERR_SUCCESS:
                self._log("debug", f"Publish rc=SUCCESS, mid={info.mid}, waiting for PUBACK")
                info.wait_for_publish(timeout=3.0)
                if info.is_published():
                    self._log("info", f"Frame published successfully (mid={info.mid})")
                    self._flush_pending()
                    return
                else:
                    self._log("warning", f"Publish attempt {attempt} timed out waiting for PUBACK")
            else:
                self._log("warning", f"Publish attempt {attempt} failed rc={info.rc}")
            time.sleep(0.25)

        self._log("error", "All publish attempts failed: message queued for retry")
        self._pending.append(payload)

    def disconnect(self):
        self._log("info", "Disconnecting from AWS IoT")
        try:
            self.client.loop_stop()
        except Exception:
            pass
        self.client.disconnect()

    # ---------------- Internal helpers ----------------
    def _try_reconnect(self):
        """Force a reconnect attempt if the loop is running but we're disconnected."""
        try:
            self._log("info", "Attempting forced reconnect...")
            self.client.reconnect()
        except Exception as e:
            self._log("warning", f"Reconnect attempt failed: {e} — will rely on auto-reconnect")

    def _flush_pending(self):
        if not self._pending:
            self._log("debug", "No queued messages to flush")
            return
        self._log("info", f"Flushing {len(self._pending)} queued message(s)")
        while self._pending and self._connected:
            p = self._pending[0]
            info = self.client.publish(self._topic, p, qos=QOS)
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                self._log("warning", f"Flush failed rc={info.rc}, stopping flush")
                break
            info.wait_for_publish(timeout=3.0)
            if info.is_published():
                self._log("info", f"Flushed queued message (mid={info.mid})")
                self._pending.popleft()
            else:
                self._log("warning", f"Flush publish timed out (mid={info.mid}), will retry later")
                break
        if self._pending:
            self._log("warning", f"{len(self._pending)} message(s) remain queued")

    # ---------------- Callbacks ----------------
    def on_connect(self, client, userdata, flags, rc, properties=None):
        self._connected = (rc == 0)
        if rc == 0:
            self._log("success", f"Connected to AWS IoT. Submitting queued messages if any.")
            self._flush_pending()
        else:
            self._log("error", f"Connection failed with rc={rc}")

    def on_disconnect(self, client, userdata, disconnect_flags, rc, properties=None):
        self._connected = False
        if rc == 0:
            self._log("info", "Clean disconnect from AWS IoT")
        else:
            self._log("warning", f"Unexpected disconnect rc={rc}, auto-reconnect will run")