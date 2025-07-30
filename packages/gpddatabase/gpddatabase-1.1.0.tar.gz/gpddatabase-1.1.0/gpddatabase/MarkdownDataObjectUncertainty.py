#since object members in this class are created dynamically, disable pylint error with:
#pylint: disable=no-member
class MarkdownDataObjectUncertainty:

	''' Markdown representation of DataObjectUncertainty class.'''

	def convert_to_markdown(self):

		''' Get markdown representation.'''

		output = ''

		if self.is_asymmetric():
			output += str(self.unc_lower) + '/' + str(self.unc_upper)
		else:
			output += str(self.unc_lower)

		return output
