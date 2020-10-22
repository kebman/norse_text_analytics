#!/usr/bin/python3
# read 'havamal4.json'

import json
from pathlib import Path

file = Path('../data/havamal4.json')

try:
	with open (file, 'rb') as f:
		data = json.load(f)

except Exception as e:
	print(e)

else:
	# print the first strophe in Verse I.
	lines = data['poem']['verses'][0]['strophes'][0]['lines']

	for line in lines:
		print(line) 
