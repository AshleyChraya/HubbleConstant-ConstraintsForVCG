from paida.paida_core.PAbsorber import *
from paida.paida_core.ICloud1D import *
from paida.paida_core.ICloud2D import *
from paida.paida_core.ICloud3D import *
from paida.paida_core.IHistogram1D import *
from paida.paida_core.IHistogram2D import *
from paida.paida_core.IHistogram3D import *
from paida.paida_core.IProfile1D import *
from paida.paida_core.IProfile2D import *
from paida.paida_core.PExceptions import *
from paida.paida_core.PUtilities import *

from types import *
import os

class IHistogramFactory:

	def __init__(self, tree):
		self._setTree(tree)

	def _setTree(self, tree):
		self._tree = tree

	def _getTree(self):
		return self._tree

	def destroy(self, histogram):
		self._tree._rmObject(histogram)

	def createCloud1D(self, data1, data2 = None, data3 = None, data4 = None):
		if isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and (data3 == None) and (data4 == None):
			name = data1
			title = data2
			nMax = -1
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and (data4 == None):
			name = data1
			title = data2
			nMax = data3
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, StringTypes):
			name = data1
			title = data2
			nMax = data3
			options = optionAnalyzer(data4)
		elif isinstance(data1, StringTypes) and (data2 == None) and (data3 == None) and (data4 == None):
			name = data1
			title = data1
			nMax = -1
			options = optionAnalyzer(None)
		else:
			raise IllegalArgumentException()

		object = ICloud1D(os.path.basename(name), title, nMax, options)
		self._getTree()._mkObject(name, object)
		return object

	def createCloud2D(self, data1, data2 = None, data3 = None, data4 = None):
		if isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and (data3 == None) and (data4 == None):
			name = data1
			title = data2
			nMax = -1
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and (data4 == None):
			name = data1
			title = data2
			nMax = data3
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, StringTypes):
			name = data1
			title = data2
			nMax = data3
			options = optionAnalyzer(data4)
		elif isinstance(data1, StringTypes) and (data2 == None) and (data3 == None) and (data4 == None):
			name = data1
			title = data1
			nMax = -1
			options = optionAnalyzer(None)
		else:
			raise IllegalArgumentException()

		object = ICloud2D(os.path.basename(name), title, nMax, options)
		self._getTree()._mkObject(name, object)
		return object

	def createCloud3D(self, data1, data2 = None, data3 = None, data4 = None):
		if isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and (data3 == None) and (data4 == None):
			name = data1
			title = data2
			nMax = -1
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and (data4 == None):
			name = data1
			title = data2
			nMax = data3
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, StringTypes):
			name = data1
			title = data2
			nMax = data3
			options = optionAnalyzer(data4)
		elif isinstance(data1, StringTypes) and (data2 == None) and (data3 == None) and (data4 == None):
			name = data1
			title = data1
			nMax = -1
			options = optionAnalyzer(None)
		else:
			raise IllegalArgumentException()

		object = ICloud3D(os.path.basename(name), title, nMax, options)
		self._getTree()._mkObject(name, object)
		return object

	def _createEdges(self, nBins, lower, upper):
		result = [float(lower)]
		fullWidth = upper - lower
		unit = float(fullWidth) / nBins
		for i in range(1, nBins):
			result.append(lower + i * unit)
		result.append(upper)
		return result

	def createHistogram1D(self, data1, data2, data3, data4 = None, data5 = None, data6 = None):
		IntOrFloatType = (IntType, FloatType)
		if isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and (data6 == None):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			fixedBinning = True
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, StringTypes):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			fixedBinning = True
			options = optionAnalyzer(data6)
		elif isinstance(data1, StringTypes) and isinstance(data2, IntType) and isinstance(data3, IntOrFloatType) and isinstance(data4, IntOrFloatType) and (data5 == None) and (data6 == None):
			name = data1
			title = data1
			edgesX = self._createEdges(data2, data3, data4)
			fixedBinning = True
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and (data4 == None) and (data5 == None) and (data6 == None):
			name = data1
			title = data2
			edgesX = data3
			fixedBinning = False
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and isinstance(data4, StringTypes) and (data5 == None) and (data6 == None):
			name = data1
			title = data2
			edgesX = data3
			fixedBinning = False
			options = optionAnalyzer(data4)
		else:
			raise IllegalArgumentException()

		edgesY = []
		edgesZ = []
		edges = [edgesX, edgesY, edgesZ]
		object = IHistogram1D(os.path.basename(name), title, edges, fixedBinning, options)
		self._getTree()._mkObject(name, object)
		return object

	def createHistogram2D(self, data1, data2, data3, data4, data5 = None, data6 = None, data7 = None, data8 = None, data9 = None):
		IntOrFloatType = (IntType, FloatType)
		if isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntOrFloatType) and (data9 == None):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			edgesY = self._createEdges(data6, data7, data8)
			fixedBinning = True
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntOrFloatType) and isinstance(data9, StringTypes):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			edgesY = self._createEdges(data6, data7, data8)
			fixedBinning = True
			options = optionAnalyzer(data9)
		elif isinstance(data1, StringTypes) and isinstance(data2, IntType) and isinstance(data3, IntOrFloatType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntType) and isinstance(data6, IntOrFloatType) and isinstance(data7, IntOrFloatType) and (data8 == None) and (data9 == None):
			name = data1
			title = data1
			edgesX = self._createEdges(data2, data3, data4)
			edgesY = self._createEdges(data5, data6, data7)
			fixedBinning = True
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and (data5 == None) and (data6 == None) and (data7 == None) and (data8 == None) and (data9 == None):
			name = data1
			title = data2
			edgesX = data3
			edgesY = data4
			fixedBinning = False
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and isinstance(data5, StringTypes) and (data6 == None) and (data7 == None) and (data8 == None) and (data9 == None):
			name = data1
			title = data2
			edgesX = data3
			edgesY = data4
			fixedBinning = False
			options = optionAnalyzer(data5)
		else:
			raise IllegalArgumentException()

		edgesZ = []
		edges = [edgesX, edgesY, edgesZ]
		object = IHistogram2D(os.path.basename(name), title, edges, fixedBinning, options)
		self._getTree()._mkObject(name, object)
		return object

	def createHistogram3D(self, data1, data2, data3, data4, data5, data6 = None, data7 = None, data8 = None, data9 = None, data10 = None, data11 = None, data12 = None):
		IntOrFloatType = (IntType, FloatType)
		if isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntOrFloatType) and isinstance(data9, IntType) and isinstance(data10, IntOrFloatType) and isinstance(data11, IntOrFloatType) and (data12 == None):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			edgesY = self._createEdges(data6, data7, data8)
			edgesZ = self._createEdges(data9, data10, data11)
			fixedBinning = True
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntOrFloatType) and isinstance(data9, IntType) and isinstance(data10, IntOrFloatType) and isinstance(data11, IntOrFloatType) and isinstance(data12, StringTypes):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			edgesY = self._createEdges(data6, data7, data8)
			edgesZ = self._createEdges(data9, data10, data11)
			fixedBinning = True
			options = optionAnalyzer(data12)
		elif isinstance(data1, StringTypes) and isinstance(data2, IntType) and isinstance(data3, IntOrFloatType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntType) and isinstance(data6, IntOrFloatType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntType) and isinstance(data9, IntOrFloatType) and isinstance(data10, IntOrFloatType) and (data11 == None) and (data12 == None):
			name = data1
			title = data1
			edgesX = self._createEdges(data2, data3, data4)
			edgesY = self._createEdges(data5, data6, data7)
			edgesZ = self._createEdges(data8, data9, data10)
			fixedBinning = True
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and (data6 == None) and (data7 == None) and (data8 == None) and (data9 == None) and (data10 == None) and (data11 == None) and (data12 == None):
			name = data1
			title = data2
			edgesX = data3
			edgesY = data4
			edgesZ = data5
			fixedBinning = False
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and isinstance(data6, StringTypes) and (data7 == None) and (data8 == None) and (data9 == None) and (data10 == None) and (data11 == None) and (data12 == None):
			name = data1
			title = data2
			edgesX = data3
			edgesY = data4
			edgesZ = data5
			fixedBinning = False
			options = optionAnalyzer(data6)
		else:
			raise IllegalArgumentException()

		edges = [edgesX, edgesY, edgesZ]
		object = IHistogram3D(os.path.basename(name), title, edges, fixedBinning, options)
		self._getTree()._mkObject(name, object)
		return object

	def createProfile1D(self, data1, data2, data3, data4 = None, data5 = None, data6 = None, data7 = None, data8 = None):
		IntOrFloatType = (IntType, FloatType)
		if isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and (data6 == None) and (data7 == None) and (data8 == None):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			fixedBinning = True
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, StringTypes) and (data7 == None) and (data8 == None):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			fixedBinning = True
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(data6)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntOrFloatType) and isinstance(data7, IntOrFloatType) and (data8 == None):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			fixedBinning = True
			lowerValue = data6
			upperValue = data7
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntOrFloatType) and isinstance(data7, IntOrFloatType) and isinstance(data8, StringTypes):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			fixedBinning = True
			lowerValue = data6
			upperValue = data7
			options = optionAnalyzer(data8)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and (data4 == None) and (data5 == None) and (data6 == None) and (data7 == None) and (data8 == None):
			name = data1
			title = data2
			edgesX = data3
			fixedBinning = False
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and isinstance(data4, StringTypes) and (data5 == None) and (data6 == None) and (data7 == None) and (data8 == None):
			name = data1
			title = data2
			edgesX = data3
			fixedBinning = False
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(data4)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and (data6 == None) and (data7 == None) and (data8 == None):
			name = data1
			title = data2
			edgesX = data3
			fixedBinning = False
			lowerValue = data4
			upperValue = data5
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, StringTypes) and (data7 == None) and (data8 == None):
			name = data1
			title = data2
			edgesX = data3
			fixedBinning = False
			lowerValue = data4
			upperValue = data5
			options = optionAnalyzer(data6)
		elif isinstance(data1, StringTypes) and isinstance(data2, IntType) and isinstance(data3, IntOrFloatType) and isinstance(data4, IntOrFloatType) and (data5 == None) and (data6 == None) and (data7 == None) and (data8 == None):
			name = data1
			title = data1
			edgesX = self._createEdges(data2, data3, data4)
			fixedBinning = True
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, IntType) and isinstance(data3, IntOrFloatType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntOrFloatType) and (data7 == None) and (data8 == None):
			name = data1
			title = data1
			edgesX = self._createEdges(data2, data3, data4)
			fixedBinning = True
			lowerValue = data5
			upperValue = data6
			options = optionAnalyzer(None)
		else:
			raise IllegalArgumentException()

		edgesY = []
		edgesZ = []
		edges = [edgesX, edgesY, edgesZ]
		object = IProfile1D(os.path.basename(name), title, edges, fixedBinning, lowerValue, upperValue, options)
		self._getTree()._mkObject(name, object)
		return object

	def createProfile2D(self, data1, data2, data3, data4, data5 = None, data6 = None, data7 = None, data8 = None, data9 = None, data10 = None, data11 = None):
		IntOrFloatType = (IntType, FloatType)
		if isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntOrFloatType) and (data9 == None) and (data10 == None) and (data11 == None):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			edgesY = self._createEdges(data6, data7, data8)
			fixedBinning = True
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntOrFloatType) and isinstance(data9, StringTypes) and (data10 == None) and (data11 == None):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			edgesY = self._createEdges(data6, data7, data8)
			fixedBinning = True
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(data9)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntOrFloatType) and isinstance(data9, IntOrFloatType) and isinstance(data10, IntOrFloatType) and (data11 == None):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			edgesY = self._createEdges(data6, data7, data8)
			fixedBinning = True
			lowerValue = data9
			upperValue = data10
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and isinstance(data3, IntType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntOrFloatType) and isinstance(data9, IntOrFloatType) and isinstance(data10, IntOrFloatType) and isinstance(data11, StringTypes):
			name = data1
			title = data2
			edgesX = self._createEdges(data3, data4, data5)
			edgesY = self._createEdges(data6, data7, data8)
			fixedBinning = True
			lowerValue = data9
			upperValue = data10
			options = optionAnalyzer(data11)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and (data5 == None) and (data6 == None) and (data7 == None) and (data8 == None) and (data9 == None) and (data10 == None) and (data11 == None):
			name = data1
			title = data2
			edgesX = data3
			edgesY = data4
			fixedBinning = False
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and isinstance(data5, StringTypes) and (data6 == None) and (data7 == None) and (data8 == None) and (data9 == None) and (data10 == None) and (data11 == None):
			name = data1
			title = data2
			edges = [[], [], []]
			edges[0] = data3
			edges[1] = data4
			fixedBinning = False
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(data5)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and (data7 == None) and (data8 == None) and (data9 == None) and (data10 == None) and (data11 == None):
			name = data1
			title = data2
			edgesX = data3
			edgesY = data4
			fixedBinning = False
			lowerValue = data5
			upperValue = data6
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and isinstance(data5, IntOrFloatType) and isinstance(data6, IntType) and isinstance(data7, StringTypes) and (data8 == None) and (data9 == None) and (data10 == None) and (data11 == None):
			name = data1
			title = data2
			edgesX = data3
			edgesY = data4
			fixedBinning = False
			lowerValue = data5
			upperValue = data6
			options = optionAnalyzer(data7)
		elif isinstance(data1, StringTypes) and isinstance(data2, IntType) and isinstance(data3, IntOrFloatType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntType) and isinstance(data6, IntOrFloatType) and isinstance(data7, IntOrFloatType) and (data8 == None) and (data9 == None) and (data10 == None) and (data11 == None):
			name = data1
			title = data1
			edgesX = self._createEdges(data2, data3, data4)
			edgesY = self._createEdges(data5, data6, data7)
			fixedBinning = True
			lowerValue = None
			upperValue = None
			options = optionAnalyzer(None)
		elif isinstance(data1, StringTypes) and isinstance(data2, IntType) and isinstance(data3, IntOrFloatType) and isinstance(data4, IntOrFloatType) and isinstance(data5, IntType) and isinstance(data6, IntOrFloatType) and isinstance(data7, IntOrFloatType) and isinstance(data8, IntOrFloatType) and isinstance(data9, IntOrFloatType) and (data10 == None) and (data11 == None):
			name = data1
			title = data1
			edgesX = self._createEdges(data2, data3, data4)
			edgesY = self._createEdges(data5, data6, data7)
			fixedBinning = True
			lowerValue = data8
			upperValue = data9
			options = optionAnalyzer(None)
		else:
			raise IllegalArgumentException()

		edgesZ = []
		edges = [edgesX, edgesY, edgesZ]
		object = IProfile2D(os.path.basename(name), title, edges, fixedBinning, lowerValue, upperValue, options)
		self._getTree()._mkObject(name, object)
		return object

	def createCopy(self, name, data):
		if not isinstance(name, StringTypes):
			raise IllegalArgumentException()

		if isinstance(data, ICloud1D):
			newData = self.createCloud1D(name, data.title(), data.maxEntries(), data._getOptionString())
			data._copyContents(newData)
		elif isinstance(data, ICloud2D):
			newData = self.createCloud2D(name, data.title(), data.maxEntries(), data._getOptionString())
			data._copyContents(newData)
		elif isinstance(data, ICloud3D):
			newData = self.createCloud3D(name, data.title(), data.maxEntries(), data._getOptionString())
			data._copyContents(newData)
		elif isinstance(data, IHistogram1D):
			newData = self.createHistogram1D(name, data.title(), data.axis()._getEdges(), data._getOptionString())
			newData.add(data)
		elif isinstance(data, IHistogram2D):
			newData = self.createHistogram2D(name, data.title(), data.xAxis()._getEdges(), data.yAxis()._getEdges(), data._getOptionString())
			newData.add(data)
		elif isinstance(data, IHistogram3D):
			newData = self.createHistogram3D(name, data.title(), data.xAxis()._getEdges(), data.yAxis()._getEdges(), data.zAxis()._getEdges(), data._getOptionString())
			newData.add(data)
		elif isinstance(data, IProfile1D):
			newData = self.createProfile1D(name, data.title(), data.axis()._getEdges(), data._getLowerValue(), data._getUpperValue(), data._getOptionString())
			newData.add(data)
		elif isinstance(data, IProfile2D):
			newData = self.createProfile2D(name, data.title(), data.xAxis()._getEdges(), data.yAxis()._getEdges(), data._getLowerValue(), data._getUpperValue(), data._getOptionString())
			newData.add(data)
		else:
			raise IllegalArgumentException()
		return newData

	def add(self, name, data1, data2):
		if isinstance(name, StringTypes) and isinstance(data1, IHistogram1D) and isinstance(data2, IHistogram1D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
		elif isinstance(name, StringTypes) and isinstance(data1, IHistogram2D) and isinstance(data2, IHistogram2D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[1]._edgeList != data2._axis[1]._edgeList:
				raise IllegalArgumentException()
		elif isinstance(name, StringTypes) and isinstance(data1, IHistogram3D) and isinstance(data2, IHistogram3D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[1]._edgeList != data2._axis[1]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[2]._edgeList != data2._axis[2]._edgeList:
				raise IllegalArgumentException()
		else:
			raise IllegalArgumentException()

		newHistogram = self.createCopy(name, data1)
		newHistogram.add(data2)
		return newHistogram

	def subtract(self, name, data1, data2):
		if isinstance(name, StringTypes) and isinstance(data1, IHistogram1D) and isinstance(data2, IHistogram1D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
		elif isinstance(name, StringTypes) and isinstance(data1, IHistogram2D) and isinstance(data2, IHistogram2D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[1]._edgeList != data2._axis[1]._edgeList:
				raise IllegalArgumentException()
		elif isinstance(name, StringTypes) and isinstance(data1, IHistogram3D) and isinstance(data2, IHistogram3D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[1]._edgeList != data2._axis[1]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[2]._edgeList != data2._axis[2]._edgeList:
				raise IllegalArgumentException()
		else:
			raise IllegalArgumentException()

		newHistogram = self.createCopy(name, data1)
		newHistogram._binEntries.subtract(data2._binEntries)
		newHistogram._binSumOfWeights.subtract(data2._binSumOfWeights)
		newHistogram._binSumOfErrors.add(data2._binSumOfErrors)
		newHistogram._binSumOfTorquesX.subtract(data2._binSumOfTorquesX)
		newHistogram._binSumOfTorquesY.subtract(data2._binSumOfTorquesY)
		newHistogram._binSumOfTorquesZ.subtract(data2._binSumOfTorquesZ)
		newHistogram._binSumOfInertialsX.subtract(data2._binSumOfInertialsX)
		newHistogram._binSumOfInertialsY.subtract(data2._binSumOfInertialsY)
		newHistogram._binSumOfInertialsZ.subtract(data2._binSumOfInertialsZ)
		return newHistogram

	def multiply(self, name, data1, data2):
		if isinstance(name, StringTypes) and isinstance(data1, IHistogram1D) and isinstance(data2, IHistogram1D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			dimension = 1
		elif isinstance(name, StringTypes) and isinstance(data1, IHistogram2D) and isinstance(data2, IHistogram2D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[1]._edgeList != data2._axis[1]._edgeList:
				raise IllegalArgumentException()
			dimension = 2
		elif isinstance(name, StringTypes) and isinstance(data1, IHistogram3D) and isinstance(data2, IHistogram3D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[1]._edgeList != data2._axis[1]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[2]._edgeList != data2._axis[2]._edgeList:
				raise IllegalArgumentException()
			dimension = 3
		else:
			raise IllegalArgumentException()

		newHistogram = self.createCopy(name, data1)
		tmpHistogram = self.createCopy(name, data2)
		newHistogram._binSumOfWeights.multiply(data2._binSumOfWeights)
		newHistogram._binSumOfErrors.multiplySquared(data2._binSumOfWeights)
		tmpHistogram._binSumOfErrors.multiplySquared(data1._binSumOfWeights)
		newHistogram._binSumOfErrors.add(tmpHistogram._binSumOfErrors)
		newHistogram._binSumOfTorquesX.multiply(data2._binSumOfWeights)
		newHistogram._binSumOfInertialsX.multiply(data2._binSumOfWeights)
		if dimension in [2, 3]:
			newHistogram._binSumOfTorquesY.multiply(data2._binSumOfWeights)
			newHistogram._binSumOfInertialsY.multiply(data2._binSumOfWeights)
		if dimension == 3:
			newHistogram._binSumOfTorquesZ.multiply(data2._binSumOfWeights)
			newHistogram._binSumOfInertialsZ.multiply(data2._binSumOfWeights)
		return newHistogram

	def divide(self, name, data1, data2):
		if isinstance(name, StringTypes) and isinstance(data1, IHistogram1D) and isinstance(data2, IHistogram1D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			dimension = 1
		elif isinstance(name, StringTypes) and isinstance(data1, IHistogram2D) and isinstance(data2, IHistogram2D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[1]._edgeList != data2._axis[1]._edgeList:
				raise IllegalArgumentException()
			dimension = 2
		elif isinstance(name, StringTypes) and isinstance(data1, IHistogram3D) and isinstance(data2, IHistogram3D):
			if data1._axis[0]._edgeList != data2._axis[0]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[1]._edgeList != data2._axis[1]._edgeList:
				raise IllegalArgumentException()
			if data1._axis[2]._edgeList != data2._axis[2]._edgeList:
				raise IllegalArgumentException()
			dimension = 3
		else:
			raise IllegalArgumentException()

		newHistogram = self.createCopy(name, data1)
		for i in range(len(data1._binEntries.data)):
			weight2 = data2._binSumOfWeights.data[i]
			try:
				newHistogram._binSumOfWeights.data[i] /= weight2
				newHistogram._binSumOfErrors.data[i] /= weight2**2
				newHistogram._binSumOfErrors.data[i] += data2._binSumOfErrors.data[i] * data1._binSumOfWeights.data[i]**2 / weight2**4
				newHistogram._binSumOfTorquesX.data[i] /= weight2
				newHistogram._binSumOfInertialsX.data[i] /= weight2
				if dimension in [2, 3]:
					newHistogram._binSumOfTorquesY.data[i] /= weight2
					newHistogram._binSumOfInertialsY.data[i] /= weight2
				if dimension == 3:
					newHistogram._binSumOfTorquesZ.data[i] /= weight2
					newHistogram._binSumOfInertialsZ.data[i] /= weight2
			except ZeroDivisionError:
				newHistogram._binEntries.data[i] = 0.0
				newHistogram._binSumOfWeights.data[i] = 0.0
				newHistogram._binSumOfErrors.data[i] = 0.0
				newHistogram._binSumOfTorquesX.data[i] = 0.0
				newHistogram._binSumOfInertialsX.data[i] = 0.0
				if dimension in [2, 3]:
					newHistogram._binSumOfTorquesY.data[i] = 0.0
					newHistogram._binSumOfInertialsY.data[i] = 0.0
				if dimension == 3:
					newHistogram._binSumOfTorquesZ.data[i] = 0.0
					newHistogram._binSumOfInertialsZ.data[i] = 0.0
		return newHistogram

	def projectionX(self, name, hist):
		axis = hist.yAxis()
		return self.sliceX(name, hist, axis.UNDERFLOW_BIN, axis.OVERFLOW_BIN)

	def projectionY(self, name, hist):
		axis = hist.xAxis()
		return self.sliceY(name, hist, axis.UNDERFLOW_BIN, axis.OVERFLOW_BIN)

	def sliceX(self, name, hist, data1, data2 = None, inner = False):
		if isinstance(name, StringTypes) and isinstance(hist, IHistogram2D) and isinstance(data1, IntType) and (data2 == None):
			edges = [hist.xAxis()._edgeList[:], [], []]
			newHistogram = IHistogram1D(name, hist.title(), edges, hist.xAxis().isFixedBinning(), hist._getOption())
			lengthX = hist._sizeX
			data1 += 2
			for i in range(lengthX):
				newHistogram._binEntries[i, 0, 0] = hist._binEntries[i, data1, 0]
				newHistogram._binSumOfWeights[i, 0, 0] = hist._binSumOfWeights[i, data1, 0]
				newHistogram._binSumOfErrors[i, 0, 0] = hist._binSumOfErrors[i, data1, 0]
				newHistogram._binSumOfTorquesX[i, 0, 0] = hist._binSumOfTorquesX[i, data1, 0]
				newHistogram._binSumOfInertialsX[i, 0, 0] = hist._binSumOfInertialsX[i, data1, 0]
			if inner == False:
				self._getTree()._mkObject(name, newHistogram)
			return newHistogram
		elif isinstance(name, StringTypes) and isinstance(hist, IHistogram2D) and isinstance(data1, IntType) and isinstance(data2, IntType):
			edges = [hist.xAxis()._edgeList[:], [], []]
			newHistogram = IHistogram1D(name, hist.title(), edges, hist.xAxis().isFixedBinning(), hist._getOption())
			axisY = hist.yAxis()
			lengthY = hist._sizeY
			if (data1 == axisY.UNDERFLOW_BIN) and (data2 == axisY.OVERFLOW_BIN):
				binRange = range(lengthY - 2)
				binRange.append(axisY.UNDERFLOW_BIN)
				binRange.append(axisY.OVERFLOW_BIN)
			elif (data1 == axisY.UNDERFLOW_BIN) and (data2 != axisY.OVERFLOW_BIN):
				binRange = range(data2 + 1)
				binRange.append(axisY.UNDERFLOW_BIN)
			elif (data1 != axisY.UNDERFLOW_BIN) and (data2 == axisY.OVERFLOW_BIN):
				binRange = range(data1, lengthY - 2)
				binRange.append(axisY.OVERFLOW_BIN)
			elif (data1 != axisY.UNDERFLOW_BIN) and (data2 != axisY.OVERFLOW_BIN):
				binRange = range(data1, data2 + 1)
			else:
				raise IllegalArgumentException()
			for bin in binRange:
				newHistogram.add(self.sliceX('temp', hist, bin, inner = True))
			if inner == False:
				self._getTree()._mkObject(name, newHistogram)
			return newHistogram
		else:
			raise IllegalArgumentException()

	def sliceY(self, name, hist, data1, data2 = None, inner = False):
		if isinstance(name, StringTypes) and isinstance(hist, IHistogram2D) and isinstance(data1, IntType) and (data2 == None):
			edges = [hist.yAxis()._edgeList[:], [], []]
			newHistogram = IHistogram1D(name, hist.title(), edges, hist.yAxis().isFixedBinning(), hist._getOption())
			lengthY = hist._sizeY
			data1 += 2
			for i in range(lengthY):
				newHistogram._binEntries[i, 0, 0] = hist._binEntries[data1, i, 0]
				newHistogram._binSumOfWeights[i, 0, 0] = hist._binSumOfWeights[data1, i, 0]
				newHistogram._binSumOfErrors[i, 0, 0] = hist._binSumOfErrors[data1, i, 0]
				newHistogram._binSumOfTorquesX[i, 0, 0] = hist._binSumOfTorquesY[data1, i, 0]
				newHistogram._binSumOfInertialsX[i, 0, 0] = hist._binSumOfInertialsY[data1, i, 0]
			if inner == False:
				self._getTree()._mkObject(name, newHistogram)
			return newHistogram
		elif isinstance(name, StringTypes) and isinstance(hist, IHistogram2D) and isinstance(data1, IntType) and isinstance(data2, IntType):
			edges = [hist.yAxis()._edgeList[:], [], []]
			newHistogram = IHistogram1D(name, hist.title(), edges, hist.yAxis().isFixedBinning(), hist._getOption())
			axisX = hist.xAxis()
			lengthX = hist._sizeX
			if (data1 == axisX.UNDERFLOW_BIN) and (data2 == axisX.OVERFLOW_BIN):
				binRange = range(lengthX - 2)
				binRange.append(axisX.UNDERFLOW_BIN)
				binRange.append(axisX.OVERFLOW_BIN)
			elif (data1 == axisX.UNDERFLOW_BIN) and (data2 != axisX.OVERFLOW_BIN):
				binRange = range(data2 + 1)
				binRange.append(axisX.UNDERFLOW_BIN)
			elif (data1 != axisX.UNDERFLOW_BIN) and (data2 == axisX.OVERFLOW_BIN):
				binRange = range(data1, lengthX - 2)
				binRange.append(axisX.OVERFLOW_BIN)
			elif (data1 != axisX.UNDERFLOW_BIN) and (data2 != axisX.OVERFLOW_BIN):
				binRange = range(data1, data2 + 1)
			else:
				raise IllegalArgumentException()
			for bin in binRange:
				newHistogram.add(self.sliceY('temp', hist, bin, inner = True))
			if inner == False:
				self._getTree()._mkObject(name, newHistogram)
			return newHistogram
		else:
			raise IllegalArgumentException()

	def projectionXY(self, name, hist):
		axis = hist.zAxis()
		return self.sliceXY(name, hist, axis.UNDERFLOW_BIN, axis.OVERFLOW_BIN)

	def projectionXZ(self, name, hist):
		axis = hist.yAxis()
		return self.sliceXZ(name, hist, axis.UNDERFLOW_BIN, axis.OVERFLOW_BIN)

	def projectionYZ(self, name, hist):
		axis = hist.xAxis()
		return self.sliceYZ(name, hist, axis.UNDERFLOW_BIN, axis.OVERFLOW_BIN)

	def _sliceSingleXY(self, name, hist, bin):
		edges = [hist.xAxis()._edgeList[:], hist.yAxis()._edgeList[:], []]
		newHistogram = IHistogram2D(name, hist.title(), edges, hist.xAxis().isFixedBinning(), hist._getOption())
		lengthX = hist._sizeX
		lengthY = hist._sizeY
		bin += 2
		for i in range(lengthX):
			for j in range(lengthY):
				newHistogram._binEntries[i, j, 0] = hist._binEntries[i, j, bin]
				newHistogram._binSumOfWeights[i, j, 0] = hist._binSumOfWeights[i, j, bin]
				newHistogram._binSumOfErrors[i, j, 0] = hist._binSumOfErrors[i, j, bin]
				newHistogram._binSumOfTorquesX[i, j, 0] = hist._binSumOfTorquesX[i, j, bin]
				newHistogram._binSumOfTorquesY[i, j, 0] = hist._binSumOfTorquesY[i, j, bin]
				newHistogram._binSumOfInertialsX[i, j, 0] = hist._binSumOfInertialsX[i, j, bin]
				newHistogram._binSumOfInertialsY[i, j, 0] = hist._binSumOfInertialsY[i, j, bin]
		return newHistogram

	def sliceXY(self, name, hist, data1, data2 = None):
		edges = [hist.xAxis()._edgeList[:], hist.yAxis()._edgeList[:], []]
		newHistogram = IHistogram2D(name, hist.title(), edges, hist.xAxis().isFixedBinning(), hist._getOption())
		axis = hist.zAxis()
		length = hist._sizeZ
		if (data1 == axis.UNDERFLOW_BIN) and (data2 == axis.OVERFLOW_BIN):
			binRange = range(length - 2)
			binRange.append(axis.UNDERFLOW_BIN)
			binRange.append(axis.OVERFLOW_BIN)
		elif (data1 == axis.UNDERFLOW_BIN) and (data2 != axis.OVERFLOW_BIN):
			binRange = range(data2 + 1)
			binRange.append(axis.UNDERFLOW_BIN)
		elif (data1 != axis.UNDERFLOW_BIN) and (data2 == axis.OVERFLOW_BIN):
			binRange = range(data1, length - 2)
			binRange.append(axis.OVERFLOW_BIN)
		elif (data1 != axis.UNDERFLOW_BIN) and (data2 != axis.OVERFLOW_BIN):
			binRange = range(data1, data2 + 1)
		else:
			raise IllegalArgumentException()
		for bin in binRange:
			newHistogram.add(self._sliceSingleXY('temp', hist, bin))
		self._getTree()._mkObject(name, newHistogram)
		return newHistogram

	def _sliceSingleXZ(self, name, hist, bin):
		edges = [hist.xAxis()._edgeList[:], hist.zAxis()._edgeList[:], []]
		newHistogram = IHistogram2D(name, hist.title(), edges, hist.xAxis().isFixedBinning(), hist._getOption())
		lengthX = hist._sizeX
		lengthZ = hist._sizeZ
		bin += 2
		for i in range(lengthX):
			for j in range(lengthZ):
				newHistogram._binEntries[i, j, 0] = hist._binEntries[i, bin, j]
				newHistogram._binSumOfWeights[i, j, 0] = hist._binSumOfWeights[i, bin, j]
				newHistogram._binSumOfErrors[i, j, 0] = hist._binSumOfErrors[i, bin, j]
				newHistogram._binSumOfTorquesX[i, j, 0] = hist._binSumOfTorquesX[i, bin, j]
				newHistogram._binSumOfTorquesY[i, j, 0] = hist._binSumOfTorquesZ[i, bin, j]
				newHistogram._binSumOfInertialsX[i, j, 0] = hist._binSumOfInertialsX[i, bin, j]
				newHistogram._binSumOfInertialsY[i, j, 0] = hist._binSumOfInertialsZ[i, bin, j]
		return newHistogram

	def sliceXZ(self, name, hist, data1, data2 = None):
		edges = [hist.xAxis()._edgeList[:], hist.zAxis()._edgeList[:], []]
		newHistogram = IHistogram2D(name, hist.title(), edges, hist.xAxis().isFixedBinning(), hist._getOption())
		newHistogram._sumOfInertials = [None, None, None]
		axis = hist.yAxis()
		length = hist._sizeY
		if (data1 == axis.UNDERFLOW_BIN) and (data2 == axis.OVERFLOW_BIN):
			binRange = range(length - 2)
			binRange.append(axis.UNDERFLOW_BIN)
			binRange.append(axis.OVERFLOW_BIN)
		elif (data1 == axis.UNDERFLOW_BIN) and (data2 != axis.OVERFLOW_BIN):
			binRange = range(data2 + 1)
			binRange.append(axis.UNDERFLOW_BIN)
		elif (data1 != axis.UNDERFLOW_BIN) and (data2 == axis.OVERFLOW_BIN):
			binRange = range(data1, length - 2)
			binRange.append(axis.OVERFLOW_BIN)
		elif (data1 != axis.UNDERFLOW_BIN) and (data2 != axis.OVERFLOW_BIN):
			binRange = range(data1, data2 + 1)
		else:
			raise IllegalArgumentException()
		for bin in binRange:
			newHistogram.add(self._sliceSingleXZ('temp', hist, bin))
		self._getTree()._mkObject(name, newHistogram)
		return newHistogram

	def _sliceSingleYZ(self, name, hist, bin):
		edges = [hist.yAxis()._edgeList[:], hist.zAxis()._edgeList[:], []]
		newHistogram = IHistogram2D(name, hist.title(), edges, hist.yAxis().isFixedBinning(), hist._getOption())
		lengthY = hist._sizeY
		lengthZ = hist._sizeZ
		bin += 2
		for i in range(lengthY):
			for j in range(lengthZ):
				newHistogram._binEntries[i, j, 0] = hist._binEntries[bin, i, j]
				newHistogram._binSumOfWeights[i, j, 0] = hist._binSumOfWeights[bin, i, j]
				newHistogram._binSumOfErrors[i, j, 0] = hist._binSumOfErrors[bin, i, j]
				newHistogram._binSumOfTorquesX[i, j, 0] = hist._binSumOfTorquesY[bin, i, j]
				newHistogram._binSumOfTorquesY[i, j, 0] = hist._binSumOfTorquesZ[bin, i, j]
				newHistogram._binSumOfInertialsX[i, j, 0] = hist._binSumOfInertialsY[bin, i, j]
				newHistogram._binSumOfInertialsY[i, j, 0] = hist._binSumOfInertialsZ[bin, i, j]
		return newHistogram

	def sliceYZ(self, name, hist, data1, data2 = None):
		edges = [hist.yAxis()._edgeList[:], hist.zAxis()._edgeList[:], []]
		newHistogram = IHistogram2D(name, hist.title(), edges, hist.yAxis().isFixedBinning(), hist._getOption())
		axis = hist.xAxis()
		length = hist._sizeX
		if (data1 == axis.UNDERFLOW_BIN) and (data2 == axis.OVERFLOW_BIN):
			binRange = range(length - 2)
			binRange.append(axis.UNDERFLOW_BIN)
			binRange.append(axis.OVERFLOW_BIN)
		elif (data1 == axis.UNDERFLOW_BIN) and (data2 != axis.OVERFLOW_BIN):
			binRange = range(data2 + 1)
			binRange.append(axis.UNDERFLOW_BIN)
		elif (data1 != axis.UNDERFLOW_BIN) and (data2 == axis.OVERFLOW_BIN):
			binRange = range(data1, length - 2)
			binRange.append(axis.OVERFLOW_BIN)
		elif (data1 != axis.UNDERFLOW_BIN) and (data2 != axis.OVERFLOW_BIN):
			binRange = range(data1, data2 + 1)
		else:
			raise IllegalArgumentException()
		for bin in binRange:
			newHistogram.add(self._sliceSingleYZ('temp', hist, bin))
		self._getTree()._mkObject(name, newHistogram)
		return newHistogram
