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


## scrape data, and filter out the stuff we dont need

    ./manage_data.py.py download_advertisements
    ./manage_data.py filter_advertisements

## set up the database


    ./manage_data.py init_database_advertisements
    ./manage_data.py init_database_techwords
    ./manage_data.py update_database



## put these to cron
If you want to keep database up to date automatically
    ./manage_data.py.py download_advertisements
    ./manage_data.py filter_advertisements
    ./manage_data.py update_database





# Better server for Flask

wsgi for apache



uwsgi for nginx
      pip install uwsgi

uwsgi --http :9090 --wsgi-file api.py
