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

# Prints output.
def print_output(station_data):
	# Create the output to be printed.
	output = []
	# Get the padding lengths.
	paddings = {}
	for station_id in station_data.keys():
		for key in station_data[station_id].keys():
			value_length = len(str(station_data[station_id][key]))
			if value_length > paddings.get(key, 0):
				paddings.update({key: value_length})
	# Format the output.
	for station_id in station_data.keys():
		# Get the values.
		station_name = station_data[station_id].get("name", "unknown")
		station_available = station_data[station_id].get("available", False)
		station_size = str(station_data[station_id].get("size", 0))
		station_bikes = str(station_data[station_id].get("bikes", 0))
		# Check the station availability.
		if not station_available:
			station_size = "0"
			station_bikes = "0"
		# Create the output line and add it to the output.
		output_line = station_name.ljust(paddings.get("name", 0)) + "    " \
			+ station_bikes.rjust(paddings.get("bikes", 0)) + "/" \
			+ station_size.rjust(paddings.get("size", 0))
		output.append(output_line)
	# Print the output.
	for line in output:
		print(line)
	# All done, return.
	return None

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
query_stations = ["001", "002", "003", "004", "005", "006", "007", "008", "009"]

# Query the HKL API and parse the replies.
query_replies = query_bikes(query_url, query_values, query_stations)
station_data = parse_replies(query_replies)

# Print the output.
print_output(station_data)

# All done, exit.
exit(0)
