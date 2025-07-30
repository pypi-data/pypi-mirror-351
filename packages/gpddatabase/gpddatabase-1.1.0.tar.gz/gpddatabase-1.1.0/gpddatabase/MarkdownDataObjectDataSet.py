#since object members in this class are created dynamically, disable pylint error with:
#pylint: disable=no-member
class MarkdownDataObjectDataSet:

	''' Markdown representation of DataObjectDataSet class.'''

	def convert_to_markdown(self):

		''' Get markdown representation.'''

		output = ''
		additional_info = ''
		table_line = ''
		unit_line = ''
		scale_line = ''

		output += '### Data set: ' + self.label + '\n'

		output += '\n'

		# rather than running
		# output += self.kinematics.convert_to_markdown()
		# output += self.observables.convert_to_markdown()
		# we loop over data points

		if self.kinematics.get_uncertainties():
			additional_info += '* uncertainties of kinematic values' + '\n'
		if self.kinematics.get_replicas():
			additional_info += '* replica values for kinematics' + '\n'
		if self.kinematics.get_bins():
			additional_info += '* boundaries of kinematic bins' + '\n'
		if self.observables.get_norm_uncertainties_contribution():
			additional_info += '* contributions to normalisation uncertainties' + '\n'
		if self.observables.get_sys_uncertainties_contribution():
			additional_info += '* contributions to systematic uncertainties' + '\n'
		if self.observables.get_replicas():
			additional_info += '* replica values for observables' + '\n'
		if self.observables.get_norm_uncertainties():
			additional_info += '* correlation between normalisation uncertainties' + '\n'

		if self.observables.get_stat_uncertainties():

			hasStatCorr = False

			for uncertainty_set in self.observables.get_stat_uncertainties():
				if uncertainty_set.get_correlation_matrix():
					hasStatCorr = True
					break

			if hasStatCorr:
				additional_info += '* correlation between statistical uncertainties' + '\n'

		if self.observables.get_sys_uncertainties():

			hasStatCorr = False

			for uncertainty_set in self.observables.get_sys_uncertainties():
				if uncertainty_set.get_correlation_matrix():
					hasStatCorr = True
					break

			if hasStatCorr:
				additional_info += '* correlation between systematic uncertainties' + '\n'

		if additional_info != '':
			output += 'Additional information availible:' + '\n'
			output += additional_info


		output += '\n'

		output += 'Table of values:' + '\n'

		output += '\n'

		output += '| | '
		table_line += '| --- | '
		unit_line += '| unit: | '
		if self.observables.get_norm_uncertainties():
			scale_line += '| norm unc.: | '

		for name, unit in zip(self.kinematics.get_names(), self.kinematics.get_units()):
			output += name + ' | '
			table_line += ':---:' + ' | '
			unit_line += unit + ' | '
			if self.observables.get_norm_uncertainties():
				scale_line += ' ' + ' | '

		for name, unit in zip(self.observables.get_names(), self.observables.get_units()):
			output += name + ' | stat | sys | '
			table_line += ':---:' + ' | :---: | :---: | '
			unit_line += unit + ' | ' + unit + ' | ' + unit + ' | '

		if self.observables.get_norm_uncertainties():
			for i in range(0, self.observables.get_norm_uncertainties().get_number_of_uncertainties()):
				scale_line += self.observables.get_norm_uncertainties().get_uncertainty(i).convert_to_markdown() + ' |  |  | '

		output += '\n' + table_line
		output += '\n' + unit_line
		if self.observables.get_norm_uncertainties():
			output += '\n' + scale_line
		output += '\n'

		for i in range(0, self.get_number_of_data_points()):
			output += '| ' + str(i) + self.get_data_point(i).convert_to_markdown() + '\n'

		output += '\n'

		return output
