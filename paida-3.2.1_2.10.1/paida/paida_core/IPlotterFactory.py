from paida.paida_core.PAbsorber import *
from paida.paida_core.IAxisStyle import *
from paida.paida_core.IDataStyle import *
from paida.paida_core.IPlotterStyle import *
from paida.paida_core.ITitleStyle import *
from paida.paida_core.IFillStyle import *
from paida.paida_core.ILineStyle import *
from paida.paida_core.IMarkerStyle import *
from paida.paida_core.IPlotter import *
from paida.paida_core.ITextStyle import *

class IPlotterFactory:
	def __init__(self):
		self._plotterNumber = 0

	def create(self, name = None):
		plotter = IPlotter()
		if name == None:
			name = 'plotter_%d' % self._plotterNumber
			plotter._setWindowTitle(name)
		else:
			plotter.setTitle(name)
		self._plotterNumber += 1
		return plotter

	def createAxisStyle(self):
		return IAxisStyle()
		
	def createDataStyle(self):
		return IDataStyle()
		
	def createFillStyle(self):
		return IFillStyle()

	def createLineStyle(self):
		return ILineStyle()
		
	def createMarkerStyle(self):
		return IMarkerStyle()
		
	def createPlotterStyle(self):
		return IPlotterStyle()
		
	def createTextStyle(self):
		return ITextStyle()
		
	def createTitleStyle(self):
		return ITitleStyle()
