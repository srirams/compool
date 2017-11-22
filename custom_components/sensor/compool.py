import compool.api
import logging

from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT, ATTR_TEMPERATURE
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "compool"

def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    device = hass.data[DOMAIN]
    add_devices_callback([
        PoolPumpSensor(device),
        HeaterSensor(device),
        AirTemperatureSensor(device)
    ])

class PoolPumpSensor(Entity):
    def __init__(self, device):
        self.device = device
        self.device.update_callbacks.append(self.update)

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return "Pool Pump"

    @property
    def state(self):
        if self.device.state.is_delayed():
            return "delay"
        elif self.device.state.is_pump_on():
            return "on"
        else:
            return "off"
            
    def update(self, old):
        if old.is_delayed() != self.device.state.is_delayed():
            self.schedule_update_ha_state()
        elif old.is_pump_on() != self.device.state.is_pump_on():
            self.schedule_update_ha_state()

class HeaterSensor(Entity):
    def __init__(self, device):
        self.device = device
        self.device.update_callbacks.append(self.update)

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return "Heater"

    @property
    def state(self):
        return "on" if self.device.state.is_heater_on() else "off"

    def update(self, old):
        if old.is_heater_on() != self.device.state.is_heater_on():
            self.schedule_update_ha_state()
            
class AirTemperatureSensor(Entity):
    def __init__(self, device):
        self.device = device
        self.device.update_callbacks.append(self.update)

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return "Air Temp"

    @property
    def state(self):
        return self.device.state.get_air_temp()
        
    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS       

    def update(self, old):
        if old.get_air_temp() != self.device.state.get_air_temp():
            self.schedule_update_ha_state()    
            
