import compool.api
import logging

from homeassistant.components.switch import SwitchDevice

_LOGGER = logging.getLogger(__name__)

DOMAIN = "compool"

def setup_platform(hass, config, add_devices, discovery_info=None):
    device = hass.data[DOMAIN]
    equipment = discovery_info['equipment']
    add_devices([CompoolPrimaryEquipment(device, name, num) for num, name in equipment.items()])

class CompoolPrimaryEquipment(SwitchDevice):
    def __init__(self, device, name, number):
        self.device = device
        self._name = name
        self.number = number
        self.device.update_callbacks.append(self.update)

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return None

    @property
    def assumed_state(self):
        return False

    @property
    def is_on(self):
        if self.number<2 and self.device.state.is_delay_on(self.number):
            return False
        return self.device.state.is_primary_equipment_on(self.number)

    def turn_on(self, **kwargs):
        self.device.set_primary_equipment_state(self.number, True)        

    def turn_off(self, **kwargs):
        self.device.set_primary_equipment_state(self.number, False)

    def update(self, old):
        if old.is_primary_equipment_on(self.number)!=self.device.state.is_primary_equipment_on(self.number):       
            self.schedule_update_ha_state()
        elif self.number < 2 and old.is_delay_on(self.number)!=self.device.state.is_delay_on(self.number):
            self.schedule_update_ha_state()
