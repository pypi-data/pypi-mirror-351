import json
import logging
import threading
from typing import List
import paho.mqtt.client as mqtt
from collections import defaultdict

from mqtt_presence.config.configuration import Configuration
from mqtt_presence.devices.device_data import DeviceData, Homeassistant, HomeassistantType
from mqtt_presence.devices.devices import Devices
from mqtt_presence.devices.device import Device

from mqtt_presence.utils import Tools

logger = logging.getLogger(__name__)


# Binary sensor for availability
AVAILABLE_SENSOR_TOPIC = "status"
AVAILABLE_STATUS_ONLINE = "online"
AVAILABLE_STATUS_OFFLINE = "offline"


class MQTTClient:
    def __init__(self, mqtt_callback):
        self._available_topic = DeviceData("Online state", data=AVAILABLE_STATUS_ONLINE, homeassistant=Homeassistant(type=HomeassistantType.BINARY_SENSOR))
        self._devices: Devices = Devices
        self._devices_data_old: dict[str, dict[str, str]] = defaultdict(dict)
        self._config: Configuration = None
        self._mqtt_callback = mqtt_callback
        self._client: mqtt = None
        self._lock = threading.RLock()
        self._discovery_prefix: str = None
        self._node_id: str = None
        self._topic_prefix: str = None
        self._published_topics : List[str] = []


    def set_devices_data(self, devices: Devices):
        self._devices = devices
        self._devices_data_old.clear()
        self._publish_available(AVAILABLE_STATUS_ONLINE)



    def handle_action(self, topic, function):
        publish_topic = f"{self._topic_prefix}/{topic}/action"
        logger.info("🚀 Publish: %s: %s", publish_topic, function)
        self._client.publish(publish_topic, payload=function, retain=True)


    def connect(self, config: Configuration, password: str):
        with self._lock:
            self._config = config
            # mqtt data
            self._node_id = self._config.mqtt.broker.client_id           #   self._config.mqtt.broker.prefix.replace("/", "_")
            self._discovery_prefix = self._config.mqtt.homeassistant.discovery_prefix
            self._topic_prefix = self._config.mqtt.broker.prefix            

            try:
                logger.info("🚪 Starting MQTT for %s on %s:%d",
                            self._node_id,
                            self._config.mqtt.broker.host,
                            self._config.mqtt.broker.port)

                self._create_client(self._node_id, password)
                self._client.connect(
                    self._config.mqtt.broker.host,
                    self._config.mqtt.broker.port,
                    self._config.mqtt.broker.keepalive
                )
                self._client.loop_start()
            except Exception as e: # pylint: disable=broad-exception-caught
                logger.warning("❌ MQTT connection failed: %s", e)
                self.disconnect()


    def is_connected(self):
        return False if self._client is None else self._client.is_connected()


    def disconnect(self):
        with self._lock:
            if self._client is not None:
                if self.is_connected():
                    logger.info("🚪 Stopping mqtt...")
                    self._publish_available("offline")
                self._client.loop_stop()
                self._client.disconnect()
                self._devices_data = Devices()
                self._devices_data_old.clear()
                self._client = None




    def publish_mqtt_data(self, force: bool = False):
        with self._lock: 
            for device_key, device in self._devices.devices.items():
                for data_key, device_data in device.data.items():
                    component = device_data.homeassistant.type if device_data.homeassistant else None
                    if component==HomeassistantType.SENSOR or component==HomeassistantType.SWITCH or component==HomeassistantType.BINARY_SENSOR:
                        value = None
                        topic = f"{self._topic_prefix}/{device_key}/{data_key}/state"
                        try:
                            value = device_data.data
                            old_value = self._devices_data_old.get(device_key, {}).get(data_key, None)
                            if value is not None and (force or old_value is None or value != old_value):
                                self._devices_data_old[device_key][data_key] = value
                                self._client.publish(topic, payload=str(value), retain=True)
                                logger.debug("📡 Published %s: %s = %s",component.value, device_data.friendly_name, value)
                        except Exception as exception:      # pylint: disable=broad-exception-caught
                            logger.error("Failed to get %s data %s: %s  (%s, %s)", component.value, topic, exception, value, old_value)



    def publish_discovery(self):
        with self._lock:
            self._published_topics = []

            device_data = self._available_topic
            data_key = AVAILABLE_SENSOR_TOPIC
            component = device_data.homeassistant.type if device_data.homeassistant else None
            if (component is not None):
                discovery_topic = f"{self._discovery_prefix}/{component.value}/{self._node_id}/config"
                topic = f"{self._topic_prefix}/{data_key}"
                payload = self._get_discovery_payload(topic, data_key, device_data, component.value)
                self._client.publish(discovery_topic, json.dumps(payload), retain=True)
                self._published_topics.append(discovery_topic)
                logger.info("🧠 Discovery published for %s: %s(%s)", component.value,  data_key, device_data.friendly_name)

            for device_key, device in self._devices.devices.items():
                for data_key, device_data in device.data.items():
                    component = device_data.homeassistant.type if device_data.homeassistant else None
                    if component is not None:
                        topic = f"{self._topic_prefix}/{device_key}/{data_key}"
                        unique_id = f"{device_key}_{data_key}"
                        if device_data.homeassistant.actions is not None:
                            for action in device_data.homeassistant.actions:
                                discovery_topic = f"{self._discovery_prefix}/{component.value}/{self._node_id}/action_{unique_id}_{action}/config"
                                payload = self._get_discovery_payload(topic, unique_id, device_data, component.value)
                                payload["type"] = action
                                payload["subtype"] = f"{unique_id}_{action}"
                                payload["unique_id"] = f"{unique_id}_{action}"
                                payload["payload"] = action
                                self._client.publish(discovery_topic, json.dumps(payload), retain=True)
                                self._published_topics.append(discovery_topic)
                                logger.info("🧠 %s %s Discovery published for %s: %s", action, component.value, data_key, device_data.friendly_name)
                        else:
                            discovery_topic = f"{self._discovery_prefix}/{component.value}/{self._node_id}/{unique_id}/config"
                            payload = self._get_discovery_payload(topic, unique_id, device_data, component.value)
                            self._client.publish(discovery_topic, json.dumps(payload), retain=True)
                            self._published_topics.append(discovery_topic)
                            logger.info("🧠 Discovery published for %s: %s(%s)", component.value, data_key, device_data.friendly_name)



    def clean_discovery_topics(self, clear_all: bool = False):
        self._client.unsubscribe(f"homeassistant/+/{self._node_id}/+/config")
        # Remove all topics that are no longer in the list of actively published topics
        for topic in self._existing_discovery_topics or []:
            if clear_all or topic not in self._published_topics:
                logger.info("🧹 Removing outdated discovery topic: %s", topic)
                self._client.publish(topic, payload=None, retain=True)
            #else:
                #logger.info("✅ Keeping active discovery topic: %s", topic)




    def _on_connect(self, _client, _userdata, _flags, reason_code, _properties=None):
        if self._client.is_connected():
            logger.info("🟢 Connected to MQTT broker")
            self._mqtt_callback("on_connect")
            self._subscribe_topics()
        else:
            if reason_code.value != 0:
                reason = reason_code.name if hasattr(reason_code, "name") else str(reason_code)
                logger.error("🔴 Connection to  MQTT broker failed: %s (rc=%s)", reason, reason_code.value if hasattr(reason_code, 'value') else reason_code)
            else:
                logger.info("🔴 Connection closed")


    def _on_disconnect(self, _client, _userdata, _flags, reason_code, _properties=None):
        reason = reason_code.name if hasattr(reason_code, "name") else str(reason_code)
        logger.error("🔴 Connection to  MQTT broker closed: %s (rc=%s)", reason, reason_code.value if hasattr(reason_code, 'value') else reason_code)
        self._mqtt_callback("on_disconnect")



    def _on_message(self, _client, _userdata, msg):
        payload = msg.payload.decode().strip().lower()
                
        if msg.topic.startswith("homeassistant/") and msg.topic.endswith("/config"):
            self._existing_discovery_topics.append(msg.topic)
        else:
            topic_prefix = self._topic_prefix
            topic_without_prefix = msg.topic[len(topic_prefix)+1:] if msg.topic.startswith(topic_prefix) else topic_prefix
            logger.info("📩 Received command: %s → %s", msg.topic, payload)
            for device_key, device in self._devices.devices.items():
                for data_key, device_data in device.data.items():
                    component = device_data.homeassistant.type if device_data.homeassistant else None
                    relative_topic = f"{device_key}/{data_key}"
                    if component is not None and topic_without_prefix == f"{relative_topic}/command":
                        device_data.action(payload)
                        self._mqtt_callback("on_message_action")



    def _get_available_topic(self):
        return f"{self._topic_prefix}/{AVAILABLE_SENSOR_TOPIC}/state"



    def _subscribe_topics(self):
        self._existing_discovery_topics: List[str] = []
        self._client.subscribe(f"homeassistant/+/{self._node_id}/+/config")

        for device_key, device in self._devices.devices.items():
            for data_key, device_data in device.data.items():
                component = device_data.homeassistant.type if device_data.homeassistant else None
                relative_topic = f"{device_key}/{data_key}/command"
                if component == HomeassistantType.BUTTON or component == HomeassistantType.SWITCH:
                    self._client.subscribe(f"{self._topic_prefix}/{relative_topic}")


    def _publish_available(self, state):
        self._client.publish(self._get_available_topic(), payload=state, retain=True)
        logger.info("📡 Status publisched: %s", state)




    def _get_discovery_payload(self, topic, unique_id, device_data: DeviceData, component):
        device_info = {
            "identifiers": [self._node_id],
            "name": self._config.mqtt.homeassistant.device_name,
            "manufacturer": "mqtt-presence",
            "model": "Presence Agent"
        }
        payload = {
                "name": device_data.friendly_name,
                "availability_topic": self._get_available_topic(),
                "payload_available": "online",
                "payload_not_available": "offline",
                "unique_id": f"{self._node_id}_{unique_id}",
                "device": device_info
        }
        if device_data.homeassistant.icon is not None:
            payload["icon"] = f"mdi:{device_data.homeassistant.icon}"
        if device_data.unit is not None:
            payload["unit_of_measurement"] = device_data.unit

        if component == "button":
            payload["command_topic"] = f"{topic}/command"
            payload["payload_press"] = "press"
        elif component == "switch":
            payload["state_topic"] = f"{topic}/state"
            payload["command_topic"] = f"{topic}/command"
            payload["payload_off"] = "OFF"
            payload["payload_on"] = "ON"
        elif component == "binary_sensor":
            payload["state_topic"] = f"{topic}/state"
            payload["payload_on"] = "online"
            payload["payload_off"] = "offline"
            payload["device_class"] = "connectivity"
        elif component == "sensor":
            payload["state_topic"] = f"{topic}/state"
        elif component == "device_automation":
            payload["automation_type"] = "trigger"
            payload["topic"] = f"{topic}/action"
        return payload



    def _create_client(self, client_id, password: str):
        with self._lock:
            if self._client is not None:
                self.disconnect()
            self._client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
            # Callback-Methoden
            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message
            self._client.on_disconnect = self._on_disconnect
            # Authentifizierung
            self._client.username_pw_set(self._config.mqtt.broker.username, password)
            # "Last Will"
            self._client.will_set(self._get_available_topic(), payload="offline", retain=True)
