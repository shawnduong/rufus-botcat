def scrape(CRN: int, url: str, output: dict) -> int:
	"""
	Write the number of open seats given a course registration page URL to a
	specified output.
	"""

	import bs4
	import requests

	page = requests.get(url).content
	soup = bs4.BeautifulSoup(page, "html.parser")

	table = soup.find_all("table", attrs={"class": "datadisplaytable"})[-1]
	seats = table.find_all("td", attrs={"class": "dddefault"})[-1].text

	output[CRN] = int(seats)

