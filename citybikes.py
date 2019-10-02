#! /usr/bin/env python3

# A command-line tool to show HSL city bike availability at selected bike stations.

# Copyright 2019 Joonas Saario.
# This program is licensed under the GNU GPL version 3 or any later version.


# Imports.

# http_post() makes a HTTP POST request to a given server.
from requests import post as http_post


# Functions.

# Parses the output of query_bikes and returns a list.
def parse_replies(replies):
	# Create the output.
	station_data = {}
	# Parse the replies.
	for reply in replies:
		# Get the values.
		station_id = reply.get("stationId", None)
		station_name = reply.get("name", None)
		station_state = reply.get("state", "")
		station_bikes = reply.get("bikesAvailable", 0)
		station_emptyspaces = reply.get("spacesAvailable", 0)
		station_dropoff = reply.get("allowDropoff", False)
		# Check the values.
		if station_id is None or station_name is None:
			pass
		# Check the state of the station.
		if station_state == "Station on" and station_dropoff:
			station_available = True
		else:
			station_available = False
		# Calculate the station size.
		station_size = station_bikes + station_emptyspaces
		# Store the values.
		station_data.update({station_id: {
			"name": station_name,
			"available": station_available,
			"size": station_size,
			"bikes": station_bikes
			}})
	# All done, return.
	return station_data

# Queries the given URL for the bikes.
def query_bikes(url, values, stations):
	# Create the output.
	replies = []
	# Create a string from the query value list.
	value_string = " ".join(values)
	# The API only allows to query one station at a time. Let's query one station at a time, then.
	for station in stations:
		# Query the station.
		query_string = "{bikeRentalStation(id: \"%s\") {%s}}" %(station, value_string)
		reply = http_post(url, json={"query": query_string})
		# Store the JSON-formatted version of the reply.
		reply_json = reply.json()
		replies.append(reply_json["data"]["bikeRentalStation"])
	# All done, return.
	return replies


# Main.

# Temporary parameters.
query_url = "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
query_values = ["stationId", "name", "state", "bikesAvailable", "spacesAvailable", "allowDropoff"]
query_stations = ["001", "002"]

# Query the HKL API and parse the replies.
query_replies = query_bikes(query_url, query_values, query_stations)
station_data = parse_replies(query_replies)

# Next: Output.
print(station_data)

# All done, exit.
exit(0)
