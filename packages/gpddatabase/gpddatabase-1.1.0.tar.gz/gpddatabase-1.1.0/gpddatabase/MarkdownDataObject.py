#since object members in this class are created dynamically, disable pylint error with:
#pylint: disable=no-member
class MarkdownDataObject:

	''' Markdown representation of DataObject class.'''

	def convert_to_markdown(self):

		''' Get markdown representation.'''

		output = ''

		output += '# File: ' + self.uuid.convert_to_markdown() + '\n'

		output += '\n' + self.general_info.convert_to_markdown()

		output += '\n' + self.data.convert_to_markdown()

		if len(self.correlation.get_correlation_matrices()) != 0:
			output += '\n' + self.correlation.convert_to_markdown()

		return output
