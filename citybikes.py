#! /usr/bin/env python3

# A command-line tool to show HSL city bike availability at selected bike stations.

# Copyright 2019 Joonas Saario.
# This program is licensed under the GNU GPL version 3 or any later version.


# Imports.

# argumentparser() handles the parsing of command line arguments.
from argparse import ArgumentParser as argumentparser
# http_post() makes a HTTP POST request to a given server.
from requests import post as http_post


# Functions.

# Returns data for the given stations.
def get_station_data(stations):
	# Create the output.
	station_data = {}
	# Query the stations one at a time.
	for station_id in stations:
		reply = query_stations(station_id=station_id)
		# Check the contents of the reply and skip empty replies.
		if not reply:
			print("Warning: Station '{}' not found.".format(station_id))
			continue
		# Get the values from the reply.
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
def print_output(station_data, hide_empty=False, hide_unavailable=False):
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
			# Check if unavailable stations should be printed or not.
			if hide_unavailable:
				continue
			else:
				station_size = "0"
				station_bikes = "0"
		# Check if empty stations should be printed or not.
		if hide_empty and station_bikes == "0":
			continue
		# Pad the output values.
		station_name = station_name.ljust(paddings.get("name", 0))
		station_bikes = station_bikes.rjust(paddings.get("bikes", 0))
		station_size = station_size.rjust(paddings.get("size", 0))
		# Create a new output line and add it to the output.
		output_line = "{}    {}/{}".format(station_name, station_bikes, station_size)
		output.append(output_line)
	# Print the output.
	for line in output:
		print(line)
	# All done, return.
	return None

# Queries the HSL API for station information.
# If station ID is given, extended information for that station is returned.
# If no ID is given, limited information for all stations is returned.
def query_stations(station_id=None):
	# Set the query url. This only needs to be changed if the API changes.
	url = "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
	# Check if one station or all stations should be queried.
	if station_id:
		# Master keyword used in retrieving the data.
		keyword = "bikeRentalStation"
		# Values to be retrieved.
		values = "stationId name state bikesAvailable spacesAvailable allowDropoff"
		# String used in the query. The API requires curly spaces in the query string, thus making .format() syntax very, very ugly.
		query = "{{{keyword}(id: \"{station}\") {{{values}}}}}".format(keyword=keyword, station=station_id, values=values)
	else:
		# Master keyword used in retrieving the data.
		keyword = "bikeRentalStations"
		# Values to be retrieved.
		values = "stationId name"
		# String used in the query. The API requires curly spaces in the query string, thus making .format() syntax very, very ugly.
		query = "{{{keyword} {{{values}}}}}".format(keyword=keyword, values=values)
	# Query the API.
	reply = http_post(url, json={"query": query})
	# Get the JSON-formatted version of the reply and extract the station information.
	reply_json = reply.json()
	reply_data = reply_json["data"][keyword]
	# All done, return.
	return reply_data


# Parses the output of query_bikes and returns a list.
def parse_replies(replies):
	# Create the output.
	station_data = {}
	# Parse the replies.
	for reply in replies:
		if not reply:
			continue
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
def query_bikes_old(stations):
	url = "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
	values = ["stationId", "name", "state", "bikesAvailable", "spacesAvailable", "allowDropoff"]
	# Create the output.
	replies = []
	# Create a string from the query value list.
	value_string = " ".join(values)
	# The API only allows to query one station at a time. Let's query one station at a time, then.
	for station in stations:
		# Query the station. The API requires curly spaces in the query string, thus making .format() syntax very, very ugly.
		query_string = "{{bikeRentalStation(id: \"{station}\") {{{values}}}}}".format(station=station, values=value_string)
		reply = http_post(url, json={"query": query_string})
		# Get the JSON-formatted version of the reply and extract the station information.
		reply_json = reply.json()
		reply_station = reply_json["data"]["bikeRentalStation"]
		# Check the contents of the reply and skip empty replies.
		if not reply_station:
			print("Warning: Station '{}' not found.".format(station))
			continue
		# Append the reply.
		replies.append(reply_station)
	# All done, return.
	return replies


# Main.

# Create a parser for the command line arguments.
argument_parser = argumentparser(description="Returns the status of selected HSL city bike stations.", allow_abbrev=False)
argument_parser.add_argument("-s", "--stations", type=str, help="Return the status of one or more space-separated STATIONs. Only station number is accepted.", nargs="*", required=True)
argument_parser.add_argument("--hide-empty", action="store_true", help="Hide stations that are empty.")
argument_parser.add_argument("--hide-unavailable", action="store_true", help="Hide stations that are unavailable.")
# Parse the arguments.
arguments = argument_parser.parse_args()

# Get the list of stations.
stations = arguments.stations

# Query the HKL API and parse the replies, old version.
query_replies = [query_stations(station_id=station) for station in stations]
station_data_old = parse_replies(query_replies)

# Query the HKL API and parse the replies, new version.
station_data = get_station_data(stations)

# Print the output.
print_output(station_data_old, hide_empty=arguments.hide_empty, hide_unavailable=arguments.hide_unavailable)
print_output(station_data, hide_empty=arguments.hide_empty, hide_unavailable=arguments.hide_unavailable)


# All done, exit.
exit(0)
