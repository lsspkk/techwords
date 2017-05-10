# -*- coding: UTF-8 -*-
import urllib.parse
from urllib.request import Request, urlopen
from manger.py import PROPERTY_ID

d = {'dp': '/api/v1/trends',
     'dh': 'hyöty.net',
     't': 'pageview',
     'v': '1',
     'tid': PROPERTY_ID,
     'cid': '46601a07-d6a8-40a9-a941-29742f15e857',
     'uip': '85.76.105.38'}
a = urllib.parse.urlencode(d).encode()
b = Request('http://www.google-analytics.com/collect', a)

print(urlopen(b).read().decode())
