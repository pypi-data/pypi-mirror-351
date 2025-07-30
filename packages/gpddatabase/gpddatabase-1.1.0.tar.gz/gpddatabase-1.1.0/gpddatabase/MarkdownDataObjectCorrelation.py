#since object members in this class are created dynamically, disable pylint error with:
#pylint: disable=no-member
class MarkdownDataObjectCorrelation:

	''' Markdown representation of MarkdownDataObjectCorrelation class.'''

	def convert_to_markdown(self):

		''' Get markdown representation.'''

		output = ''

		output += '## Definition of correlation matrices:' + '\n'

		output += '\n'

		for label in self.correlation_matrices:
			output += '* ' +  label + ': ' + '\n'
			output += str(self.correlation_matrices[label]) + '\n'

		return output
