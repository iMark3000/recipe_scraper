import os
from datetime import datetime
import inspect


class LogEvent:

	def __init__(self, address, message):
		self.DIR_LOCATION = './error_logs'
		self.method_source = inspect.stack()[1][3]
		self.address = address
		self._log(message)

	def _check_for_log_directory(self):
		'''Checks for lod directory, creates one if not found'''
		if not os.path.isdir(self.DIR_LOCATION):
			os.mkdir(self.DIR_LOCATION)

	def _open_log(self):
		'''Opens a log'''
		return open(os.path.join(self.DIR_LOCATION, 'logs.txt'), 'a')

	def _log(self, message):
		self._check_for_log_directory()
		logfile = self._open_log()
		tm = datetime.now()
		tm_string = tm.strftime("%m/%d/%y - %H:%M:%S")
		logfile.write(f'{tm_string} || {self.address} || - error in {self.method_source}  -- {message}\n')
		print('+++ ERROR LOGGED +++')
