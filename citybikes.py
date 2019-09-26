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
query_values = ["stationId", "name", "state", "bikesAvailable", "spacesAvailable", "allowDropoff"]
stations = ["001", "002"]

# Create a string from the query values and an empty list for storing the replies.
value_string = " ".join(query_values)
replies = []
# The API only allows to query one station at a time. So let's query one station at a time, then.
for station in stations:
	# Query the station.
	query_string = "{bikeRentalStation(id: \"%s\") {%s}}" %(station, value_string)
	reply = http_post(query_url, json={"query": query_string})
	# Store the reply.
	reply_json = reply.json()
	replies.append(reply_json["data"]["bikeRentalStation"])

# "state": "Station on",
# "state": "Station off",

# All done, exit.
exit(0)
