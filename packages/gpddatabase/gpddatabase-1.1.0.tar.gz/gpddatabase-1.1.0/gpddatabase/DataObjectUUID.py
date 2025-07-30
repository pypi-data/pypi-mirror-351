from gpddatabase.MarkdownDataObjectUUID import MarkdownDataObjectUUID as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionWrongType
from gpddatabase.Exceptions import ExceptionWrongUUID

class DataObjectUUID(MarkdownFunctionalities):

	'''Class representing UUID.'''

	def __init__(self, uuid):

		if uuid is None:
			raise ExceptionNoField('uuid')

		if not isinstance(uuid, str):
			raise ExceptionWrongType('uuid')

		if len(uuid) != 8 or (not uuid.isalnum()):
			raise ExceptionWrongUUID()

		self.uuid = uuid

	def get_uuid(self):

		'''Get UUID value.'''

		return self.uuid
