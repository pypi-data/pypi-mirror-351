from gpddatabase.MarkdownDataObjectKinematicBin import MarkdownDataObjectKinematicBin as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionWrongLength
from gpddatabase.Exceptions import ExceptionWrongType
from gpddatabase.Exceptions import ExceptionValuesGEQ

class DataObjectKinematicBin(MarkdownFunctionalities):

	'''Class representing a single kinematic bin.'''

	def __init__(self, data):

		#min max
		if data is None:
			raise ExceptionNoField('bin')

		if len(data) != 2:
			raise ExceptionWrongLength('bin', 2)

		for value in data:

			if (not isinstance(value, int)) and (not isinstance(value, float)):
				raise ExceptionWrongType('bin')

		if data[0] >= data[1]:
			raise ExceptionValuesGEQ(data[0], data[1])

		self.min = data[0]
		self.max = data[1]

	def get_min(self):

		'''Get lower value.'''

		return self.min

	def get_max(self):

		'''Get higher value.'''

		return self.max
