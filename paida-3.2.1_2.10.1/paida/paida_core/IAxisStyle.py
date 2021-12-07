from paida.paida_core.PAbsorber import *
from paida.paida_core.IBaseStyle import *
from paida.paida_core.ILineStyle import *
from paida.paida_core.ITextStyle import *

class IAxisStyle(IBaseStyle):

	def __init__(self):
		IBaseStyle.__init__(self)
		self._setType('labelStyle', styleParameter(ITextStyle, 'ITextStyle'))
		self._setType('lineStyle', styleParameter(ILineStyle, 'ILineStyle'))
		self._setType('tickLabelStyle', styleParameter(ITextStyle, 'ITextStyle'))

		self._setType('label', stringParameter(''))
		self._setType('scale', listedParameter('linear', ['log', 'lin', 'logarithmic', 'linear']))
		self._setType('type', listedParameter('double', ['double', 'int', 'time']))
		self._setType('grid', booleanParameter(True))
		self._setType('gridSub', booleanParameter(False))
		self._setType('tickLine', listedParameter('both', ['in', 'out', 'both', '']))

	def lineStyle(self):
		return self._parameterData('lineStyle')

	def tickLabelStyle(self):
		return self._parameterData('tickLabelStyle')

	def labelStyle(self):
		return self._parameterData('labelStyle')
		
	def setLineStyle(self, style):
		return self.setParameter('lineStyle', style)
		
	def setTickLabelStyle(self, style):
		return self.setParameter('tickLabelStyle', style)
		
	def setLabelStyle(self, style):
		return self.setParameter('labelStyle', style)

	def setLabel(self, label):
		return self.setParameter('label', label)
