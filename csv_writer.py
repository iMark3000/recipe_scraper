import csv

# This works. Do not Touch.

class LogToCSV:

	def __init__(self, jfile):
		self.jfile = jfile

	def write_meta_data(self, meta_data):

		field_names = ['website_name', 'website_address', 'recipe_author','recipe_name', 'recipe_description']

		with open('./recipe_spreadsheets/meta_data.csv', 'a', newline='') as file:
			csvwriter = csv.DictWriter(file, fieldnames = field_names)
			#csvwriter.writeheader()
			csvwriter.writerow(meta_data)

	def write_ingredient_data(self, ingredient_data):

		field_names = ['recipe_name', 'recipe_address', 'ingredient_group_name', 'ingredient', 'amount', 'unit']

		with open('./recipe_spreadsheets/ingredient_data.csv', 'a', newline='') as file:
			csvwriter = csv.DictWriter(file, fieldnames = field_names)
			#csvwriter.writeheader()
			for row in ingredient_data:
				csvwriter.writerow(row)


	def write_instruction_data(self, ingredient_data):

		field_names = ['recipe_name', 'recipe_address', 'instruction_group_name', 'instruction_set_number', 'instruction_step', 'instruction_text']

		with open('./recipe_spreadsheets/instruction_data.csv', 'a', newline='') as file:
			csvwriter = csv.DictWriter(file, fieldnames = field_names)
			#Scsvwriter.writeheader()
			for row in ingredient_data:
				csvwriter.writerow(row)
