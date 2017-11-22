import compool.api
import logging

from homeassistant.components.climate import (
    ClimateDevice, ATTR_TARGET_TEMP_HIGH, ATTR_TARGET_TEMP_LOW)
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT, ATTR_TEMPERATURE

_LOGGER = logging.getLogger(__name__)

DOMAIN = "compool"

def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    device = hass.data[DOMAIN]
    add_devices_callback([
        CompoolHeater(device),
    ])

class CompoolHeater(ClimateDevice):

    def __init__(self, device):
        self.device = device
        self.device.update_callbacks.append(self.update)

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return "Pool Heater"

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        return self.device.state.get_water_temp()

    @property
    def target_temperature(self):
        return self.device.state.get_desired_spa_temp()

    @property
    def current_operation(self):
        return 'heat' if self.device.state.is_spa_heater_mode_on() else 'off'

    @property
    def operation_list(self):
        return ['heat', 'off']

    def set_temperature(self, **kwargs):
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self.device.set_desired_spa_temp(kwargs.get(ATTR_TEMPERATURE))

    def set_operation_mode(self, operation_mode):
        self.device.set_spa_heater_mode(operation_mode=='heat')

    def update(self, old):
        if old.get_water_temp() != self.device.state.get_water_temp():
            self.schedule_update_ha_state()
        elif old.get_desired_spa_temp() != self.device.state.get_desired_spa_temp():
            self.schedule_update_ha_state()
        elif old.is_spa_heater_mode_on() != self.device.state.is_spa_heater_mode_on():
            self.schedule_update_ha_state()
        