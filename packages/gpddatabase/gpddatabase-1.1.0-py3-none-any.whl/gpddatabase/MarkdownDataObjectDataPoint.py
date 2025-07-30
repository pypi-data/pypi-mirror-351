#since object members in this class are created dynamically, disable pylint error with:
#pylint: disable=no-member
class MarkdownDataObjectDataPoint:

	''' Markdown representation of DataObjectDataPoint class.'''

	def convert_to_markdown(self):

		''' Get markdown representation.'''

		output = ''

		output += '| '

		for value in self.kinematic_values:
			output += str(value) + ' | '

		for i, item in enumerate(self.observables_values):
			output += str(item) + ' | '
			if self.observables_stat_uncertainties:
				output += self.observables_stat_uncertainties.get_uncertainty(i).convert_to_markdown() + ' | '
			else:
				output += "---" + ' | '

			if self.observables_sys_uncertainties:
				output += self.observables_sys_uncertainties.get_uncertainty(i).convert_to_markdown() + ' | '
			else:
				output += "---" + ' | '

		return output
