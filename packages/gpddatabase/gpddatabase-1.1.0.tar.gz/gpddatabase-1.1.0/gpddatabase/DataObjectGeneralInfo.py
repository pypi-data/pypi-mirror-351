from munch import Munch as munch

from gpddatabase.MarkdownDataObjectGeneralInfo import MarkdownDataObjectGeneralInfo as MarkdownFunctionalities

from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionStringToDate
from gpddatabase.Exceptions import ExceptionWrongType
from gpddatabase.Exceptions import ExceptionWrongLength
from gpddatabase.Exceptions import ExceptionNoRequirement

import gpddatabase as db

from gpddatabase.ParticleTypes import ParticleTypes

class DataObjectGeneralInfo(MarkdownFunctionalities):

	'''Class storing general information.'''

	def __init__(self, data):

		#date
		if 'date' not in data:
			raise ExceptionNoField('date')

		if data['date'] is None:
			raise ExceptionNoField('date')

		try:
			data['date'].fromisoformat('1900-01-01')
		except AttributeError as err:
			raise ExceptionStringToDate(data['date']) from err

		self.date = data['date']

		#data type
		if 'data_type' not in data:
			raise ExceptionNoField('data_type')

		if data['data_type'] is None:
			raise ExceptionNoField('data_type')

		db.ExclusiveDatabase().get_data_types().check_type(data['data_type'])

		self.data_type = data['data_type']

		#pseudodata
		if 'pseudodata' not in data:
			self.pseudodata = False
		else:

			if data['pseudodata'] is None:
				raise ExceptionNoField('data_type')

			if not isinstance(data['pseudodata'], bool):
				raise ExceptionWrongType('pseudodata')

			self.pseudodata = data['pseudodata']

		#collaboration
		if 'collaboration' not in data:
			raise ExceptionNoField('collaboration')

		if data['collaboration'] is None:
			raise ExceptionNoField('collaboration')

		if not isinstance(data['collaboration'], str):
			raise ExceptionWrongType('collaboration')

		if len(data['collaboration']) > 40:
			raise ExceptionWrongLength('collaboration', 40)

		self.collaboration = data['collaboration']

		#reference
		if 'reference' not in data:
			self.reference = None
		else:

			if data['reference'] is None:
				raise ExceptionNoField('reference')

			if not isinstance(data['reference'], str):
				raise ExceptionWrongType('reference')

			if len(data['reference']) > 255:
				raise ExceptionWrongLength('reference', 255)

			self.reference = data['reference']

		#conditions
		if 'conditions' not in data:
			raise ExceptionNoField('conditions')

		if data['conditions'] is None:
			raise ExceptionNoField('conditions')

		self.conditions = munch.toDict(data['conditions'])

		for requirement in db.ExclusiveDatabase().get_data_types().get_required_name(self.data_type):
			if requirement not in self.conditions:

				if requirement == 'hadron_beam_energy':
					self.conditions['hadron_beam_energy'] = 0.001 * ParticleTypes().get_particle(self.conditions['hadron_beam_type']).mass # MeV -> GeV
				else:
					raise ExceptionNoRequirement(requirement)

			else:
				db.ExclusiveDatabase().get_required_types().check_value(
					db.ExclusiveDatabase().get_data_types().get_required_type_by_name(self.data_type, requirement),
					self.conditions[requirement]
				)

		for requirement in db.ExclusiveDatabase().get_data_types().get_optional_name(self.data_type):
			if requirement not in self.conditions:
				self.conditions[requirement] = db.ExclusiveDatabase().get_data_types().get_optional_default_by_name(self.data_type, requirement)

			else:
				db.ExclusiveDatabase().get_required_types().check_value(
					db.ExclusiveDatabase().get_data_types().get_optional_type_by_name(self.data_type, requirement),
					self.conditions[requirement]
				)

		#comment
		if 'comment' not in data:
			self.comment = None
		else:

			if data['comment'] is None:
				raise ExceptionNoField('comment')

			if not isinstance(data['comment'], str):
				raise ExceptionWrongType('comment')

			if len(data['comment']) > 255:
				raise ExceptionWrongLength('comment', 255)

			self.comment = data['comment']

	def get_date(self):

		'''Get date.'''

		return self.date

	def get_data_type(self):

		'''Get data type.'''

		return self.data_type

	def get_pseudodata(self):

		'''Check if pseudodata.'''

		return self.pseudodata

	def get_collaboration(self):

		'''Get collaboration name.'''

		return self.collaboration

	def get_reference(self):

		'''Get reference.'''

		return self.reference

	def get_conditions(self):

		'''Get conditions.'''

		return self.conditions

	def get_comment(self):

		'''Get comment.'''

		return self.comment
