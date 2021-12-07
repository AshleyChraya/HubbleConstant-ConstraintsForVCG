from paida.paida_core.PAbsorber import *
from paida.paida_core.IBrushStyle import *

class IFillStyle(IBrushStyle):

	def __init__(self):
		IBrushStyle.__init__(self)
		self._setType('pattern', listedParameter('flat', ['flat']))

		self.setParameter('color', 'white', customize = False)

	def availablePatterns(self):
		return self.availableParameterOptions('pattern')

	def pattern(self):
		return self._parameterData('pattern')

	def setPattern(self, pattern):
		return self.setParameter('pattern', pattern)

	def _createCopy(self):
		style = IFillStyle()
		self._createCopyWalker(self, style)
		return style

	def _createCopyWalker(self, styleData, copyTo):
		for name in styleData.availableParameters():
			parameterType = styleData._getType(name)
			if parameterType.__class__.__name__ == 'styleParameter':
				self._createCopyWalker(parameterType.getValue(), copyTo._parameterData(name))
			else:
				result = copyTo.setParameter(name, parameterType.getValue(), styleData._getCustomized(name))