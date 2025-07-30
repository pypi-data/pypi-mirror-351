from gpddatabase.MarkdownDataObject import MarkdownDataObject as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionUnknownLabel

from gpddatabase.DataObjectUUID import DataObjectUUID
from gpddatabase.DataObjectGeneralInfo import DataObjectGeneralInfo
from gpddatabase.DataObjectData import DataObjectData
from gpddatabase.DataObjectCorrelation import DataObjectCorrelation

class DataObject(MarkdownFunctionalities):

	'''Class representing a single data file.'''

	def __init__(self, data):

		#read uuid
		if 'uuid' not in data:
			raise ExceptionNoField('uuid')

		self.uuid = DataObjectUUID(data['uuid'])

		#read general info
		if 'general_info' not in data:
			raise ExceptionNoField('general_info')

		self.general_info = DataObjectGeneralInfo(data['general_info'])

		#read correlation
		if 'correlation' not in data:
			self.correlation = DataObjectCorrelation({})
		else:
			self.correlation = DataObjectCorrelation(data['correlation'])

		#read data
		if 'data' not in data:
			raise ExceptionNoField('data')

		self.data = DataObjectData(data['data'])

		#check labels of correlation matrices
		for data_set in self.data.get_data_sets():

			if self.data.get_data_sets()[data_set].get_kinematics().get_uncertainties():
				for uncertainty in self.data.get_data_sets()[data_set].get_kinematics().get_uncertainties():
					label = uncertainty.get_correlation_matrix()
					if label is not None:
						if label not in self.correlation.get_correlation_matrices():
							raise ExceptionUnknownLabel(label)

			if self.data.get_data_sets()[data_set].get_observables().get_stat_uncertainties():
				for uncertainty in self.data.get_data_sets()[data_set].get_observables().get_stat_uncertainties():
					label = uncertainty.get_correlation_matrix()
					if label is not None:
						if label not in self.correlation.get_correlation_matrices():
							raise ExceptionUnknownLabel(label)

			if self.data.get_data_sets()[data_set].get_observables().get_sys_uncertainties():
				for uncertainty in self.data.get_data_sets()[data_set].get_observables().get_sys_uncertainties():
					label = uncertainty.get_correlation_matrix()
					if label is not None:
						if label not in self.correlation.get_correlation_matrices():
							raise ExceptionUnknownLabel(label)

			if self.data.get_data_sets()[data_set].get_observables().get_sys_uncertainties_contribution():
				for uncertainties in self.data.get_data_sets()[data_set].get_observables().get_sys_uncertainties_contribution():
					for uncertainty in uncertainties:
						label = uncertainty.get_correlation_matrix()
						if label is not None:
							if label not in self.correlation.get_correlation_matrices():
								raise ExceptionUnknownLabel(label)

			if self.data.get_data_sets()[data_set].get_observables().get_norm_uncertainties():
				label = self.data.get_data_sets()[data_set].get_observables().get_norm_uncertainties().get_correlation_matrix()
				if label is not None:
					if label not in self.correlation.get_correlation_matrices():
						raise ExceptionUnknownLabel(label)

			if self.data.get_data_sets()[data_set].get_observables().get_norm_uncertainties_contribution():
				for uncertainty in self.data.get_data_sets()[data_set].get_observables().get_norm_uncertainties_contribution():
					label = uncertainty.get_correlation_matrix()
					if label is not None:
						if label not in self.correlation.get_correlation_matrices():
							raise ExceptionUnknownLabel(label)

	def get_uuid(self):

		'''Get UUID data object.'''

		return self.uuid

	def get_general_info(self):

		'''Get general information data object.'''

		return self.general_info

	def get_correlation(self):

		'''Get general information data object.'''

		return self.correlation

	def get_data(self):

		'''Get data object.'''

		return self.data
