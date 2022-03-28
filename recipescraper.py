import requests
import re
import sys

from bs4 import BeautifulSoup as bs

from error_logger import *

#	This app will scrape all of the data from 
#	websites. It will store the data in a few 
#	different data structures to be passed on. It will raise notify other 
#	modules of errors.



class WordPressScraper:

	def __init__(self):
		self.address = ''
		self.recipe_name = ''
		self.author = ''
		self.website_name = ''
		self.scraped_date = ''
		self.ingredients = []
		self.keywords = []
		self.instructions = []
		self.nutrition = {}
		self.notes = []	# Not used...but planning to grab recipe notes eventually
		self.recipe_description = ''
		self.no_errors = True

	def scraper_input(self, address):
		# Start point for scraper
		self.address = address
		self.drive()

	def _request_site(self):
		self.req = requests.get(self.address)
		self.req.close()

	def _create_soup(self):
		self.soup = bs(self.req.text, 'lxml')

	def _scrape_meta_data_driver(self):
		# Calls all of the methods that
		# scrape recipe meta data
		self._scrape_website_name()
		self._scrape_recipe_name()
		self._scrape_author_name()
		self._scrape_recipe_description()

	# Meta data
	def _scrape_website_name(self):
		try:
			meta_tag = self.soup.find_all('meta', property='og:site_name')
			self.website_name = meta_tag[0].attrs['content']
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.website_name = 'NONE'
			self.no_errors = False

	def _scrape_recipe_name(self):
		try:
			self.recipe_name = self.soup.find_all('h1', class_='entry-title')[0].text.strip()
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.recipe_name = 'NONE'
			self.no_errors = False

	def _scrape_author_name(self):
		try:
			self.author = self.soup.find_all('span', class_='entry-author-name')[0].text
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.author = self.website_name
			self.no_errors = False	

	def _scrape_recipe_description(self):
		try:
			meta_tag = self.soup.find_all('meta', property='og:description')
			self.recipe_description = meta_tag[0].attrs['content']
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.recipe_description = 'NONE'
			self.no_errors = False

	# INGREDIENTS

	def _scrape_ingredient_data_driver(self):
		self._scrape_ingredients_container()
		self._analyze_ingredient_structure()

	def _scrape_ingredients_container(self):
		try:
			self.ingredients_container = self.soup.find_all('div', class_='wprm-recipe-ingredients-container')[0]
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	

	def _analyze_ingredient_structure(self):
		#This function determines if there are multiple recipe ingredient groups
		ingredient_groups = self._scrape_ingredient_groups()
		if len(ingredient_groups) == 1:
			ingredient_group = ingredient_groups[0]
			ingredient_group_name = 'main'
			self._scrape_recipe_ingredients(ingredient_group, ingredient_group_name)
		else:
			for group in ingredient_groups:
				ingredient_group_name = self._scrape_ingredient_group_name(group).lower()
				self._scrape_recipe_ingredients(group, ingredient_group_name)
		
	def _scrape_ingredient_groups(self):
		# TODO: If this doesn't work, the whole program fails; Find a solution	
		try:
			return self.ingredients_container.find_all('div', class_='wprm-recipe-ingredient-group')
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	


	def _scrape_recipe_ingredients(self, ingredient_group, ingredient_group_name):
		ingredients_li = self._scrape_recipe_li(ingredient_group)
		ingredient_list = []
		for line in ingredients_li:
			ingredient_data = {}
			ingredient_data['ingredient'] = self._scrape_ingredient_name(line).lower()
			ingredient_data['amount'] = self._scrape_ingredient_amount(line)
			ingredient_data['unit'] = self. _scrape_ingredient_unit_of_measurement(line).lower()
			ingredient_list.append(ingredient_data)
			
		# This data is for json file
		ingredient_set_pacakge = {
			'ingredient_component_name':ingredient_group_name,
			'ingredient_component_list': ingredient_list
		}
			
		self.ingredients.append(ingredient_set_pacakge)

	def _scrape_recipe_li(self, group):
		# TODO: If this doesn't work, the whole program fails; Find a solution
		try:
			return group.find_all('li', class_='wprm-recipe-ingredient')
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	


	def _convert_amount_string_to_float(self, string):
		fraction = re.compile(r'(\d\/\d)')
		fraction_finder = re.split(fraction, string)
		print(fraction_finder)

		if len(fraction_finder) == 1:
			try:
				return float(fraction_finder[0])
			except ValueError:
				LogEvent(self.address, sys.exc_info()[0])
				return self._ascii_convertion(fraction_finder[0])
		else:
			try:
				float_whole_number = float(fraction_finder[0])
				float_fraction = self._fraction_conversion(fraction_finder[1])
				return float_whole_number + float_fraction
			except ValueError:
				LogEvent(self.address, sys.exc_info()[0])	
				return self._fraction_conversion(fraction_finder[1])

	def _fraction_conversion(self, fraction):
		if fraction == '1/8':
			return 0.125
		elif fraction == '1/4':
			return 0.25
		elif fraction == '1/3':
			return 0.33
		elif fraction  == '1/2':
			return 0.5
		elif fraction == '3/4':
			return 0.75

	def _ascii_convertion(self, string):
		if ord(string) == 188:
			return 0.25
		if ord(string) == 189:
			return 0.5
		if ord(string) == 190:
			return 0.75


	def _scrape_ingredient_name(self, line):
		try:
			return line.find_all('span', class_='wprm-recipe-ingredient-name')[0].text
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	
			return 'NONE'

	def _scrape_ingredient_amount(self, line):
		try:
			amount = line.find_all('span', class_='wprm-recipe-ingredient-amount')[0].text
			return self._convert_amount_string_to_float(amount)
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	
			return 'NONE'

	def _scrape_ingredient_unit_of_measurement(self, line):
		try:
			return line.find_all('span', class_='wprm-recipe-ingredient-unit')[0].text
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	
			return 'NONE'

	def _scrape_ingredient_group_name(self, group):
		try:
			return group.find_all('h4', class_='wprm-recipe-group-name')[0].text
		except:
			try:
				return group.find_all('h3', class_='wprm-recipe-group-name')[0].text
			except:
				LogEvent(self.address, sys.exc_info()[0])
				self.no_errors = False	
				return 'NONE'		

	# INSTRUCTIONS

	def _scrape_instruction_data_driver(self):
		self._scrape_instructions_container()
		self._analyze_instructions_structure()

	def _scrape_instructions_container(self):
		try:
			self.instructions_container = self.soup.find_all('div', 
				class_='wprm-recipe-instructions-container')[0]
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	

	def _analyze_instructions_structure(self):
		#This function finds whether there are multiple recipe groups
		instructions_group = self._scrape_instructions_group()
		if len(instructions_group) == 1:
			instructional_group = instructions_group[0]
			instructions_group_name = 'main'
			self._scrape_recipe_instructions(instructional_group, instructions_group_name)
		else:
			for group in instructions_group:
				instruction_group_name = group.find_all('h4', class_='wprm-recipe-group-name')[0].text.lower()
				self._scrape_recipe_instructions(group, instruction_group_name)


	def _scrape_instructions_group(self):
		# TODO: If this doesn't work, the whole program fails; Find a solution
		try:
			return self.instructions_container.find_all('div', class_='wprm-recipe-instruction-group')
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	

	def _scrape_recipe_instructions(self, instruction_group, instruction_group_name):
		instruction_set = self._scrape_instruction_set(instruction_group)
		set_number = self._scrape_instruction_set_number(instruction_set)
		instruction_list = []
		for instruction in instruction_set:
			step_data = {}
			step_data['instruction_step'] = self._scrape_instruction_step(instruction)
			step_data['instruction_text'] = self._scrape_instruction_text(instruction)
			instruction_list.append(step_data)
			
		instruction_set_package = {
			'instruction_set_name': instruction_group_name,
			'instruction_set_order': set_number,
			'instructions': instruction_list
		}

		self.instructions.append(instruction_set_package)

	def _scrape_instruction_set(self, group):
		# TODO: If this doesn't work, the whole program fails; Find a solution
		try:
			return group.find_all('li', class_='wprm-recipe-instruction')
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	
			return None

	def _scrape_instruction_set_number(self, line):
		try:
			return line[0]['id'].split('-')[-2]
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	
			return 'NONE'

	def _scrape_instruction_step(self, line):
		try:
			return line['id'].split('-')[-1]
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	
			return 'NONE'

	def _scrape_instruction_text(self, line):
		try:
			return line.text
		except:
			LogEvent(self.address, sys.exc_info()[0])
			self.no_errors = False	
			return 'NONE'

	# Getter Methods

	def _get_instructions_data(self):
		return self.instructions

	def _get_meta_data(self):
		meta_dict = {'website_name': self.website_name,
		'website_address': self.address,
		'recipe_author': self.author,
		'recipe_name': self.recipe_name,
		'recipe_description': self.recipe_description}
		return meta_dict

	def _get_ingredient_data(self):
		return self.ingredients

	def get_data_package(self):
		recipe_data = {}
		recipe_data['meta_data'] = self._get_meta_data()
		recipe_data['ingredients'] = self._get_ingredient_data()
		recipe_data['instructions'] = self._get_instructions_data()
		return recipe_data

	def drive(self):
		self._request_site()
		self._create_soup()
		self._scrape_meta_data_driver()
		self._scrape_ingredients_container()
		self._scrape_ingredient_data_driver()
		self._scrape_instruction_data_driver()