#
#https://cloud.google.com/appengine/docs/standard/python/google-analytics
#https://developers.google.com/analytics/devguides/collection/protocol/v1/devguide
#
from random import randint
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.parse import urlunparse
from urllib.parse import urlparse
from hashlib import sha1
from os import environ
import time
import logging
from flask import request

logger1 = logging.getLogger('google_analytics')


def send_ga(request):
    PROPERTY_ID = "***REMOVED***"
    data = {
        'v': '1',  # API Version.
        'tid': PROPERTY_ID,  # Tracking ID / Property ID.
        # Anonymous Client Identifier. Ideally, this should be a UUID that
        # is associated with particular user, device, or browser instance.
        'cid': '46601a07-d6a8-40a9-a941-29742f15e857', # just some id 
        't': 'pageview',  # Event hit type.
        'dh': 'xn--hyty-6qa.net',  # Event category.
        'dp': request.path,  # Event action.
        'uip': request.remote_addr
    }

    r = Request('http://www.google-analytics.com', data=urlencode(data).encode())
    logger1.info( "Request posted to GA")
    logger1.info(str(data))
    logger1.info(urlopen(r).info())

if __name__ == '__main__':
    send_ga("/")
