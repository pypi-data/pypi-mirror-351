from gpddatabase.MarkdownDataObjectKinematics import MarkdownDataObjectKinematics as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionNotUnique
from gpddatabase.Exceptions import ExceptionRequiredDiffSizes
from gpddatabase.Exceptions import ExceptionDifferentUnitGroups
from gpddatabase.Exceptions import ExceptionWrongType

import gpddatabase as db

from gpddatabase.DataObjectUncertaintySet import DataObjectUncertaintySet
from gpddatabase.DataObjectKinematicBin import DataObjectKinematicBin
from gpddatabase.DataObjectReplicaSet import DataObjectReplicaSet

class DataObjectKinematics(MarkdownFunctionalities):

	'''Class representing a data kinematics.'''

	def __init__(self, data):

		#get names of variables
		self.names = []

		if 'name' not in data:
			raise ExceptionNoField('name')

		if data['name'] is None:
			raise ExceptionNoField('name')

		for name in data['name']:

			db.ExclusiveDatabase().get_variable_types().check_type(name)

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

			if db.ExclusiveDatabase().get_variable_types().get_unit_group(name) != db.ExclusiveDatabase().get_unit_types().get_unit_group(unit):
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

		#get unc
		self.uncertainties = []

		if 'unc' in data:

			if data['unc'] is None:
				raise ExceptionNoField('unc')

			for uncertainty_set_raw in data['unc']:

				uncertainty_set = DataObjectUncertaintySet(uncertainty_set_raw)

				if len(uncertainty_set.get_uncertainties()) != len(self.names):
					raise ExceptionRequiredDiffSizes(uncertainty_set.get_uncertainties(), self.names)

				self.uncertainties.append(uncertainty_set)

			if len(self.uncertainties) != len(self.values):
				raise ExceptionRequiredDiffSizes(self.uncertainties, self.values)

		#get bins
		self.bins = []

		if 'bin' in data:

			if data['bin'] is None:
				raise ExceptionNoField('bin')

			for bins in data['bin']:

				this_bins = []

				if len(bins) != len(self.names):
					raise ExceptionRequiredDiffSizes(bins, self.names)

				for this_bin in bins:
					this_bins.append(DataObjectKinematicBin(this_bin))

				self.bins.append(this_bins)

			if len(self.bins) != len(self.values):
				raise ExceptionRequiredDiffSizes(self.bins, self.values)

		#get replicas
		self.replicas = []

		if 'replica' in data:

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

	def get_uncertainties(self):

		'''Get uncertainties.'''

		return self.uncertainties

	def get_bins(self):

		'''Get bins.'''

		return self.bins

	def get_replicas(self):

		'''Get replicas.'''

		return self.replicas
