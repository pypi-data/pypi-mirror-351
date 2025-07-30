from particle import Particle
from particle import ParticleNotFound

from gpddatabase.Exceptions import ExceptionUnknownType

class ParticleTypes:

	'''Class defining particle types. Uses python 'particle' library.'''

	def check_type(self, value):

		'''Check if type exist. If not, raise exception.'''

		self.get_particle(value)

	def get_description(self, value):

		'''Get description of a given type.'''

		return self.get_particle(value).name

	def get_particle(self, value):

		'''Get 'Particle' object (see 'particle' library) for a given type.'''

		for particle in Particle.findall(value):
			if particle.name == value:
				return particle

		raise ExceptionUnknownType(value) from ParticleNotFound
