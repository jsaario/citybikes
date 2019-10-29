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

# Returns the station IDs for given stations. Input can be the name or the ID of the station, or the integer of the ID.
# Some of the station IDs contain leading zeroes, while others do not. This is a feature of the API.
# This routine is needed to mitigate the issue and allow invalid station IDs to be given as import.
def get_station_ids(stations):
	# Create the output.
	station_ids = []
	# Query the API for the station information. As we give no station ID, this will return all stations.
	station_data = query_stations()
	# Create temporary dictionaries.
	stations_by_name = {}
	stations_by_integer = {}
	# Process the queried data.
	for station in station_data:
		# Get the name and the ID for this station.
		station_name = station.get("name", None)
		station_id = station.get("stationId", None)
		# Check that the data is sane.
		if station_name is None or station_id is None:
			continue
		# Check that the station_id is a number and convert it to an integer.
		if not station_id.isdecimal():
			continue
		station_integer = int(station_id)
		# Add the values to the respective dictionaries.
		stations_by_name.update({station_name: station_id})
		stations_by_integer.update({station_integer: station_id})
	# Process the input station list.
	for station in stations:
		# Check the type of identifier given. All input is assumed to be strings!
		if station.isdecimal():		
			# The string contains a numerical value. It is assumed to be an ID.
			station_integer = int(station)
			station_id = stations_by_integer.get(station_integer, None)
		else:
			# The string contains non-decimal characters. It is assumed to be a name.
			station_name = station
			station_id = stations_by_name.get(station_name, None)
		# Check the station ID and append it.
		if not station_id:
			print("Warning: Station '{station}' not found.".format(station=station))
			continue
		station_ids.append(station_id)
	# All done, return.
	return station_ids

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


# Main.

# Create a parser for the command line arguments.
argument_parser = argumentparser(description="Returns the status of selected HSL city bike stations.", allow_abbrev=False)
argument_parser.add_argument("-s", "--stations", type=str, help="Return the status of one or more space-separated STATIONs. Only station number is accepted.", nargs="*", required=True)
argument_parser.add_argument("--hide-empty", action="store_true", help="Hide stations that are empty.")
argument_parser.add_argument("--hide-unavailable", action="store_true", help="Hide stations that are unavailable.")
# Parse the arguments.
arguments = argument_parser.parse_args()

# Get the list of stations.
stations = get_station_ids(arguments.stations)
#stations = arguments.stations

# Query the HKL API and parse the replies.
station_data = get_station_data(stations)

# Print the output.
print_output(station_data, hide_empty=arguments.hide_empty, hide_unavailable=arguments.hide_unavailable)

# All done, exit.
exit(0)
