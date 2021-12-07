from paida.paida_core.PAbsorber import *
from paida.paida_core.IBaseStyle import *
from paida.paida_core.IDataStyle import IDataStyle
from paida.paida_core.IInfoStyle import IInfoStyle
from paida.paida_core.ITitleStyle import ITitleStyle
from paida.paida_core.IAxisStyle import IAxisStyle

class IPlotterStyle(IBaseStyle):

	def __init__(self):
		IBaseStyle.__init__(self)
		self._setType('dataStyle', styleParameter(IDataStyle, 'IDataStyle'))
		self._setType('infoStyle', styleParameter(IInfoStyle, 'IInfoStyle'))
		self._setType('titleStyle', styleParameter(ITitleStyle, 'ITitleStyle'))
		self._setType('xAxisStyle', styleParameter(IAxisStyle, 'IAxisStyle'))
		self._setType('yAxisStyle', styleParameter(IAxisStyle, 'IAxisStyle'))
		self._setType('zAxisStyle', styleParameter(IAxisStyle, 'IAxisStyle'))

		self._setType('showTitle', booleanParameter(True))
		self._setType('showStatisticsBox', booleanParameter(False))
		self._setType('showLegendsBox', booleanParameter(False))
		self._setType('showTextsBox', booleanParameter(False))
		self._setType('backgroundColor', colorParameter('white'))
		self._setType('regionFillColor', colorParameter(''))
		self._setType('regionLineColor', colorParameter(''))
		### 3D rotated plot
		self._setType('rotationRatio', listParameter('[2.0, 4.0]'))
		self._setType('rotationAxis', listParameter('[None, None, None, None, False]'))

	def _createCopy(self):
		plotterStyle = IPlotterStyle()
		self._createCopyWalker(self, plotterStyle)
		return plotterStyle

	def _createCopyWalker(self, styleData, copyTo):
		for name in styleData.availableParameters():
			parameterType = styleData._getType(name)
			if parameterType.__class__.__name__ == 'styleParameter':
				self._createCopyWalker(parameterType.getValue(), copyTo._parameterData(name))
			else:
				result = copyTo.setParameter(name, parameterType.getValue(), styleData._getCustomized(name))

	def dataStyle(self):
		return self._parameterData('dataStyle')

	def infoStyle(self):
		return self._parameterData('infoStyle')

	def titleStyle(self):
		return self._parameterData('titleStyle')
		
	def xAxisStyle(self):
		return self._parameterData('xAxisStyle')
		
	def yAxisStyle(self):
		return self._parameterData('yAxisStyle')

	def zAxisStyle(self):
		return self._parameterData('zAxisStyle')
		
	def setDataStyle(self, style):
		return self.setParameter('dataStyle', style)
		
	def setInfoStyle(self, style):
		return self.setParameter('infoStyle', style)

	def setTitleStyle(self, style):
		return self.setParameter('titleStyle', style)

	def setXAxisStyle(self, style):
		return self.setParameter('xAxisStyle', style)
		
	def setYAxisStyle(self, style):
		return self.setParameter('yAxisStyle', style)
		
	def setZAxisStyle(self, style):
		return self.setParameter('zAxisStyle', style)
