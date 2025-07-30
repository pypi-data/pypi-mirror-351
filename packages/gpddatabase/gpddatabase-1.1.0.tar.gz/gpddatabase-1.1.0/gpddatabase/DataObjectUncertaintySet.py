from gpddatabase.MarkdownDataObjectUncertaintySet import MarkdownDataObjectUncertaintySet as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionValuesLEQ
from gpddatabase.Exceptions import ExceptionValuesGEQ

from gpddatabase.DataObjectUncertainty import DataObjectUncertainty

class DataObjectUncertaintySet(MarkdownFunctionalities):

	'''Class representing a set of uncertainties including correlation matrix.'''

	def __init__(self, data):

		#values
		self.uncertainties = []

		if isinstance(data[0], str):

			offset = 1
			self.correlation_matrix = data[0]

		else:

			offset = 0
			self.correlation_matrix = None

		for uncertainty in data[offset:]:
			self.uncertainties.append(DataObjectUncertainty(uncertainty))

	def get_uncertainties(self):

		'''Get uncertainties.'''

		return self.uncertainties

	def get_correlation_matrix(self):

		'''Get correlation matrix.'''

		return self.correlation_matrix

	def get_number_of_uncertainties(self):

		'''Get number of stored uncertainties.'''

		return len(self.uncertainties)

	def get_uncertainty(self, i):

		'''Get a single uncertainty.'''

		#check index
		if i < 0:
			raise ExceptionValuesLEQ(i, -1)

		if i >= len(self.uncertainties):
			raise ExceptionValuesGEQ(i, len(self.uncertainties))

		return self.uncertainties[i]
