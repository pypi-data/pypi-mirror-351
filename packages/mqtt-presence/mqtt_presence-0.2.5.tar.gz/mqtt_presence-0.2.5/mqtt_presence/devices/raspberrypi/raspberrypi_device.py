import logging
from typing import List

from mqtt_presence.devices.raspberrypi.raspberrypi_data import RaspberryPiSettings
from mqtt_presence.devices.raspberrypi.raspberrypi_gpio_handler import GpioHandler
from mqtt_presence.devices.device_data import DeviceData, Homeassistant, HomeassistantType
from mqtt_presence.devices.device import Device
from mqtt_presence.config.configuration import Configuration


logger = logging.getLogger(__name__)



class RaspberryPiDevice(Device):
    def __init__(self):
        super().__init__()
        self._gpio_handlers: List[GpioHandler] = []
        self.online = False


    def exit(self):
        if self.online or len(self._gpio_handlers) > 0:
            logger.info("🔴 Stopping raspberrypi device")
            for gpio in self._gpio_handlers:
                gpio.close()
            self._gpio_handlers = []


    def init(self, config: Configuration, topic_callback):
        settings: RaspberryPiSettings = config.devices.raspberryPi
        if (not settings or settings.enabled is False):
            return
        
        try:
            logger.info("🟢 Initializing raspberrypi device")

            self._gpio_handlers = []
            for gpio in settings.gpios:
                gpio_handler = GpioHandler(gpio, topic_callback)
                if gpio is not None:
                    self._gpio_handlers.append(gpio_handler)
            logger.info("🍓 Created %s gpios", len(self._gpio_handlers))

            for gpio_handler in self._gpio_handlers:
                gpio_handler.create_data(self.data)
            
            self.online = True          
        except Exception as e:
            logger.info("🔴 Raspberrypi failed: %s", e)
            self._gpio_handlers = []
            self.online = False


    def update_data(self, mqtt_online: bool = None):
        for gpio_handler in self._gpio_handlers:
            gpio_handler.update_data(self.data, mqtt_online)


    def get_gpio_handler(self, gpio_setting):
        return next((gpio for gpio in self._gpio_handlers if gpio.gpio == gpio_setting), None)

    def get_gpio_handler_by_number(self, number):
        return next((gpio for gpio in self._gpio_handlers if gpio.gpio.number== number), None)