from paida.paida_core.PAbsorber import *
from paida.paida_core.IBaseStyle import *

class IBrushStyle(IBaseStyle):

	def __init__(self):
		IBaseStyle.__init__(self)
		self._setType('color', colorParameter('black'))
		self._setType('opacity', floatRangeParameter(0.0, 0.0, 1.0))

	def availableColors(self):
		return self.availableParameterOptions('color')

	def color(self):
		return self._parameterData('color')

	def opacity(self):
		return self._parameterData('opacity')

	def setColor(self, color):
		return self.setParameter('color', color)

	def setOpacity(self, opacity):
		return self.setParameter('opacity', opacity)
