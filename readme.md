# API from TE-Keskus job advertisements

Coders sought in Tampere region

See how to use from the examples-folder

      /trends
      with daily amounts of different technologies employees want


      /techwords
      (todo you can change and update these with APIkey)


      /advertisements
      just to see the new and history


      /matchresult/ad-id/
      to see techword match result on single advertisement



# Swagger docs
To see swagger UI docs, run the API and open with browser http://localhost:9090/apidocs


## Get the Data

What a nice URL we use:

http://www.mol.fi/tyopaikat/tyopaikkatiedotus/ws/tyopaikat?lang=fi&hakusana=&hakusanakentta=sanahaku&alueet=pirkanmaa&ilmoitettuPvm=1&valitutAmmattialat=25&vuokrapaikka=---&start=0&kentat=ilmoitusnumero,tyokokemusammattikoodi,ammattiLevel3,tehtavanimi,tyokokemusammatti,tyonantajanNimi,kunta,ilmoituspaivamaara,hakuPaattyy,tyoaikatekstiYhdistetty,tyonKestoKoodi,tyonKesto,tyonKestoTekstiYhdistetty,hakemusOsoitetaan,maakunta,maa,hakuTyosuhdetyyppikoodi,hakuTyoaikakoodi,hakuTyonKestoKoodi&rows=300&sort=mainAmmattiRivino+asc,+tehtavanimi+asc,+tyonantajanNimi+asc,+viimeinenHakupaivamaara+asc&facet.fkentat=ammattiLevel3,maakunta,kunta,maa,hakuTyosuhdetyyppikoodi,hakuTyoaikakoodi,hakuTyonKestoKoodi&facet.fsort=index&facet.flimit=10000&_=1488917769087


### Set up and update data
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

Test it with web server, use the html files from examples-folder
