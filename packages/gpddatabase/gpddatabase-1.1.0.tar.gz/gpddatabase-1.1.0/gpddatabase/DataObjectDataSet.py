from gpddatabase.MarkdownDataObjectDataSet import MarkdownDataObjectDataSet as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionRequiredDiffSizes
from gpddatabase.Exceptions import ExceptionValuesLEQ
from gpddatabase.Exceptions import ExceptionValuesGEQ

from gpddatabase.DataObjectKinematics import DataObjectKinematics
from gpddatabase.DataObjectObservable import DataObjectObservable
from gpddatabase.DataObjectDataPoint import DataObjectDataPoint

class DataObjectDataSet(MarkdownFunctionalities):

	'''Class representing a single data set.'''

	def __init__(self, data, label):

		#label
		self.label = label

		#kinematics
		if 'kinematics' not in data:
			raise ExceptionNoField('kinematics')

		self.kinematics = DataObjectKinematics(data['kinematics'])

		#observables
		if 'observable' not in data:
			raise ExceptionNoField('observable')

		self.observables = DataObjectObservable(data['observable'])

		#check number of points in both sets
		if len(self.kinematics.get_values()) != len(self.observables.get_values()):
			raise ExceptionRequiredDiffSizes(self.kinematics.get_values(), self.observables.get_values())

	def get_label(self):

		'''Get label.'''

		return self.label

	def get_kinematics(self):

		'''Get object representing kinematics.'''

		return self.kinematics

	def get_observables(self):

		'''Get object representing observables.'''

		return self.observables

	def get_number_of_data_points(self):

		'''Get number of data points.'''

		return len(self.kinematics.get_values())

	def get_data_point(self, i):

		'''Get a single data point.'''

		#check index
		if i < 0:
			raise ExceptionValuesLEQ(i, -1)

		if i >= len(self.kinematics.get_values()):
			raise ExceptionValuesGEQ(i, len(self.kinematics.get_values()))

		return DataObjectDataPoint(
			self.label,

			self.kinematics.get_names(),
			self.kinematics.get_units(),
			self.kinematics.get_values()[i],
			self.kinematics.get_uncertainties()[i] if self.kinematics.get_uncertainties() else None,
			self.kinematics.get_bins()[i] if self.kinematics.get_bins() else None,
			self.kinematics.get_replicas()[i] if self.kinematics.get_replicas() else None,

			self.observables.get_names(),
			self.observables.get_units(),
			self.observables.get_values()[i],
			self.observables.get_stat_uncertainties()[i] if self.observables.get_stat_uncertainties() else None,
			self.observables.get_sys_uncertainties()[i] if self.observables.get_sys_uncertainties() else None,
			self.observables.get_sys_uncertainties_contribution_labels() if self.observables.get_sys_uncertainties_contribution_labels() else None,
			self.observables.get_sys_uncertainties_contribution()[i] if self.observables.get_sys_uncertainties_contribution() else None,
			self.observables.get_norm_uncertainties() if self.observables.get_norm_uncertainties() else None,
			self.observables.get_norm_uncertainties_contribution_labels() if self.observables.get_norm_uncertainties_contribution_labels() else None,
			self.observables.get_norm_uncertainties_contribution() if self.observables.get_norm_uncertainties_contribution() else None,
			self.observables.get_replicas()[i] if self.observables.get_replicas() else None
			)
