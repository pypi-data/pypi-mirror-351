from gpddatabase.MarkdownDataObjectUncertainty import MarkdownDataObjectUncertainty as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionValuesLT
from gpddatabase.Exceptions import ExceptionWrongLength
from gpddatabase.Exceptions import ExceptionWrongType
from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionAsymmetricUnc

class DataObjectUncertainty(MarkdownFunctionalities):

	'''Class representing a single uncertainty.'''

	def __init__(self, data):

		#get
		if data is None:
			raise ExceptionNoField('unc')

		if isinstance(data, (int, float)):

			if data < 0.:
				raise ExceptionValuesLT(data, 0.)

			self.unc_lower = data
			self.unc_upper = data

		elif isinstance(data, list):

			if len(data) != 2:
				raise ExceptionWrongLength('unc', 2)

			for value in data:

				if (not isinstance(value, int)) and (not isinstance(value, float)):
					raise ExceptionWrongType('unc')

				if value < 0.:
					raise ExceptionValuesLT(value, 0.)

			if len(data) == 2:
				self.unc_lower = data[0]
				self.unc_upper = data[1]

		else:

			raise ExceptionWrongType('unc')

	def get_unc_lower(self):

		'''Get lower value of uncertainty.'''

		return self.unc_lower

	def get_unc_upper(self):

		'''Get upper value of uncertainty.'''

		return self.unc_upper

	def is_asymmetric(self):

		'''Returns true is uncertainty asymmetric.'''

		return self.unc_lower != self.unc_upper

	def get_unc(self):

		'''Get value of uncertainty. If asymmetric exception will be raised.'''

		if self.is_asymmetric():
			raise ExceptionAsymmetricUnc()

		return self.unc_upper
