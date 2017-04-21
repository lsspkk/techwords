#!/usr/bin/python
from flask import Flask, abort, request, jsonify
from flask_cors import CORS, cross_origin
import datetime, json
import models, controllers, utils

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# we rely on auto sorting the dates, dont use this:
# app.config["JSON_SORT_KEYS"] = False


@app.route('/api/v1/trends', methods=['POST','GET'])
def trends():
    today = datetime.datetime.now()

    start_date = request.args.get('start_date', today.isoformat())
    end_date = request.args.get('end_date', today.isoformat())
    try:
        dates = utils.check_dates(start_date, end_date)
        r = controllers.get_techword_counts(dates[0],dates[1])
        return jsonify(r)
    except ValueError, e:
        return bad_request(e)


@app.route('/api/v1/techwords', methods=['GET'])
def techwords():
    words = controllers.get_techwords()
    return jsonify([w.serialize for w in words])

@app.route('/api/v1/techword/<string:word>', methods=['GET'])
def techword(word):
    words = controllers.get_techword(word)
    if len(words) == 0:
        return bad_request(("TechWord %s not found" % word))
    return jsonify([w.serialize for w in words])


@app.route('/api/v1/advertisements', methods=['GET'])
def advertisements():
    try:
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
    except ValueError, e:
        return bad_request(e)

@app.route('/api/v1/matchresult/<int:id>/<string:word>', methods=['GET'])
def matchresults(word, id):
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
    app.run(host='0.0.0.0', port=9090)
