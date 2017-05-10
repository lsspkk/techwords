#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask, abort, request, jsonify
from flask_cors import CORS, cross_origin
from flask_compress import Compress
from flasgger import Swagger
import datetime, json, time
import logging

compress = Compress()
app = Flask(__name__)jed
compress.init_app(app)

import manager
from manager import PROPERTY_ID

import models, controllers, utils
from utils import measure_time
from google-analytics2 import send_ga

app.config['SWAGGER'] = { 'title': 'TechWords API', 'uiversion': 2 }
Swagger(app, template=manager.swagger_template)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def intro():
    send_ga(request.path)

    return "TechWords API" + """
        <script>
          (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
          (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
          m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
          })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

          ga('create', '%s', 'auto');
          ga('send', 'pageview');

        </script>
            """ % (PROPERTY_ID)

# we rely on auto sorting the dates, dont use this:
# app.config["JSON_SORT_KEYS"] = False

@app.route('/api/v1/trends', methods=['GET'])
@measure_time
def trends():
    """Get list of technology trends between dates
    ---
    tags:
     - API v1
    parameters:
     - name: start_date
       type: string
       format: date
       in: query
     - name: end_date
       type: string
       format: date
       in: query
    import: "schemas.yaml"
    responses:
      200:
        description: "Dictionary of date strings mapped to array of objects: techword and count"
        schema:
            $ref: '#/definitions/map_date_techwords'
        examples:
          { "2017-05-01": [ { word: "Python", count: 42 },
                            { word: "Java", count: 10 }] }
      404:
        description: "Bad format in dates"
    """
    send_ga(request.path)


    today = datetime.datetime.now()

    start_date = request.args.get('start_date', today.isoformat())
    end_date = request.args.get('end_date', today.isoformat())
    try:
        dates = utils.check_dates(start_date, end_date)
        r = controllers.get_techword_counts(dates[0],dates[1])
        return jsonify(r)
    except ValueError as e:
        return bad_request(e)


@app.route('/api/v1/techwords', methods=['GET'])
def techwords():
    """Get all techwords
    ---
    tags:
     - API v1
    import: "schemas.yaml"
    responses:
      200:
        description: "Array of objects: tech_word and search_strings used to find it"
        schema:
            $ref: '#/definitions/techword_array'
        examples:
          [ { tech_word: 'C',  search_strings: [ " C, ", " C." ] } ]
    """
    send_ga(request.path)

    words = controllers.get_techwords()
    return jsonify([w.serialize for w in words])



@app.route('/api/v1/techword/<string:word>', methods=['GET'])
def techword(word):
    """Get single techword
    ---
    tags:
     - API v1
    import: "schemas.yaml"
    parameters:
      - name: word
        in: path
        type: string
        required: true
    responses:
      200:
        description: "The techword objects: tech_word and search_strings used to find it"
        schema:
            $ref: '#/definitions/word'
        examples:
          { tech_word: 'C',  search_strings: [ " C, ", " C." ] }
      404:
        description: "Techword not found"
    """
    send_ga(request.path)

    words = controllers.get_techword(word)
    if len(words) == 0:
        return bad_request(("TechWord %s not found" % word))
    return jsonify([w.serialize for w in words])




@app.route('/api/v1/advertisements', methods=['GET'])
def advertisements():
    """Get list of job advertisements between dates
    ---
    tags:
     - API v1
    parameters:
     - name: start_date
       type: string
       format: date
       in: query
     - name: end_date
       type: string
       format: date
       in: query
     - name: text
       in: query
       type: boolean
       description: Include the advertisement text in responses
    import: "schemas.yaml"
    responses:
      200:
        description: "Array of job advertisements"
        schema:
            $ref: '#/definitions/advertisements_array'
        examples:
          [ {    end_date: "Sun, 19 Feb 2017 22:00:00 GMT", id: 9143236,
    start_date: "Thu, 19 Jan 2017 22:00:00 GMT",  title: "Ohjelmistosuunnittelija (Magento), Gelo Oy, Tampere"
        }, {   "end_date": "Tue, 21 Mar 2017 00:00:00 GMT", id: 9143263,
    start_date: "Thu, 19 Jan 2017 22:00:00 GMT",   title: "Ohjelmistosuunnittelija, PHP Solutions Oy, Tampere"
        } ]
      404:
        description: "Bad format in dates"
    """
    try:
        send_ga(request.path)
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')

        include_text = request.args.get('text','false')
        text = utils.check_true_false(include_text)
        if start_date != '' and end_date != '':
            dates = utils.check_dates(start_date, end_date)
            r = controllers.get_advertisements(dates[0],dates[1])
        else:
            r = controllers.get_advertisements()

        if text:
            return jsonify([a.serialize_with_text for a in r])

        return jsonify([a.serialize for a in r])
    except ValueError as e:
        return bad_request(e)





@app.route('/api/v1/matchresult/<int:id>/<string:word>', methods=['GET'])
def matchresults(word, id):
    """Get locations of single techword in advertisement text
    ---
    tags:
     - API v1
    parameters:
     - name: id
       type: integer
       format: int64
       in: path
       description: an id of an advertisement e.g. 9143263
     - name: word
       type: string
       in: path
       description: a known techword e.g. GIT
    import: "schemas.yaml"
    responses:
      200:
        description: "Advertisement text and array of matches for techword"
        schema:
            $ref: '#/definitions/match_results'
        examples:
          {  matches: [ { index: 137, search_string: " git", word: "GIT" } ],
            text: "PHP ...." }
      404:
        description: "Parameters for techword or advertisement id are wrong"
    """
    send_ga(request.path)

    words = controllers.get_techword(word)
    if len(words) == 0:
        return bad_request(("TechWord %s not found" % word))
    if len(words) > 1:
        return bad_request(("Multiple TechWords %s found, use one" % word))

    ads = controllers.get_advertisement(id)
    if len(ads) == 0:
        return bad_request(("No Advertisement found with id %d " % id))

    r = controllers.match_result(ads[0],words)
    return jsonify(text=ads[0].text, matches=r)

@app.route('/api/v1/matchresult/<int:id>', methods=['GET'])
def matchresult(id):
    """Get locations of all techwords found in advertisement text
    ---
    tags:
     - API v1
    parameters:
     - name: id
       type: integer
       format: int64
       in: path
       description: an id of an advertisement e.g. 9143263
    import: "schemas.yaml"
    responses:
      200:
        description: "Advertisement text and array of matches for techwords"
        schema:
            $ref: '#/definitions/match_results'
        examples:
          {  matches: [  { index: 90, search_string: "sql", word: "SQL" },
                         { index: 137, search_string: " git", word: "GIT" } ],
            text: "PHP ...." }
      404:
        description: "Advertisement id are wrong"
    """
    send_ga(request.path)


    words = controllers.get_techwords()
    ads = controllers.get_advertisement(id)
    if len(ads) == 0:
        return bad_request(("No Advertisement found with id %d " % id))

    r = controllers.match_result(ads[0],words)
    return jsonify(text=ads[0].text, matches=r)





@app.errorhandler(400)
def bad_request(e):
    response = jsonify({'message': str(e)})
    response.status_code = 400
    return response








if __name__ == '__main__':
    app.debug = True
    app.run(host=manager.default_host, port=manager.default_port)
