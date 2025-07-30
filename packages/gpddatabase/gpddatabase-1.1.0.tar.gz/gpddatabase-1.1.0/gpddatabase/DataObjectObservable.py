from gpddatabase.MarkdownDataObjectObservable import MarkdownDataObjectObservable as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionNotUnique
from gpddatabase.Exceptions import ExceptionRequiredDiffSizes
from gpddatabase.Exceptions import ExceptionDifferentUnitGroups
from gpddatabase.Exceptions import ExceptionWrongType
from gpddatabase.Exceptions import ExceptionWrongLength
from gpddatabase.Exceptions import ExceptionWrongLabel

import gpddatabase as db

from gpddatabase.DataObjectUncertaintySet import DataObjectUncertaintySet
from gpddatabase.DataObjectReplicaSet import DataObjectReplicaSet

class DataObjectObservable(MarkdownFunctionalities):

	'''Class representing collection of data observables.'''

	def __init__(self, data):

		#get names of variables
		self.names = []

		if 'name' not in data:
			raise ExceptionNoField('name')

		if data['name'] is None:
			raise ExceptionNoField('name')

		for name in data['name']:

			db.ExclusiveDatabase().get_observable_types().check_type(name)

			if name in self.names:
				raise ExceptionNotUnique(name)

			self.names.append(name)

		#get units
		self.units = []

		if 'unit' not in data:
			raise ExceptionNoField('unit')

		if data['unit'] is None:
			raise ExceptionNoField('unit')

		if len(data['name']) != len(data['unit']):
			raise ExceptionRequiredDiffSizes(data['name'], data['unit'])

		for unit in data['unit']:
			db.ExclusiveDatabase().get_unit_types().check_type(unit)

		for name, unit in zip(data['name'], data['unit']):

			if db.ExclusiveDatabase().get_observable_types().get_unit_group(name) != db.ExclusiveDatabase().get_unit_types().get_unit_group(unit):
				raise ExceptionDifferentUnitGroups(name, unit)

			self.units.append(unit)

		#get values
		self.values = []

		if 'value' not in data:
			raise ExceptionNoField('value')

		if data['value'] is None:
			raise ExceptionNoField('value')

		for point in data['value']:

			if len(point) != len(self.names):
				raise ExceptionRequiredDiffSizes(point, self.names)

			for value in point:
				if (not isinstance(value, int)) and (not isinstance(value, float)):
					raise ExceptionWrongType('value')

			self.values.append(point)

		#get norm unc
		if 'norm_unc' not in data:
			self.norm_uncertainties = None
		else:

			if data['norm_unc'] is None:
				raise ExceptionNoField('norm_unc')

			self.norm_uncertainties = DataObjectUncertaintySet(data['norm_unc'])

			if len(self.norm_uncertainties.get_uncertainties()) != len(self.names):
				raise ExceptionRequiredDiffSizes(self.norm_uncertainties.get_uncertainties(), self.names)

		#get norm unc contrib labels
		if 'norm_unc_contrib_label' not in data:
			self.norm_uncertainties_contrib_labels = None
		else:

			self.norm_uncertainties_contrib_labels = []

			if data['norm_unc_contrib_label'] is None:
				raise ExceptionNoField('norm_unc_contrib_label')

			labels = data['norm_unc_contrib_label']

			for label in labels:

				if not isinstance(label, str):
					raise ExceptionWrongType('norm_unc_contrib_label')

				if len(label) > 40:
					raise ExceptionWrongLength('norm_unc_contrib_label', 40)

				if not label.replace('_', '').isalnum():
					raise ExceptionWrongLabel(label)

			self.norm_uncertainties_contrib_labels = labels

		#get norm unc contrib contributions
		if 'norm_unc_contrib' not in data:
			self.norm_uncertainties_contrib = None
		else:

			self.norm_uncertainties_contrib = []

			if data['norm_unc_contrib'] is None:
				raise ExceptionNoField('norm_unc_contrib')

			for uncertainty_set_raw in data['norm_unc_contrib']:

				uncertainty_set = DataObjectUncertaintySet(uncertainty_set_raw)

				if len(uncertainty_set.get_uncertainties()) != len(self.norm_uncertainties_contrib_labels):
					raise ExceptionRequiredDiffSizes(uncertainty_set.get_uncertainties(), self.norm_uncertainties_contrib_labels)

				self.norm_uncertainties_contrib.append(uncertainty_set)

			if len(self.norm_uncertainties_contrib) != len(self.names):
				raise ExceptionRequiredDiffSizes(self.norm_uncertainties_contrib, self.names)

		#get stat unc
		if 'stat_unc' not in data:
			self.stat_uncertainties = None
		else:

			self.stat_uncertainties = []

			if data['stat_unc'] is None:
				raise ExceptionNoField('stat_unc')

			for uncertainty_set_raw in data['stat_unc']:

				uncertainty_set = DataObjectUncertaintySet(uncertainty_set_raw)

				if len(uncertainty_set.get_uncertainties()) != len(self.names):
					raise ExceptionRequiredDiffSizes(uncertainty_set.get_uncertainties(), self.names)

				self.stat_uncertainties.append(uncertainty_set)

			if len(self.stat_uncertainties) != len(self.values):
				raise ExceptionRequiredDiffSizes(self.stat_uncertainties, self.values)

		#get sys unc
		if 'sys_unc' not in data:
			self.sys_uncertainties = None
		else:

			self.sys_uncertainties = []

			if data['sys_unc'] is None:
				raise ExceptionNoField('sys_unc')

			for uncertainty_set_raw in data['sys_unc']:

				uncertainty_set = DataObjectUncertaintySet(uncertainty_set_raw)

				if len(uncertainty_set.get_uncertainties()) != len(self.names):
					raise ExceptionRequiredDiffSizes(uncertainty_set.get_uncertainties(), self.names)

				self.sys_uncertainties.append(uncertainty_set)

			if len(self.sys_uncertainties) != len(self.values):
				raise ExceptionRequiredDiffSizes(self.sys_uncertainties, self.values)

		#get sys unc contrib labels
		if 'sys_unc_contrib_label' not in data:
			self.sys_uncertainties_contrib_labels = None
		else:

			self.sys_uncertainties_contrib_labels = []

			if data['sys_unc_contrib_label'] is None:
				raise ExceptionNoField('sys_unc_contrib_label')

			labels = data['sys_unc_contrib_label']

			for label in labels:

				if not isinstance(label, str):
					raise ExceptionWrongType('sys_unc_contrib_label')

				if len(label) > 40:
					raise ExceptionWrongLength('sys_unc_contrib_label', 40)

				if not label.replace('_', '').isalnum():
					raise ExceptionWrongLabel(label)

			self.sys_uncertainties_contrib_labels = labels

		#get sys unc contrib
		if 'sys_unc_contrib' not in data:
			self.sys_uncertainties_contrib = None
		else:

			self.sys_uncertainties_contrib = []

			if data['sys_unc_contrib'] is None:
				raise ExceptionNoField('sys_unc_contrib')

			for uncertainty_set_set_raw in data['sys_unc_contrib']:

				uncertainty_set_set = []

				if isinstance(uncertainty_set_set_raw[0], str):

					uncertainty_set = DataObjectUncertaintySet(uncertainty_set_set_raw)

					if len(uncertainty_set.get_uncertainties()) != (len(self.sys_uncertainties_contrib_labels) * len(self.names)):
						raise ExceptionRequiredDiffSizes(uncertainty_set.get_uncertainties(), (len(self.sys_uncertainties_contrib_labels) * len(self.names)))

					uncertainty_set_set.append(uncertainty_set)

				else:

					for uncertainty_set_raw in uncertainty_set_set_raw:

						uncertainty_set = DataObjectUncertaintySet(uncertainty_set_raw)

						if len(uncertainty_set.get_uncertainties()) != len(self.sys_uncertainties_contrib_labels):
							raise ExceptionRequiredDiffSizes(uncertainty_set.get_uncertainties(), self.sys_uncertainties_contrib_labels)

						uncertainty_set_set.append(uncertainty_set)

					if len(uncertainty_set_set) != len(self.names):
						raise ExceptionRequiredDiffSizes(uncertainty_set_set, self.names)

				self.sys_uncertainties_contrib.append(uncertainty_set_set)

			if len(self.sys_uncertainties_contrib) != len(self.values):
				raise ExceptionRequiredDiffSizes(self.sys_uncertainties_contrib, self.values)

		#get replicas
		if 'replica' not in data:
			self.replicas = None
		else:

			self.replicas = []

			if data['replica'] is None:
				raise ExceptionNoField('replica')

			for replicas in data['replica']:

				this_replicas = []

				if len(replicas) != len(self.names):
					raise ExceptionRequiredDiffSizes(replicas, self.names)

				for replica in replicas:
					this_replicas.append(DataObjectReplicaSet(replica))

				self.replicas.append(this_replicas)

			if len(self.replicas) != len(self.values):
				raise ExceptionRequiredDiffSizes(self.replicas, self.values)

	def get_names(self):

		'''Get names of variables.'''

		return self.names

	def get_units(self):

		'''Get names and units.'''

		return self.units

	def get_values(self):

		'''Get values.'''

		return self.values

	def get_stat_uncertainties(self):

		'''Get statistical uncertainties.'''

		return self.stat_uncertainties

	def get_sys_uncertainties(self):

		'''Get systematic uncertainties.'''

		return self.sys_uncertainties

	def get_sys_uncertainties_contribution_labels(self):

		'''Get labels of contributions to systematic uncertainties.'''

		return self.sys_uncertainties_contrib_labels

	def get_sys_uncertainties_contribution(self):

		'''Get contributions to systematic uncertainties.'''

		return self.sys_uncertainties_contrib

	def get_norm_uncertainties(self):

		'''Get normalisation uncertainties.'''

		return self.norm_uncertainties

	def get_norm_uncertainties_contribution_labels(self):

		'''Get labels of contributions to normalisation uncertainties.'''

		return self.norm_uncertainties_contrib_labels

	def get_norm_uncertainties_contribution(self):

		'''Get contributions to normalisation uncertainties.'''

		return self.norm_uncertainties_contrib

	def get_replicas(self):

		'''Get replicas.'''

		return self.replicas
