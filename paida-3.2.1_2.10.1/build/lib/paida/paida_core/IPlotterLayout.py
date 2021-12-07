from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import *
from paida.paida_core.IBaseStyle import listedParameter, stringParameter

class IPlotterLayout:
	def __init__(self):
		self._parameters = {}

		self._setType('statisticsBoxAnchor', listedParameter('NE', ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']))
		self._setType('statisticsBoxOffsetX', stringParameter('0p'))
		self._setType('statisticsBoxOffsetY', stringParameter('0p'))

		self._setType('legendsBoxAnchor', listedParameter('NW', ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']))
		self._setType('legendsBoxOffsetX', stringParameter('0p'))
		self._setType('legendsBoxOffsetY', stringParameter('0p'))

		self._setType('textsBoxAnchor', listedParameter('NE', ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']))
		self._setType('textsBoxOffsetX', stringParameter('0p'))
		self._setType('textsBoxOffsetY', stringParameter('0p'))

	def _setType(self, parameterName, typeData):
		self._parameters[parameterName] = typeData
		
	def _getType(self, parameterName):
		return self._parameters[parameterName]

	def availableParameters(self):
		names = self._parameters.keys()
		names.sort()
		return names

	def parameterValue(self, parameterName):
		availables = self.availableParameters()
		if parameterName in availables:
			return float(self._getType(parameterName).getValue())
		else:
			raise IllegalArgumentException('Parameter %s is not in %s.' % (parameterName, availables))

	def _parameterData(self, parameterName):
		return self._getType(parameterName).getValue()

	def reset(self):
		for parameterName in self.availableParameters():
			self._getType(parameterName).reset()

	def setParameter(self, parameterName, options):
		if not parameterName in self.availableParameters():
			return False
		else:
			try:
				self._getType(parameterName).setValue(options)
			except _convertException:
				return False
			return True
