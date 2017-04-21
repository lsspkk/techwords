#!/usr/bin/python
import sys, urllib2, json, io, datetime, calendar, os

import models

dir_path = os.path.dirname(os.path.realpath(__file__))

tech_file =  dir_path+'/data/techwords.json'
ads_file =  dir_path+'/data/bar.json'
ads_filtered_file =  dir_path+'/data/bar_filtered.json'
database_file = 'sqlite:///data/foo.db'

# coders from Pirkanmaa area
scrape_url = "http://www.mol.fi/tyopaikat/tyopaikkatiedotus/ws/tyopaikat?lang=fi&hakusana=&hakusanakentta=sanahaku&alueet=pirkanmaa&ilmoitettuPvm=1&valitutAmmattialat=25&vuokrapaikka=---&start=0&kentat=ilmoitusnumero,tyokokemusammattikoodi,ammattiLevel3,tehtavanimi,tyokokemusammatti,tyonantajanNimi,kunta,ilmoituspaivamaara,hakuPaattyy,tyoaikatekstiYhdistetty,tyonKestoKoodi,tyonKesto,tyonKestoTekstiYhdistetty,hakemusOsoitetaan,maakunta,maa,hakuTyosuhdetyyppikoodi,hakuTyoaikakoodi,hakuTyonKestoKoodi&rows=300&sort=mainAmmattiRivino+asc,+tehtavanimi+asc,+tyonantajanNimi+asc,+viimeinenHakupaivamaara+asc&facet.fkentat=ammattiLevel3,maakunta,kunta,maa,hakuTyosuhdetyyppikoodi,hakuTyoaikakoodi,hakuTyonKestoKoodi&facet.fsort=index&facet.flimit=10000&_=1488917769087"


def print_info():
    print """
    manage data download_advertisements
          - get new advertisements from internet
            write json to %s""" % ads_file
    print """
    manage_data filter_advertisements
         - make the advertisements ready for our database:
           read json from %s
           and write to %s""" % (ads_file, ads_filtered_file)
    print """
    manage_data init_database_advertisements
          - init the advertisements in database
            read json from %s

    manage_data init_database_techwords
          - init the techwords in database
            read json from %s

    manage_data update_database
          - find techwords from advertisements
          """ %(ads_filtered_file, tech_file)



def download_advertisements():
    ads = {}
    try:
        with open(ads_file) as data_file:
            ads = json.load(data_file)
    except:
        print "no ads file, making a new one: %s" % file_name

    r = urllib2.urlopen(scrape_url)
    j = json.loads(r.read())

    print( "Ilmoituksia tunnetaan: %s kpl" % (len(ads.keys())))
    print( "Ilmoituksia netissa: %s kpl" % (j["response"]["numFound"]))

    timestamp = datetime.datetime.now().isoformat()
    for tag in j["response"]["docs"]:
        if unicode(tag['ilmoitusnumero']) in ads:
            print "Tunnettiin jo ilmoitus %s" % (tag['ilmoitusnumero'])
        else:
            print (str(tag['ilmoitusnumero']) + " " + tag['tehtavanimi'])
            url = "http://www.mol.fi/tyopaikat/tyopaikkatiedotus/ws/tyopaikat/" + str(tag['ilmoitusnumero'])
            r = urllib2.urlopen(url)
            j2 = json.loads(r.read())
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
        print "no file for ads: %s" % ads_file

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
        print "no file for techwords: %s" % tech_file

    return words


def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.datetime(year,month,day,sourcedate.hour,sourcedate.minute)



def pretty_advertisements():
    try:
        with open(ads_file) as data_file:
            ads = json.load(data_file)
        parts = os.path.split(ads_file)
        file_name2 =  parts[0]+ "/bar_pretty.json"
        with io.open( file_name2, "w", encoding="utf-8") as f:
            f.write(json.dumps(ads, indent=4, sort_keys=True, ensure_ascii=False))
    except:
        print "no file: %s" % ads_file






if __name__ == '__main__':
    if len(sys.argv) == 1:
        print_info()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'download_advertisements':
            download_advertisements()

        elif command == 'filter_advertisements':
            filter_advertisements()

        elif command == 'init_database_advertisements':
            models.init_advertisements()

        elif command == 'init_database_techwords':
            models.init_techwords()

        elif command == 'update_database':
            models.update_database()

        elif command == 'pretty':
            pretty_advertisements()

        else:
            print "Bad parameter"
            print_info()
