#since object members in this class are created dynamically, disable pylint error with:
#pylint: disable=no-member
class MarkdownDataObjectData:

	''' Markdown representation of DataObjectData class.'''

	def convert_to_markdown(self):

		''' Get markdown representation.'''

		output = ''

		output += '## Data sets:' + '\n'

		output += '\n'

		for data_set in self.data_sets:
			output += self.data_sets[data_set].convert_to_markdown()

		return output
