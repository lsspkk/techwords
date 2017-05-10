#
#Simple proof of concept code to push data to Google Analytics.
#Related blog post:
# * https://medium.com/python-programming-language/80eb9691d61f
# https://developers.google.com/analytics/resources/concepts/gaConceptsTrackingOverview
from random import randint
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.parse import urlunparse
from urllib.parse import urlparse
from hashlib import sha1
from os import environ
import time
import logging
from flask import request
from manager import PROPERTY_ID

logger1 = logging.getLogger('google_analytics')


def send_ga(request):
    PATH = request.path

    # Generate the visitor identifier somehow. I get it from the
    # environment, calculate the SHA1 sum of it, convert this from base 16
    # to base 10 and get first 10 digits of this number.
    #VISITOR = environ.get("GA_VISITOR", "xxxxx")
    #VISITOR = str(int("0x%s" % sha1(VISITOR).hexdigest(), 0))[:10]
    VISITOR = str(int("0x%s" % sha1("api user".encode('utf-8')).hexdigest(), 0))[:10]

    # Collect everything in a dictionary
    DATA = {"utmwv": "5.2.2d",
            "utmn": str(randint(1, 9999999999)),
            "utmp": PATH,
            "utmac": PROPERTY_ID,
            "utmhn": urlparse(request.url).hostname,
            "utmcc": "__utma=%s;" % ".".join(["1", VISITOR, "1", "1", "1", "1"])}

    if request.remote_addr:
        DATA['utmr'] = request.remote_addr
        logger1.info("remote addr: %s" % request.remote_addr)

    # Encode this data and generate the final URL
    URL = urlunparse(("http",
                      "www.google-analytics.com",
                      "/__utm.gif",
                      "",
                      urlencode(DATA),
                      ""))

    # Make the request
    logger1.info( "Requesting \n %s" % URL)
    logger1.info(urlopen(URL).info())
