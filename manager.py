#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys, urllib, json, io, datetime, calendar, os
import urllib.request
import logging
from logging.handlers import RotatingFileHandler

dir_path = os.path.dirname(os.path.realpath(__file__))

default_host = '0.0.0.0' # 0.0.0.0 = localhost  - where API is run
default_port = 9090 # the port where API is run

logging.basicConfig(handlers=[RotatingFileHandler(dir_path+'nice.log',maxBytes=200000,backupCount=5)], level=logging.DEBUG)

tech_file =  dir_path+'/data/techwords.json'
ads_file =  dir_path+'/data/bar.json'
ads_filtered_file =  dir_path+'/data/bar_filtered.json'
database_file = 'sqlite:///'+ dir_path + '/data/foo.db'

# coders from Pirkanmaa area
scrape_url = "http://www.mol.fi/tyopaikat/tyopaikkatiedotus/ws/tyopaikat?lang=fi&hakusana=&hakusanakentta=sanahaku&alueet=pirkanmaa&ilmoitettuPvm=1&valitutAmmattialat=25&vuokrapaikka=---&start=0&kentat=ilmoitusnumero,tyokokemusammattikoodi,ammattiLevel3,tehtavanimi,tyokokemusammatti,tyonantajanNimi,kunta,ilmoituspaivamaara,hakuPaattyy,tyoaikatekstiYhdistetty,tyonKestoKoodi,tyonKesto,tyonKestoTekstiYhdistetty,hakemusOsoitetaan,maakunta,maa,hakuTyosuhdetyyppikoodi,hakuTyoaikakoodi,hakuTyonKestoKoodi&rows=300&sort=mainAmmattiRivino+asc,+tehtavanimi+asc,+tyonantajanNimi+asc,+viimeinenHakupaivamaara+asc&facet.fkentat=ammattiLevel3,maakunta,kunta,maa,hakuTyosuhdetyyppikoodi,hakuTyoaikakoodi,hakuTyonKestoKoodi&facet.fsort=index&facet.flimit=10000&_=1488917769087"






global swagger_template
swagger_template = {
  "swagger": "2.0",
  "info": {
    "title": "TechWords API",
    "description": "API for technology words used in job advertisements of Pirkanmaa region",
    "contact": {
      "responsibleOrganization": "lvp",
      "responsibleDeveloper": "lvp",
      "email": "lspkk@gmail.com",
      #"url": "www.hyöty.net",
    },
    "termsOfService": "http://me.com/terms",
    "version": "1.0.0"
  },
  #"host": "localhost:9090",  # overrides localhost:500
  #"basePath": "/api/v1",  # base bash for blueprint registration
  "schemes": [
    [
      "http",
#      "https"
    ]
  ],
  "operationId": "getmyData"
}









import models

def download_advertisements():
    ads = {}
    try:
        with open(ads_file) as data_file:
            ads = json.load(data_file)
    except:
        print ("no ads file, making a new one: %s" % file_name)

    r = urllib.request.urlopen(scrape_url)
    j = json.loads(r.read().decode('utf-8'))

    print( "Ilmoituksia tunnetaan: %s kpl" % (len(ads.keys())))
    print( "Ilmoituksia netissa: %s kpl" % (j["response"]["numFound"]))

    timestamp = datetime.datetime.now().isoformat()
    for tag in j["response"]["docs"]:
        if str(tag['ilmoitusnumero']) in ads:
            print ("Tunnettiin jo ilmoitus %s" % (tag['ilmoitusnumero']))
        else:
            print ((str(tag['ilmoitusnumero']) + " " + tag['tehtavanimi']))
            url = "http://www.mol.fi/tyopaikat/tyopaikkatiedotus/ws/tyopaikat/" + str(tag['ilmoitusnumero'])
            r = urllib.request.urlopen(url)
            j2 = json.loads(r.read().decode('utf-8'))
            ads[tag['ilmoitusnumero']] = {
                "lukupvm" : timestamp,
                "ilmoitus": j2["response"]["docs"][0]
                }

    with io.open( ads_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(ads, ensure_ascii=False))



def filter_advertisements():
    ads = {}
    try:
        with open(ads_file) as data_file:
            ads = json.load(data_file)
    except:
        print ("no file for ads: %s" % ads_file)

    r = []
    for tag in ads:
        start =  datetime.datetime.strptime( ads[tag]['ilmoitus']['ilmoituspaivamaara'], "%Y-%m-%dT%H:%M:%SZ")
        try:
            d = ads[tag]['ilmoitus']['hakuPaattyy']
            if "klo" in d:
                end = datetime.datetime.strptime( d, "%d.%m.%Y klo %H:%M")
            else:
                end = datetime.datetime.strptime( d, "%d.%m.%Y")
        except KeyError:
            end = add_months(start,1)

        j = {}
        j['start_date'] = start.isoformat()
        j['end_date'] = end.isoformat()
        j['title'] = ads[tag]['ilmoitus']['otsikko']
        j['job'] = ads[tag]['ilmoitus']['tehtavanimi']
        j['text'] = ads[tag]['ilmoitus']['kuvausteksti']
        j['id'] = ads[tag]['ilmoitus']['ilmoitusnumero']
        r.append(j)

    with io.open( ads_filtered_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(r, indent=4, sort_keys=False, ensure_ascii=False))


def get_advertisements():
    ads = {}
    try:
        with open(ads_filtered_file) as data_file:
            ads = json.load(data_file)
    except:
        ads = {}
    return ads


def get_techwords():
    words = {}
    try:
        with open(tech_file) as data_file:
            words = json.load(data_file)
    except:
        print ("no file for techwords: %s" % tech_file)

    return words


def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.datetime(year,month,day,sourcedate.hour,sourcedate.minute)



def pretty_ads():
    try:
        with open(ads_file) as data_file:
            ads = json.load(data_file)
        parts = os.path.split(ads_file)
        file_name2 =  parts[0]+ "/bar_pretty.json"
        with io.open( file_name2, "w", encoding="utf-8") as f:
            f.write(json.dumps(ads, indent=4, sort_keys=True, ensure_ascii=False))
    except:
        print ("no file: %s" % ads_file)



def print_info():
    print ("""
    ./manager.py download_ads
          - get new advertisements from internet
            write json to %s""" % ads_file)
    print ("""
    ./manager.py filter_ads
         - make the advertisements ready for our database:
           read json from %s
           and write to %s""" % (ads_file, ads_filtered_file))
    print ("""
    ./manager.py db_init_ads
          - clear and add the advertisements into database
            read json from %s

    ./manager.py db_init_techwords
          - clear and add the techwords into database
            read json from %s

    ./manager.py db_update
          - add new advertisements (that are not already) into database
          - find techwords from advertisements
          """ %(ads_filtered_file, tech_file))



if __name__ == '__main__':
    if len(sys.argv) == 1:
        print_info()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'download_ads':
            download_advertisements()

        elif command == 'filter_ads':
            filter_advertisements()

        elif command == 'db_init_ads':
            models.init_ads()

        elif command == 'db_init_techwords':
            models.init_techwords()

        elif command == 'db_update':
            models.update_database()

        elif command == 'pretty':
            pretty_ads()

        else:
            print ("Bad parameter")
            print_info()
