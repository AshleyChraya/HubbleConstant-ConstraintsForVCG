from paida.paida_core.PAbsorber import *
from paida.paida_core.IBaseStyle import *
from paida.paida_core.ITextStyle import *

class ITitleStyle(IBaseStyle):

	def __init__(self):
		IBaseStyle.__init__(self)
		self._setType('textStyle', styleParameter(ITextStyle, 'ITextStyle'))

	def textStyle(self):
		return self._parameterData('textStyle')

	def setTextStyle(self, style):
		return self.setParameter('textStyle', style)
