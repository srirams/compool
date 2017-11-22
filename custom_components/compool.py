import compool.api
import logging

import voluptuous as vol

from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

DOMAIN = "compool"

def setup(hass, config):
    conf = config.get(DOMAIN)
    device = compool.api.CompoolAPI(conf.get('port'))
    hass.data[DOMAIN] = device
    discovery.load_platform(hass, 'switch', DOMAIN, {'equipment': conf.get('equipment')}, config)
    discovery.load_platform(hass, 'climate', DOMAIN, {}, config)
    discovery.load_platform(hass, 'sensor', DOMAIN, {}, config)
    return True