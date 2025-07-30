from gpddatabase.GenericTypes import GenericTypes

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionUnknownType

import gpddatabase as db

class VariableTypes(GenericTypes):

	'''Class stroring variable types'''

	def __init__(self, paths):

		#run parent constructor
		super().__init__(paths)

		#collect
		self.unit_groups = {}

		for field in self.data:

			try:
				field['unit_group']
			except KeyError as err:
				raise ExceptionNoField('unit_group') from err

			db.ExclusiveDatabase().get_unit_group_types().check_type(field['unit_group'])

			self.unit_groups.update({field['name']: field['unit_group']})

	def get_unit_group(self, value):

		'''Get unit group of a given variable.'''

		try:
			return self.unit_groups[value]
		except KeyError as err:
			raise ExceptionUnknownType(value) from err
