"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import Flask, redirect, url_for, request, render_template
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
import os
from pymongo import MongoClient

import logging

###
# Globals
###
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CONFIG = config.configuration()

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.tododb
###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return render_template('calc.html')


@app.route("/display")
def display():
    if db.tododb.count_documents({}) != 0:
        return render_template('display.html', items=list(db.tododb.find()))
    else:
        flask.flash("No saved times to display!")
        return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = int(request.args.get('km', 999, type=float))
    start_time = request.args.get('start_time', '2021-01-01T00:00', type=str)
    brevet_dist = request.args.get('brevet_dist', 200, type=int)
    app.logger.debug("km={}".format(km))
    app.logger.debug("start time={}".format(start_time))
    app.logger.debug("request.args: {}".format(request.args))
    open_time = acp_times.open_time(km, brevet_dist, arrow.get(start_time)).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brevet_dist, arrow.get(start_time)).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


@app.route("/_submit")
def _submit():
    new_insert = request.args.get('new_insert', False, type=bool)
    if new_insert:
        db.tododb.delete_many({})
    km = request.args.get('km', 999, type=float)
    if not db.tododb.find_one({"dist": km}):
        control_times = {
            'dist': km,
            'open': request.args.get('open_time', type=str),
            'close': request.args.get('close_time', type=str),
        }
        db.tododb.insert_one(control_times)
        return flask.jsonify(result={"message": "Successful insertion"})
    else:
        return flask.jsonify(result={"message": "Not inserted, already in database"})

#############


app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
