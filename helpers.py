#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


def get_county(lat, lon):
    ''' Takes lat and lon and returns the coresponding county '''
    payload = {"data": "[output:json];is_in(%f, %f);out;" % (lat, lon)}
    r = requests.get("http://overpass-api.de/api/interpreter", params=payload)
    x = r.json()
    output = {}
    for l in x.get("elements"):
        if "admin_level" in l["tags"]:
            output[int(l["tags"]["admin_level"])] = \
                l["tags"]["name"]
    return output


def print_success(message):
    ''' Print the message in green '''
    print('\033[1;32m%s\033[1;m' % (message))


def print_failure(message):
    ''' Print the message in red '''
    print('\033[1;31m%s\033[1;m' % (message))


def print_info(message):
    ''' Print the message in yellow '''
    print('\033[1;33m%s\033[1;m' % (message))
