from gpddatabase.MarkdownDataObjectDataPoint import MarkdownDataObjectDataPoint as MarkdownFunctionalities

class DataObjectDataPoint(MarkdownFunctionalities):

	'''Class representing a single data point.'''

	def __init__(self,
		data_set_label,

		kinematic_names,
		kinematic_units,
		kinematic_values,
		kinematic_uncertainties,
		kinematic_bins,
		kinematic_replicas,

		observables_names,
		observables_units,
		observables_values,
		observables_stat_uncertainties,
		observables_sys_uncertainties,
		observables_sys_uncertainties_contribution_labels,
		observables_sys_uncertainties_contribution,
		observables_norm_uncertainties,
		observables_norm_uncertainties_contribution_labels,
		observables_norm_uncertainties_contribution,
		observables_replicas
		):

		self.data_set_label = data_set_label

		self.kinematic_names = kinematic_names
		self.kinematic_units = kinematic_units
		self.kinematic_values = kinematic_values
		self.kinematic_uncertainties = kinematic_uncertainties
		self.kinematic_bins = kinematic_bins
		self.kinematic_replicas = kinematic_replicas

		self.observables_names = observables_names
		self.observables_units = observables_units
		self.observables_values = observables_values
		self.observables_stat_uncertainties = observables_stat_uncertainties
		self.observables_sys_uncertainties = observables_sys_uncertainties
		self.observables_sys_uncertainties_contribution_labels = observables_sys_uncertainties_contribution_labels
		self.observables_sys_uncertainties_contribution = observables_sys_uncertainties_contribution
		self.observables_norm_uncertainties = observables_norm_uncertainties
		self.observables_norm_uncertainties_contribution_labels = observables_norm_uncertainties_contribution_labels
		self.observables_norm_uncertainties_contribution = observables_norm_uncertainties_contribution
		self.observables_replicas = observables_replicas

	def get_observables_names(self):

		'''Get names of observables.'''

		return self.observables_names

	def get_observables_units(self):

		'''Get units of observables.'''

		return self.observables_units

	def get_observables_values(self):

		'''Get values of observables.'''

		return self.observables_values

	def get_observables_stat_uncertainties(self):

		'''Get statistical uncertainties of observables.'''

		return self.observables_stat_uncertainties

	def get_observables_sys_uncertainties(self):

		'''Get systematic uncertainties of observables.'''

		return self.observables_sys_uncertainties

	def get_observables_sys_uncertainties_contribution_labels(self):

		'''Get labels of contributions to systematic uncertainties of observables.'''

		return self.observables_sys_uncertainties_contribution_labels

	def get_observables_sys_uncertainties_contribution(self):

		'''Get contribution to systematic uncertainties of observables.'''

		return self.observables_sys_uncertainties_contribution

	def get_observables_norm_uncertainties(self):

		'''Get normalisation uncertainties of observables.'''

		return self.observables_norm_uncertainties

	def get_observables_norm_uncertainties_contribution_labels(self):

		'''Get labels of contributions to normalisation uncertainties of observables.'''

		return self.observables_norm_uncertainties_contribution_labels

	def get_observables_norm_uncertainties_contribution(self):

		'''Get contribution to normalisation uncertainties of observables.'''

		return self.observables_norm_uncertainties_contribution

	def get_observables_replicas(self):

		'''Get replicas of observables.'''

		return self.observables_replicas

	def get_data_set_label(self):

		'''Get data set label corresponding to this data point.'''

		return self.data_set_label

	def get_kinematics_names(self):

		'''Get names of kinematic variables.'''

		return self.kinematic_names

	def get_kinematics_units(self):

		'''Get units of kinematic variables.'''

		return self.kinematic_units

	def get_kinematics_values(self):

		'''Get values of kinematic variables.'''

		return self.kinematic_values

	def get_kinematics_uncertainties(self):

		'''Get uncertainties of kinematic variables.'''

		return self.kinematic_uncertainties

	def get_kinematics_bins(self):

		'''Get bins of kinematic variables.'''

		return self.kinematic_bins

	def get_kinematics_replicas(self):

		'''Get replicas of kinematic variables.'''

		return self.kinematic_replicas
