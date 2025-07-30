class ExceptionNoDataInFile(Exception):

	'''Exception signaling no data in given file.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "No data in file " + self.value

class ExceptionNoField(Exception):

	'''Exception signaling no filed of a given name in yaml file.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Field " + self.value + " is missing"

class ExceptionNotUnique(Exception):

	'''Exception signaling value being not unique.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Value " + self.value + " is not unique"

class ExceptionUnknownType(Exception):

	'''Exception signaling unknown type.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Unknown type " + str(self.value)

class ExceptionWrongType(Exception):

	'''Exception signaling wrong type.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Wrong type of field " + str(self.value)

class ExceptionWrongUUID(Exception):

	'''Exception signaling wrong UUID.'''

	def __str__(self):
		return "UUID must have exactly 8 alphanumeric characters"

class ExceptionWrongLabel(Exception):

	'''Exception signaling wrong label.'''

	def __str__(self):
		return "Label must only have alphanumeric characters and/or '_' character"


class ExceptionNoDirectory(Exception):

	'''Exception signaling field not set.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Directory " + str(self.value) + " does not exist"

class ExceptionNotUniqueUUID(Exception):

	'''Exception signaling not unique UUID.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "UUID of " + str(self.value) + " is not unique"

class ExceptionUnknownUUID(Exception):

	'''Exception signaling unknown UUID.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Unknown UUID " + str(self.value)

class ExceptionStringToDate(Exception):

	'''Exception signaling bad conversion from string to date.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Unable to convert " + str(self.value) + " into date"

class ExceptionWrongLength(Exception):

	'''Exception signaling wrong length of string.'''

	def __init__(self, value1, value2):
		self.value1 = value1
		self.value2 = value2

	def __str__(self):
		return "Field " + str(self.value1) + " exceeds allowed length " + str(self.value2)

class ExceptionNotWritable(Exception):

	'''Exception signaling not writable directory.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Directory " + str(self.value) + " is not writable"

class ExceptionNoRequirement(Exception):

	'''Exception signaling missing field in 'conditions' section.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Field " + str(self.value) + " required by this data type in missing in 'conditions' section"

class ExceptionRequiredDiffSizes(Exception):

	'''Exception signaling different sizes of two objects.'''

	def __init__(self, valueA, valueB):
		self.valueA = valueA
		self.valueB = valueB

	def __str__(self):
		return "Different sizes of " + str(self.valueA) + " and " + str(self.valueB)

class ExceptionUnknownLabel(Exception):

	'''Exception signaling unknown label.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Unknown label " + str(self.value)

class ExceptionWrongCorrelationMatrix(Exception):

	'''Exception signaling wrong correlation matrix.'''

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "Wrong definition of correlation matrix " + str(self.value)

class ExceptionDifferentUnitGroups(Exception):

	'''Exception signaling different data groups.'''

	def __init__(self, valueA, valueB):
		self.valueA = valueA
		self.valueB = valueB

	def __str__(self):
		return "Variable " + str(self.valueA) + " does not belong to variable group of " + str(self.valueB)

class ExceptionValuesGEQ(Exception):

	'''Exception signaling valueA >= valueB'''

	def __init__(self, valueA, valueB):
		self.valueA = valueA
		self.valueB = valueB

	def __str__(self):
		return "Value " + str(self.valueA) + " grater or equal value " + str(self.valueB)

class ExceptionValuesLEQ(Exception):

	'''Exception signaling valueA <= valueB'''

	def __init__(self, valueA, valueB):
		self.valueA = valueA
		self.valueB = valueB

	def __str__(self):
		return "Value " + str(self.valueA) + " smaller or equal value " + str(self.valueB)

class ExceptionValuesGT(Exception):

	'''Exception signaling valueA > valueB'''

	def __init__(self, valueA, valueB):
		self.valueA = valueA
		self.valueB = valueB

	def __str__(self):
		return "Value " + str(self.valueA) + " grater than value " + str(self.valueB)

class ExceptionValuesLT(Exception):

	'''Exception signaling valueA < valueB'''

	def __init__(self, valueA, valueB):
		self.valueA = valueA
		self.valueB = valueB

	def __str__(self):
		return "Value " + str(self.valueA) + " smaller than value " + str(self.valueB)

class ExceptionAsymmetricUnc(Exception):

	'''Exception signaling asymmetric uncertainty.'''

	def __str__(self):
		return "This uncertainty is asymmetric, use different function"
