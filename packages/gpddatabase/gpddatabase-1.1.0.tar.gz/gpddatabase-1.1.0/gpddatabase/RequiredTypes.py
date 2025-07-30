from gpddatabase.Exceptions import ExceptionUnknownType
from gpddatabase.Exceptions import ExceptionWrongType

import gpddatabase as db

class RequiredTypes:

	'''Class defining types of required fields and conversion function. '''

	def __init__(self):

		#define availible values
		self.required_types = {'bool', 'integer', 'float', 'string', 'particle', 'unit'}

	def check_type(self, value):

		'''Check if type exist. If not, raise exception.'''

		if value not in self.required_types:
			raise ExceptionUnknownType(value)

	def check_value(self, valueA, valueB):

		'''Check if given value corresponds to given type.'''

		if valueA == 'bool':
			if not isinstance(valueB, bool):
				raise ExceptionWrongType(valueB)
		elif valueA == 'integer':
			if not isinstance(valueB, int):
				raise ExceptionWrongType(valueB)
		elif valueA == 'float':
			if not isinstance(valueB, float):
				raise ExceptionWrongType(valueB)
		elif valueA == 'string':
			if not isinstance(valueB, str):
				raise ExceptionWrongType(valueB)
		elif valueA == 'particle':
			db.ExclusiveDatabase().get_particle_types().check_type(valueB)
		elif valueA == 'unit':
			db.ExclusiveDatabase().get_unit_types().check_type(valueB)
