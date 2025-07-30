import os
from pathlib import Path as path
import yaml
from munch import Munch as munch

from gpddatabase.MarkdownExclusiveDatabase import MarkdownExclusiveDatabase as MarkdownFunctionalities

from gpddatabase.RequiredTypes import RequiredTypes
from gpddatabase.UnitGroupTypes import UnitGroupTypes
from gpddatabase.UnitTypes import UnitTypes
from gpddatabase.VariableTypes import VariableTypes
from gpddatabase.DataTypes import DataTypes
from gpddatabase.ParticleTypes import ParticleTypes
from gpddatabase.ObservableTypes import ObservableTypes

from gpddatabase.DataObject import DataObject
from gpddatabase.DataObjectUUID import DataObjectUUID

from gpddatabase.Exceptions import ExceptionNoDirectory
from gpddatabase.Exceptions import ExceptionNoField
from gpddatabase.Exceptions import ExceptionNotUniqueUUID
from gpddatabase.Exceptions import ExceptionUnknownUUID

class ExclusiveDatabase(MarkdownFunctionalities):

	'''Main class representing the database. It is designed to be the singleton.'''

	instance = None

	def __new__(cls):

		#check if instance set
		if cls.instance is None:

			#create
			cls.instance = super(ExclusiveDatabase, cls).__new__(cls)

			#get path
			module_path = os.path.dirname(os.path.abspath(__file__))

			#initialisation
			cls.path_unit_group_types = module_path + '/data/types/unit_group_types.yaml'
			cls.path_unit_types = module_path + '/data/types/unit_types.yaml'
			cls.path_variable_types = module_path + '/data/types/variable_types.yaml'
			cls.path_data_types = module_path + '/data/types/data_types.yaml'
			cls.path_observable_types = module_path + '/data/types/observable_types.yaml'

         	#use ':' to specify multiple paths
			cls.path_data = module_path + '/data/DVCS' + ':' + module_path + '/data/latticeQCD' + ':' + module_path + '/data/other'

			#define and load types
			cls.required_types = None
			cls.unit_group_types = None
			cls.unit_types = None
			cls.variable_types = None
			cls.data_types = None
			cls.particle_types = None
			cls.observable_types = None

			cls.read_types(cls)

			#read uuids
			cls.files = None

			cls.read_uuids(cls)

		#return
		return cls.instance

	def read_types(self):

		'''Load database.'''

		self.required_types = RequiredTypes()
		self.unit_group_types = UnitGroupTypes(self.path_unit_group_types)
		self.unit_types = UnitTypes(self.path_unit_types)
		self.variable_types = VariableTypes(self.path_variable_types)
		self.data_types = DataTypes(self.path_data_types)
		self.particle_types = ParticleTypes()
		self.observable_types = ObservableTypes(self.path_observable_types)

		print("loading types... done")

	def read_uuids(self):

		'''Get list of availible database files.'''

		#clear
		self.files = {}

		#loop over directories
		for directory in self.path_data.split(":"):

			#check if directory exist
			if not path(directory).is_dir():
				raise ExceptionNoDirectory(directory)

			#get list of yaml files (recursively)
			files = path(directory).glob('**/*.yaml')

			#loop over files
			for file in files:

				#read
				with open(str(file), 'r', encoding="utf-8") as f:
					rawData = yaml.safe_load(f)

				data = munch.fromDict(rawData)

				#check
				if 'uuid' not in data:
					raise ExceptionNoField('uuid')

				uuid = DataObjectUUID(data['uuid']).get_uuid()

				#check if exist
				if uuid in self.files:
					raise ExceptionNotUniqueUUID(str(file))

				#save
				self.files.update({uuid: str(file)})

		print("loading uuids... done")

	def get_uuids(self):

		'''Get list of availible uuids.'''

		return list(self.files.keys())

	def get_data_object(self, uuid):

		'''Get DataObject corresponding to given UUID'''

		#look for path
		if uuid not in self.files:
			raise ExceptionUnknownUUID(uuid)

		#get path
		path_to_file = self.files[uuid]

		#read
		with open(path_to_file, 'r', encoding="utf-8") as f:
			rawData = yaml.safe_load(f)

		data = munch.fromDict(rawData)

		return DataObject(data)

	def get_path_to_unit_group_types(self):

		'''Get path to yaml file defining unit group types.'''

		return self.path_unit_group_types

	def get_path_to_unit_types(self):

		'''Get path to yaml file defining unit types.'''

		return self.path_unit_types

	def get_path_to_variable_types(self):

		'''Get path to yaml file defining variable types.'''

		return self.path_variable_types

	def get_path_to_data_types(self):

		'''Get path to yaml file defining data types.'''

		return self.path_data_types

	def get_path_to_observable_types(self):

		'''Get path to yaml file defining observable types.'''

		return self.path_observable_types

	def get_path_to_databse(self):

		'''Get path to database files.'''

		return self.path_data

	def set_path_to_unit_group_types(self, path_to_file):

		'''Set path to yaml file defining unit group types (triggers reloading database).'''

		self.path_unit_group_types = path_to_file
		self.read_types()

	def set_path_to_unit_types(self, path_to_file):

		'''Set path to yaml file defining unit types (triggers reloading database).'''

		self.path_unit_types = path_to_file
		self.read_types()

	def set_path_to_variable_types(self, path_to_file):

		'''Set path to yaml file defining variable types (triggers reloading database).'''

		self.path_variable_types = path_to_file
		self.read_types()

	def set_path_to_data_types(self, path_to_file):

		'''Set path to yaml file defining data types (triggers reloading database).'''

		self.path_data_types = path_to_file
		self.read_types()

	def set_path_to_observable_types(self, path_to_file):

		'''Set path to yaml file defining observable types (triggers reloading database).'''

		self.path_observable_types = path_to_file
		self.read_types()

	def set_path_to_databse(self, path_to_file):

		'''Set specific path to database files. After setting the path the list of availible files is automatically updated.'''

		self.path_data = path_to_file
		self.read_uuids()

	def get_required_types(self):

		'''Get object defining types of required attributes.'''

		return self.required_types

	def get_unit_group_types(self):

		'''Get object defining unit group types.'''

		return self.unit_group_types

	def get_unit_types(self):

		'''Get object defining unit types.'''

		return self.unit_types

	def get_variable_types(self):

		'''Get object defining variable types.'''

		return self.variable_types

	def get_data_types(self):

		'''Get object defining data types.'''

		return self.data_types

	def get_particle_types(self):

		'''Get object defining particle types.'''

		return self.particle_types

	def get_observable_types(self):

		'''Get object defining observable types.'''

		return self.observable_types
