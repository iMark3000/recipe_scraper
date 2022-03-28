import json#	This module needs to be split?
#	It both drives the scraper and routes the 
#	data to json and csv files

import pprint
import re

from error_logger import *
from recipescraper import WordPressScraper
from csv_writer import LogToCSV

def send_to_json(data):
	recipe_name = data['meta_data']['recipe_name']
	file_name = f'/home/m/Projects/python/RecipeScraper/json_files/{recipe_name}.json'
	with open(file_name, 'w') as write_file:
		json.dump(data, write_file, indent=2)

	LogToCSV(file_name)

def run():
	with open('/home/m/Projects/python/RecipeScraper/recipes_to_scrape/recipescrape_json_test.txt', 'r') as file:
		for line in file:
			scrape = WordPressScraper()
			try:
				scrape.scraper_input(line)
				if scrape.no_errors:
					recipe_data = scrape.get_data_package()
					send_to_json(recipe_data)
					print('No Errors:  JSON Created')
				else:
					with open('failed_link.txt', 'a') as fail_file:
						fail_file.write(f'{link}\n')
			except:
				LogEvent(line, sys.exc_info()[0])

	print('\n\n<<<<<PROCESS COMPLETE>>>>>>>>')


run()