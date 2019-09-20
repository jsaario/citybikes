#! /usr/bin/env python3

# A command-line tool to show HSL city bike availability at selected bike stations.

# Copyright 2019 Joonas Saario.
# This program is licensed under the GNU GPL version 3 or any later version.


# Imports.

# http_post() makes a HTTP POST request to a given server.
from requests import post as http_post


# Main.

# Temporary parameters.
query_url = "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
stations = ["001", "002"]

# The API only allows to query one station at a time. Great...
for station in stations:
	query_string = "{bikeRentalStation(id: \"%s\") {stationId name state bikesAvailable spacesAvailable allowDropoff}}" %(station)
	reply = http_post(query_url, json={"query": query_string})
	print(reply.json())

# "state": "Station on",
# "state": "Station off",

# All done, exit.
exit(0)
