from paida.paida_core.PAbsorber import *
from paida.paida_core.IAnnotation import *
from paida.paida_core.PUtilities import *

class IBaseHistogram:
	#_meps2 = -1.4901161193847656e-08
	_meps2 = -6.0554544523933479e-06

	def __init__(self, title):
		self._annotation = IAnnotation()
		self._annotation.addItem('Title', title, True)
		self._axis = []

	def reset(self):
		self._annotation.reset()

	def annotation(self):
		return self._annotation

	def dimension(self):
		return len(self._axis)

	def entries(self):
		### Must be overridden.
		raise NotImplementedError

	def setTitle(self, title):
		self._annotation.setValue('Title', title)

	def title(self):
		return self._annotation.value('Title')

	def _setOption(self, option):
		self._option = option

	def _getOption(self):
		if self._option == None:
			return None
		else:
			return self._option.copy()

	def _getOptionString(self):
		return optionConstructor(self._option)

	def _setName(self, name):
		self._name = name

	def _getName(self):
		return self._name
