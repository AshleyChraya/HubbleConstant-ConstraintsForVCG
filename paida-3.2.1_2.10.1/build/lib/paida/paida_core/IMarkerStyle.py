from paida.paida_core.PAbsorber import *
from paida.paida_core.IBrushStyle import *

class IMarkerStyle(IBrushStyle):

	def __init__(self):
		IBrushStyle.__init__(self)
		self._setType('shape', listedParameter('circle', ['circle', 'square', 'diamond', 'triangle', 'cross']))
		self._setType('size', stringParameter('5p'))
		
	def availableShapes(self):
		return self.availableParameterOptions('shape')

	def shape(self):
		return self._parameterData('shape')

	def setShape(self, shape):
		return self.setParameter('shape', shape)

	def _createCopy(self):
		style = IMarkerStyle()
		self._createCopyWalker(self, style)
		return style

	def _createCopyWalker(self, styleData, copyTo):
		for name in styleData.availableParameters():
			parameterType = styleData._getType(name)
			if parameterType.__class__.__name__ == 'styleParameter':
				self._createCopyWalker(parameterType.getValue(), copyTo._parameterData(name))
			else:
				result = copyTo.setParameter(name, parameterType.getValue(), styleData._getCustomized(name))
