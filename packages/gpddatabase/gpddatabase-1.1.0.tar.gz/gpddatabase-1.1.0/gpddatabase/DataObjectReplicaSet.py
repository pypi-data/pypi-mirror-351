from gpddatabase.MarkdownDataObjectReplicaSet import MarkdownDataObjectReplicaSet as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionWrongType

class DataObjectReplicaSet(MarkdownFunctionalities):

	'''Class representing replica set.'''

	def __init__(self, data):

		#values
		self.values = []

		if data is None:
			raise ExceptionNoField('replica')

		for value in data:

			if (not isinstance(value, int)) and (not isinstance(value, float)):
				raise ExceptionWrongType('replica')

			self.values.append(value)

	def get_values(self):

		'''Get replica values.'''

		return self.values
