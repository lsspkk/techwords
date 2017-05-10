#
#Simple proof of concept code to push data to Google Analytics.
#Related blog post:
# * https://medium.com/python-programming-language/80eb9691d61f
#
from random import randint
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.parse import urlunparse
from hashlib import sha1
from os import environ
import time

def send_ga(route):
    PROPERTY_ID = "***REMOVED***"
    PATH = route

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
            "utmcc": "__utma=%s;" % ".".join(["1", VISITOR, "1", "1", "1", "1"])}

    # Encode this data and generate the final URL
    URL = urlunparse(("http",
                      "www.google-analytics.com",
                      "/__utm.gif",
                      "",
                      urlencode(DATA),
                      ""))

    # Make the request
    print ("Requesting", URL)
    print (urlopen(URL).info())

if __name__ == '__main__':
    send_ga("/")
