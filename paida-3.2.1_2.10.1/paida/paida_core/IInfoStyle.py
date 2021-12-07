from paida.paida_core.PAbsorber import *
from paida.paida_core.IBaseStyle import *
from paida.paida_core.IFillStyle import *
from paida.paida_core.ILineStyle import *
from paida.paida_core.ITextStyle import *

class IInfoStyle(IBaseStyle):

	def __init__(self):
		IBaseStyle.__init__(self)
		self._setType('textStyle', styleParameter(ITextStyle, 'ITextStyle'))
		self._setType('lineStyle', styleParameter(ILineStyle, 'ILineStyle'))
		self._setType('fillStyle', styleParameter(IFillStyle, 'IFillStyle'))
		
		self._parameterData('fillStyle').setColor('')

	def _createCopy(self):
		infoStyle = IInfoStyle()
		self._createCopyWalker(self, infoStyle)
		return infoStyle

	def _createCopyWalker(self, styleData, copyTo):
		for name in styleData.availableParameters():
			parameterType = styleData._getType(name)
			if parameterType.__class__.__name__ == 'styleParameter':
				self._createCopyWalker(parameterType.getValue(), copyTo._parameterData(name))
			else:
				result = copyTo.setParameter(name, parameterType.getValue(), styleData._getCustomized(name))

	def reset(self):
		IBaseStyle.reset(self)
		self.parameterValue('fillStyle').setColor('')

	def textStyle(self):
		return self._parameterData('textStyle')

	def setTextStyle(self, style):
		return self.setParameter('textStyle', style)

	def paida_lineStyle(self):
		return self._parameterData('lineStyle')

	def paida_setLineStyle(self, style):
		return self.setParameter('lineStyle', style)
		
	def paida_fillStyle(self):
		return self._parameterData('fillStyle')

	def paida_setFillStyle(self, style):
		return self.setParameter('fillStyle', style)
