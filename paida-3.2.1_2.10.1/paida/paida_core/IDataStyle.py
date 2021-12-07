from paida.paida_core.PAbsorber import *
from paida.paida_core.IBaseStyle import *
from paida.paida_core.IFillStyle import *
from paida.paida_core.ILineStyle import *
from paida.paida_core.IMarkerStyle import *

class IDataStyle(IBaseStyle):

	def __init__(self):
		IBaseStyle.__init__(self)
		self._setType('fillStyle', styleParameter(IFillStyle, 'IFillStyle'))
		self._setType('lineStyle', styleParameter(ILineStyle, 'ILineStyle'))
		self._setType('markerStyle', styleParameter(IMarkerStyle, 'IMarkerStyle'))

		self._setType('histogram1DFormat', listedParameter('histogram', ['histogram', 'bar']))
		self._setType('histogram2DFormat', listedParameter('bar', ['bar', 'box', 'ellipse', 'hit']))
		self._setType('histogram3DFormat', listedParameter('box', ['box']))
		self._setType('cloud1DFormat', listedParameter('scatter', ['histogram', 'scatter', 'scatterIndexed']))
		self._setType('cloud2DFormat', listedParameter('scatter', ['histogram', 'scatter', 'scatterIndexed', 'scatterColorIndexed']))
		self._setType('cloud3DFormat', listedParameter('scatter', ['histogram', 'scatter']))
		self._setType('dataPointSet1DFormat', listedParameter('scatter', ['scatter', 'scatterIndexed']))
		self._setType('dataPointSet2DFormat', listedParameter('scatter', ['scatter', 'scatterIndexed', 'scatterColorIndexed']))
		self._setType('dataPointSet3DFormat', listedParameter('scatter', ['scatter']))
		self._setType('dataPoint', listedParameter('center', ['center', 'mean']))
		self._setType('showMarkers', booleanParameter(False))
		self._setType('showErrorBars', booleanParameter(False))
		self._setType('errorBarsColor', colorParameter('black'))

	def fillStyle(self):
		return self._parameterData('fillStyle')

	def lineStyle(self):
		return self._parameterData('lineStyle')

	def markerStyle(self):
		return self._parameterData('markerStyle')

	def setFillstyle(self, style):
		return self.setParameter('fillStyle', style)

	def setLineStyle(self, style):
		return self.setParameter('lineStyle', style)

	def setMarkerStyle(self, style):
		return self.setParameter('markerStyle', style)
