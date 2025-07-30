import yaml
from munch import Munch as munch

from gpddatabase.Exceptions import ExceptionNoDataInFile
from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionNotUnique
from gpddatabase.Exceptions import ExceptionUnknownType

class GenericTypes:

	'''Generic definition of type.'''

	def __init__(self, paths):

		#data
		self.data = []

		#loop over paths
		for path in paths.split(":"):

			#get raw data
			with open(path, 'r', encoding="utf-8") as f:
				rawData = yaml.safe_load(f)

			#get data
			data = munch.fromDict(rawData)

			#check if not empty
			if data is None:
				raise ExceptionNoDataInFile(path)

			#check for data field
			try:
				data['data']
			except KeyError as err:
				raise ExceptionNoField('data') from err

			#append
			for field in data['data']:
				self.data.append(field)

		#collect
		self.types = []

		for field in self.data:

			try:
				field['name']
			except KeyError as err:
				raise ExceptionNoField('name') from err

			if field['name'] in self.types:
				raise ExceptionNotUnique(field['name'])

			self.types.append(field['name'])

		#collect
		self.descriptions = {}

		for field in self.data:

			try:
				field['description']
			except KeyError as err:
				raise ExceptionNoField('description') from err

			self.descriptions.update({field['name']: field['description']})

	def check_type(self, value):

		'''Check if type exist. If not, raise exception.'''

		if value not in self.types:
			raise ExceptionUnknownType(value)

	def get_description(self, value):

		'''Get description of a given type.'''

		try:
			return self.descriptions[value]
		except KeyError as err:
			raise ExceptionUnknownType(value) from err
