#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


def get_county(lat, lon):
    ''' Takes lat and lon and returns the coresponding county '''
    payload = {"data": "[output:json];is_in(%f, %f);out;" % (lat, lon)}
    r = requests.get("http://overpass-api.de/api/interpreter", params=payload)
    print(r.url)
    json_response = r.json()
    admin_level_to_name = {}
    for l in json_response["elements"]:
        if "admin_level" in l["tags"]:
            admin_level_to_name[l["tags"]["admin_level"]] = l["tags"]["name"]

    # for an explanation of the numbers see
    # http://wiki.openstreetmap.org/wiki/Admin_level
    if '6' in admin_level_to_name:  # in Germany this is a Landkreis
        return admin_level_to_name['6']

    if '4' in admin_level_to_name:  # in Germany this is a Bundesland
        # this is also used for Berlin which does not have a
        # Landkreis in the OSM data
        return admin_level_to_name['4']

    return 'Unknown'


def print_success(message):
    ''' Print the message in green '''
    print('\033[1;32m%s\033[1;m' % (message))


def print_failure(message):
    ''' Print the message in red '''
    print('\033[1;31m%s\033[1;m' % (message))


def print_info(message):
    ''' Print the message in yellow '''
    print('\033[1;33m%s\033[1;m' % (message))
