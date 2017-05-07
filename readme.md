# TechWords API

REST API about coders sought in Pirkanmaa region:
Provides data about different technologies (tech words) that employers seek.

Done with Python3 and Flask microframework

(todo  APIkey registration and )


# Docs and Demo
API docs of demo site: https://hyöty.net/techwords/apidocs
If you clone the repository and run flask, docs are found at http://localhost:9090/apidocs

TechWords demo: https://hyöty.net/techwords/examples/trends.html
Search ads demo: https://hyöty.net/techwords/examples/advertisements.html

See examples folder


## Data acquirement

To scrape the data for this app, we use URL that targets Pirkanmaa region,
and vocational target 25.

URL is rather long:

http://www.mol.fi/tyopaikat/tyopaikkatiedotus/ws/tyopaikat?lang=fi&hakusana=&hakusanakentta=sanahaku&alueet=pirkanmaa&ilmoitettuPvm=1&valitutAmmattialat=25&vuokrapaikka=---&start=0&kentat=ilmoitusnumero,tyokokemusammattikoodi,ammattiLevel3,tehtavanimi,tyokokemusammatti,tyonantajanNimi,kunta,ilmoituspaivamaara,hakuPaattyy,tyoaikatekstiYhdistetty,tyonKestoKoodi,tyonKesto,tyonKestoTekstiYhdistetty,hakemusOsoitetaan,maakunta,maa,hakuTyosuhdetyyppikoodi,hakuTyoaikakoodi,hakuTyonKestoKoodi&rows=300&sort=mainAmmattiRivino+asc,+tehtavanimi+asc,+tyonantajanNimi+asc,+viimeinenHakupaivamaara+asc&facet.fkentat=ammattiLevel3,maakunta,kunta,maa,hakuTyosuhdetyyppikoodi,hakuTyoaikakoodi,hakuTyonKestoKoodi&facet.fsort=index&facet.flimit=10000&_=1488917769087


## Set up and update API data
With python code files, you can set up and update the API data with following commands.



Scrape data, and filter out the stuff we dont need

    ./manager.py download_ads
    ./manager.py filter_ads

Use these commands to setup database for the API

    ./manager.py db_init_ads
    ./manager.py db_init_techwords


This command searches job advertisements for techwords, and stores results to database
    ./manager.py update_database



If you want to keep database up to date automatically put these to cron

       ./manager.py download_ads
       ./manager.py filter_ads
       ./manager.py update_database




# Run the API
Start the api

        ./api.py

You can also wsgi -setup for your web server. Here's Apache2 SSL example,
where techwords is run from the /home/user/techwords -directory.
These lines are from /etc/apache2/sites-available/000-default-ssl.conf

       # wsgi setup
       WSGIDaemonProcess techwords python-path=/home/user/techwords lang='fi_FI.UTF-8' locale='fi_FI.UTF-8'
       WSGIScriptAlias /techwords /home/user/techwords/wsgi.py
       <Directory /home/lvp/techwords/>
         WSGIProcessGroup techwords
         WSGIApplicationGroup %{GLOBAL}
         <Files wsgi.py>
           Require all granted
         </Files>
       </Directory>

      # static files
      Alias /techwords/examples /home/user/techwords/examples
      <Directory /home/user/techwords/examples>
          Require all granted
      </Directory>

 
