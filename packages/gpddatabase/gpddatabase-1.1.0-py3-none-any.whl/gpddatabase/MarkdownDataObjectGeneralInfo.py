#since object members in this class are created dynamically, disable pylint error with:
#pylint: disable=no-member
class MarkdownDataObjectGeneralInfo:

	''' Markdown representation of DataObjectGeneralInfo class.'''

	def convert_to_markdown(self):

		''' Get markdown representation.'''

		output = ''

		output += '## General information:' + '\n'
		output += '\n'
		output += '* date: ' + str(self.date) + '\n'
		output += '* data type: ' + self.data_type + '\n'
		output += '* pseudodata: ' + ('true' if self.pseudodata else 'false') + '\n'
		output += '* collaboration: ' + self.collaboration + '\n'
		if self.reference:
			output += '* reference: ' + self.reference + '\n'

		output += '* conditions: ' + '\n'
		for condition in self.conditions:
			output += '   * ' + str(condition).replace("_", " ") + ': ' + str(self.conditions[condition]) + '\n'

		if self.comment:
			output += '* comment: ' + self.comment + '\n'

		return output
