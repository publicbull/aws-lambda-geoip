# coding=utf-8
from __future__ import print_function

import json
import geoip2.database
from geoip2.errors import AddressNotFoundError

import settings

import logging
logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)

LANGUAGES = ['ru', 'fr', 'en', 'de', 'zh-cn', 'pt-br', 'ja', 'es']
DEFAULT_LANGUAGE = 'en'

def lambda_handler(event, context):
    logger.debug(json.dumps(event, ensure_ascii=False, indent=2))

    ip_address = event.get('ip_address', [])
    if isinstance(ip_address, basestring):
        ip_address = [ip_address]

    lang = event.get('lang', DEFAULT_LANGUAGE).lower()
    if lang not in LANGUAGES:
        lang = DEFAULT_LANGUAGE

    reader = geoip2.database.Reader('GeoLite2-City.mmdb', [lang])

    items = []
    for ip in ip_address:
        item = {'ip_address': ip}
        try:
            response = reader.city(ip)
            item['found'] = True
            item['info'] = {
                'continent': response.continent.name,
                'country': response.country.name,
                'subdivision': response.subdivisions.most_specific.name,
                'city': response.city.name,
                'postal_code': response.postal.code,
                'location': [
                    response.location.latitude,
                    response.location.longitude,
                ],
                'time_zone': response.location.time_zone,
            }
        except AddressNotFoundError:
            item['found'] = False

        items.append(item)

    reader.close()

    logger.debug(json.dumps(items, ensure_ascii=False, indent=2))
    return {'items': items}
