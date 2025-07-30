from gpddatabase.GenericTypes import GenericTypes

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionRequiredDiffSizes
from gpddatabase.Exceptions import ExceptionUnknownType

import gpddatabase as db

class DataTypes(GenericTypes):

	'''Class stroring data types'''

	def __init__(self, paths):

		#run parent constructor
		super().__init__(paths)

		#collect
		self.required_name = {}
		self.required_type = {}
		self.optional_name = {}
		self.optional_type = {}
		self.optional_default = {}

		for field in self.data:

			try:
				field['required_name']
			except KeyError as err:
				raise ExceptionNoField('required_name') from err

			try:
				field['required_type']
			except KeyError as err:
				raise ExceptionNoField('required_type') from err

			if len(field['required_name']) != len(field['required_type']):
				raise ExceptionRequiredDiffSizes(field['required_name'], field['required_type'])

			for value in field['required_type']:
				db.ExclusiveDatabase().get_required_types().check_type(value)

			self.required_name.update({field['name']: field['required_name']})
			self.required_type.update({field['name']: field['required_type']})

			if 'optional_name' in field:

				try:
					field['optional_type']
				except KeyError as err:
					raise ExceptionNoField('optional_type') from err

				try:
					field['optional_default']
				except KeyError as err:
					raise ExceptionNoField('optional_default') from err

				if len(field['optional_name']) != len(field['optional_type']):
					raise ExceptionRequiredDiffSizes(field['optional_name'], field['optional_type'])

				if len(field['optional_name']) != len(field['optional_default']):
					raise ExceptionRequiredDiffSizes(field['optional_name'], field['optional_default'])

				for value in field['optional_type']:
					db.ExclusiveDatabase().get_required_types().check_type(value)

				for value in field['optional_default']:
					i = field['optional_default'].index(value)

					db.ExclusiveDatabase().get_required_types().check_value(
						field['optional_type'][i],
						value
					)

				self.optional_name.update({field['name']: field['optional_name']})
				self.optional_type.update({field['name']: field['optional_type']})
				self.optional_default.update({field['name']: field['optional_default']})

	def get_required_name(self, value):

		'''Get names of required fields in conditions for a given data type.'''

		try:
			return self.required_name[value]
		except KeyError as err:
			raise ExceptionUnknownType(value) from err

	def get_required_type(self, value):

		'''Get types of required fields in conditions for a given data type.'''

		try:
			return self.required_type[value]
		except KeyError as err:
			raise ExceptionUnknownType(value) from err

	def get_required_type_by_name(self, valueA, valueB):

		'''Get type of required field in conditions for a given data type and condition name.'''

		try:
			i = self.required_name[valueA].index(valueB)
			return self.required_type[valueA][i]
		except KeyError as err:
			raise ExceptionUnknownType(valueA) from err

	def get_optional_name(self, value):

		'''Get names of optional fields in conditions for a given data type.'''

		try:
			return self.optional_name[value]
		except KeyError as err:
			raise ExceptionUnknownType(value) from err

	def get_optional_type(self, value):

		'''Get types of optional fields in conditions for a given data type.'''

		try:
			return self.optional_type[value]
		except KeyError as err:
			raise ExceptionUnknownType(value) from err

	def get_optional_type_by_name(self, valueA, valueB):

		'''Get type of optional field in conditions for a given data type and condition name.'''

		try:
			i = self.optional_name[valueA].index(valueB)
			return self.optional_type[valueA][i]
		except KeyError as err:
			raise ExceptionUnknownType(valueA) from err

	def get_optional_default_by_name(self, valueA, valueB):

		'''Get default of optional field in conditions for a given data type and condition name.'''

		try:
			i = self.optional_name[valueA].index(valueB)
			return self.optional_default[valueA][i]
		except KeyError as err:
			raise ExceptionUnknownType(valueA) from err
