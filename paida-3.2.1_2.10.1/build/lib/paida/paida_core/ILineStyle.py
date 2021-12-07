from paida.paida_core.PAbsorber import *
from paida.paida_core.IBrushStyle import *

class ILineStyle(IBrushStyle):

	def __init__(self):
		IBrushStyle.__init__(self)
		self._setType('lineType', listedParameter('solid', ['solid', 'dot', 'dash', 'dash-dot', 'dash-dot-dot']))
		self._setType('thickness', intParameter(1))

	def availableLineTypes(self):
		return self.availableParameterOptions('lineType')

	def lineType(self):
		return self._parameterData('lineType')

	def setLineType(self, lineType):
		return self.setParameter('lineType', lineType)

	def thickness(self):
		return self._parameterData('thickness')

	def setThickness(self, thickness):
		return self.setParameter('thickness', thickness)

	def _createCopy(self):
		style = ILineStyle()
		self._createCopyWalker(self, style)
		return style

	def _createCopyWalker(self, styleData, copyTo):
		for name in styleData.availableParameters():
			parameterType = styleData._getType(name)
			if parameterType.__class__.__name__ == 'styleParameter':
				self._createCopyWalker(parameterType.getValue(), copyTo._parameterData(name))
			else:
				result = copyTo.setParameter(name, parameterType.getValue(), styleData._getCustomized(name))
