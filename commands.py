import csv
import datetime
from math import log10

import click
import requests

import config
from app import app, recheck
from helpers import print_success, print_failure
from models import Stop, db


def recheck_batch(Stops):
    total = 0
    number_of_stops = len(Stops)
    digits = int(log10(number_of_stops)) + 1
    counter = 0
    for stop in Stops:
        counter += 1
        print("%*i/%*i " % (digits, counter, digits, number_of_stops))
        out = recheck(stop.id, from_cm_line=True)
        if out > 0:
            total += 1
    print_success("Insgesamt %i neue Treffer" % total)



def recheck_all_missings_stops():
    Stops = Stop.query.filter(Stop.matches < 1).all()
    recheck_batch(Stops)


def recheck_by_name(name):
    Stops = Stop.query.filter(Stop.name.like("%" + name + "%"),
                              Stop.matches < 1).all()
    recheck_batch(Stops)


def recheck_all():
    Stops = Stop.query.all()
    recheck_batch(Stops)


@app.cli.command()
def import_stops():
    ''' The initial query to set up the stop db '''
    all_stops = Stop.query.all()
    all_ids = [stop.id for stop in all_stops]
    url = config.stops_txt_url
    req = requests.get(url)
    req.encoding = 'utf-8'
    text = req.text.split('\n')
    reader = csv.DictReader(text, delimiter=',', quotechar='"')
    counter = 0
    for line in reader:
        stop = Stop(line)
        if stop.is_station and stop.id not in all_ids:
            stop.matches = stop.is_in_osm()
            stop.query_and_set_county()
            if stop.matches > 0:
                print_success(stop.name + ": " + str(stop.matches))
            else:
                print_failure(stop.name + ":  0")
            stop.last_run = datetime.datetime.now().replace(microsecond=0)
            db.session.add(stop)
            counter += 1
            if counter % 20 == 0:
                db.session.commit()
