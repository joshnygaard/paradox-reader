# paradox-reader
Python module to read Paradox ```.txt``` files used in Crusader Kings II, Europa Universalis IV, Stellaris, and Hearts of Iron IV

## What it Does
This code will read a Paradox ```.txt``` file so that it can be used within a Python script. It can also save the read ```.txt``` as a JSON file.

## Why
My originally goal was to create some kind of tool for creating random Stellaris empires given a specific government type or personality. Instead of manually writing a JSON or YAML file of the criteria of each government or personality, it made sense to find a way to read the criteria straight from the relevant .txt files.

## How Does it do That
Given a file this script will use regular expression substitutions to translate the ```.txt``` file text into valid JSON. The Paradox .txt file format is fairly permissive so several choices had to be made to jerry-rig it into Python:
* Duplicate keys are turned into lists
```
allow = {
	is_country_type = default
	OR = {
		AND = {
			has_ethic = "ethic_fanatic_militarist"
			OR = {
				has_ethic = "ethic_spiritualist"
				has_ethic = "ethic_egalitarian"
				has_ethic = "ethic_xenophile"
			}
		}
		AND = {
			has_ethic = "ethic_fanatic_xenophile"
			has_ethic = "ethic_militarist"
		}
	}
}
```
Turns into:
```json
"allow": {
	"is_country_type": "default",
		"OR": {
			"AND": [
				{
					"has_ethic": "ethic_fanatic_militarist",
					"OR": {
						"has_ethic": [
							"ethic_spiritualist",
							"ethic_egalitarian",
							"ethic_xenophile"
						]
					}
				},
				{
					"has_ethic": [
						"ethic_fanatic_xenophile",
						"ethic_militarist"
					]
				}
			]
		}
	}
}
```
* Greater than and less than comparisions get turned into objects:
```
happened = {
	num_owned_planets > 1
}
```
Turns into
```json
"num_owned_planets": {
	"value": 1,
	"operand": ">"
}
```

## Disclaimers
I am in no way affliated with Paradox, nor do I have any knowledge on how they use these ```.txt``` files. Therefore I make no guarantees that this will correctly translate any given file, this has only been tested on a few files from Stellaris. 
