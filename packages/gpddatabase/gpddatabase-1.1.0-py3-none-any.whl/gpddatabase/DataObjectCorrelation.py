from gpddatabase.MarkdownDataObjectCorrelation import MarkdownDataObjectCorrelation as MarkdownFunctionalities

from gpddatabase.DataObjectCorrelationMatrix import DataObjectCorrelationMatrix

from gpddatabase.Exceptions import ExceptionUnknownLabel

class DataObjectCorrelation(MarkdownFunctionalities):

	'''Class representing a set of correlation matrices.'''

	def __init__(self, data):

		#get
		self.correlation_matrices = {}

		for rawMatrix in data:

			matrix = DataObjectCorrelationMatrix(rawMatrix)
			self.correlation_matrices.update({matrix.get_label(): matrix.get_correlation_matrix()})

	def get_correlation_matrices(self):

		'''Get all correlation matrices.'''

		return self.correlation_matrices

	def get_correlation_matrix_labels(self):

		'''Get correlation matrix labels.'''

		return list(self.correlation_matrices.keys())

	def get_correlation_matrix(self, label):

		'''Get a given correlation matrix by label.'''

		if label not in self.correlation_matrices:
			raise ExceptionUnknownLabel(label)

		return self.correlation_matrices[label]
