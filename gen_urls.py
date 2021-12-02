#!/usr/bin/env python3

# This script generates a URLs.json file that maps CRNs to their individual
# course URLs. The bot has no access to this. Run this once per registration
# season to keep the URLs up-to-date.
#
# You'll need to have a ./courses.html present that's just a save of
# https://mystudentrecord.ucmerced.edu/pls/PROD/xhwschedule.P_ViewSchedule

import bs4
import json
import re

def main():

	print("Generating new URLs.json...", end=" ")

	# Read courses.html and get the course table.
	with open("./courses.html", "r") as f:
		tables = bs4.BeautifulSoup(f.read(), "html.parser").find_all("table")

	data = {}

	# Get the URLs for every single CRN listed.
	for table in tables:
		for row in table.find_all("tr")[1::]:
			course = row.find("td")
			if re.match("\d{5}", course.text):
				data[course.text] = course.find("a")["href"]

	# Save everything to URLs.json.
	with open("URLs.json", "w+") as f:
		json.dump(data, f)

	print("Done.")

if __name__ == "__main__":
	main()
