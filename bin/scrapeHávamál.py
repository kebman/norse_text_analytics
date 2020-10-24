#!/usr/bin/python3
# Scrape and read Hávamál
from os import path
from urllib import request
from bs4 import BeautifulSoup

# Save web-page to HTML-file
HávamálUrl = 'https://heimskringla.no/wiki/H%C3%A1vam%C3%A1l'
file = '../data/Hávamál.html'

if (path.isfile(file)):
	print("Reading existing file")

	# read and parse file
	with open (file, 'r') as f:
		soup = BeautifulSoup(f, "html.parser")

else:
	print("Writing file")

	# Get the page
	page = request.urlopen(HávamálUrl)

	# save page
	request.urlretrieve(HávamálUrl, file)

	# read and parse page
	html = page.read().decode()
	soup = BeautifulSoup(html, "html.parser")

# scrape the poem
print(soup.dl.get_text())
