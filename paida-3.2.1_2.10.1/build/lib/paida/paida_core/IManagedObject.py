from paida.paida_core.PAbsorber import *
class IManagedObject:
	def __init__(self, name, parent = None, instance = None):
		self._name = name
		self._parent = parent
		self._instance = instance
		self._children = []
		self._tree = None

	def name(self):
		return self._name
