#since object members in this class are created dynamically, disable pylint error with:
#pylint: disable=no-member
class MarkdownDataObjectCorrelationMatrix:

	''' Markdown representation of MarkdownDataObjectCorrelationMatrix class.'''

	def convert_to_markdown(self):

		''' Get markdown representation.'''

		return self.label + str(self.correlation_matrix)
