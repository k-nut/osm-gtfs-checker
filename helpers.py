#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson
import requests


def get_landkreis(lat, lon):
    ''' Takes lat and lon and returns the coresponding Landkreis '''
    payload = {"data": "[output:json];is_in(%f, %f);out;" % (lat, lon)}
    r = requests.get("http://overpass-api.de/api/interpreter", params=payload)
    x = simplejson.loads(r.text)
    output = {}
    for l in x.get("elements"):
        if "admin_level" in l["tags"]:
            output[int(l["tags"]["admin_level"])] = \
                l["tags"]["name"]
            #if l["tags"]["admin_level"] in ["8","6"]:
            #    return l["tags"]["name"]
    return output


def print_success(message):
    ''' Print the message in green '''
    print '\033[1;32m%s\033[1;m' % (message)


def print_failure(message):
    ''' Print the message in red '''
    print '\033[1;31m%s\033[1;m' % (message)
