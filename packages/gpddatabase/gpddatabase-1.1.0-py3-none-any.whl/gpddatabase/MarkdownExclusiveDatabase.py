from pathlib import Path as path

from gpddatabase.Exceptions import ExceptionNoDirectory
from gpddatabase.Exceptions import ExceptionNotWritable

#since object members in this class are created dynamically, disable pylint error with:
#pylint: disable=no-member
class MarkdownExclusiveDatabase:

	''' Markdown functionalities of ExclusiveDatabase class.'''

	def convert_to_markdown(self, directory):

		''' Get markdown representation.'''

		#result
		output = ''

		output += '# Available datasets' + '\n'
		output += '\n'
		output += '| uuid | collaboration | reference | type | pseudo | observables | comment |' + '\n'
		output += '| ---- | ------------- | --------- | ---- | ------ | ----------- | ------- |' + '\n'

		#check if directory exist
		if not path(directory).is_dir():
			raise ExceptionNoDirectory(directory)

		#loop over all files
		for uuid in self.get_uuids():

			#print status
			print("info: working for: ", uuid)

			#get object
			dataObject = self.get_data_object(uuid)

			#print
			output += '| ' + '[' + uuid + '](' + 'file_' + uuid + '.markdown' + ')'
			output += ' | ' + dataObject.get_general_info().get_collaboration()
			output += ' | ' + dataObject.get_general_info().get_reference()
			output += ' | ' + dataObject.get_general_info().get_data_type()
			output += ' | ' + str(dataObject.get_general_info().get_pseudodata())

			output += ' |'

			observableNames = []

			for label in dataObject.get_data().get_data_set_labels():
				for observableName in dataObject.get_data().get_data_set(label).get_observables().get_names():
					if observableName not in observableNames:
						observableNames.append(observableName)

			for observableName in observableNames:
				output += ' ' + observableName

			output += ' | ' + str(dataObject.get_general_info().get_comment())

			output += ' | ' + '\n'

			#write
			try:

				with open(directory + '/file_' + uuid + '.markdown', 'w', encoding="utf-8") as file:
					print(dataObject.convert_to_markdown(), file=file)

			except FileNotFoundError as err:
				raise ExceptionNotWritable(directory) from err

		#write
		try:

			with open(directory + '/data_sets.markdown', 'w', encoding="utf-8") as file:
				print(output, file=file)

		except FileNotFoundError as err:
			raise ExceptionNotWritable(directory) from err
