#!/usr/bin/python3
# Count same word occurrences in Hávamál
import json
from pathlib import Path

def stripLine(l):
	"""Strip input string of characters contained in local ignore list.
	Param: l (str)
	Returns: list (str)"""
	strip = ['.', ',', ';', ':', '!', '?', '"']
	words = l.split(' ')
	for i in range(len(strip)):
		words = [word.replace(strip[i], '').lower() for word in words]
	return words

file = Path('../data/havamal1.json')
wordsl = []

try:
	with open (file, 'rb') as f:
		data = json.load(f)

except Exception as e:
	print(e)

else:
	verses = data['poem']['verses']

	for verse in verses:
		for strophe in verse['strophes']:
			for line in strophe['lines']:
				saneLine = stripLine(line)
				wordsl.extend(saneLine)

wordsl.sort()

counts = {}
for word in wordsl:
    if word not in counts:
        counts[word] = 0
    counts[word] += 1

print(type(counts))

for val in counts:
	if (counts[val] > 1):
		print(f"{val}: {counts[val]}")
