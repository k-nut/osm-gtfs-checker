import os

stops_txt_url = os.environ.get("OSM_CHECKER_STOPS_TXT_URL")
name = os.environ.get("OSM_CHECKER_APP_NAME", "OSM GTFS Haltestellen Validator")
initial_map_cordinates = {'lat': os.environ.get("OSM_CHECKER_LAT"),
                          'lon': os.environ.get("OSM_CHECKER_LON")}
attribution = os.environ.get("OSM_CHECKER_ATTRIBUTION")