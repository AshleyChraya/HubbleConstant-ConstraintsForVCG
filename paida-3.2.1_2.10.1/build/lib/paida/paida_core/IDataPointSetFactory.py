from paida.paida_core.PAbsorber import *
from paida.paida_core.IAnnotation import *
from paida.paida_core.IDataPointSet import *
from paida.paida_core.PExceptions import *
from paida.paida_core.PUtilities import *

from math import sqrt
import types
import os

class IDataPointSetFactory:

	def __init__(self, tree):
		self._tree = tree

	def create(self, data1, data2, data3 = None):
		if (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and (type(data3) == types.IntType):
			name = data1
			title = data2
			dimension = data3
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (type(data2) == types.IntType) and (data3 == None):
			name = data1
			title = data1
			dimension = data2
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IHistogram1D') and (data3 == None):
			name = data1
			histogram = data2
			title = histogram.title()
			dimension = 2
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			axisX = histogram.axis()
			for indexX in range(axisX.bins()):
				binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
				binHeight = histogram.binHeight(indexX)
				binError = histogram.binError(indexX)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binHeight)
				measurementY.setErrorPlus(binError)
				measurementY.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IHistogram1D') and (type(data3) in types.StringTypes):
			name = data1
			histogram = data2
			options = optionAnalyzer(data3)
			title = histogram.title()
			dimension = 2
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension, options)
			axisX = histogram.axis()
			for indexX in range(axisX.bins()):
				binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
				binHeight = histogram.binHeight(indexX)
				binError = histogram.binError(indexX)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binHeight)
				measurementY.setErrorPlus(binError)
				measurementY.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IHistogram2D') and (data3 == None):
			name = data1
			histogram = data2
			title = histogram.title()
			dimension = 3
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			axisX = histogram.xAxis()
			axisY = histogram.yAxis()
			for indexX in range(axisX.bins()):
				for indexY in range(axisY.bins()):
					binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
					binCenterY = (axisY.binLowerEdge(indexY) + axisY.binUpperEdge(indexY)) / 2.0
					binHeight = histogram.binHeight(indexX, indexY)
					binError = histogram.binError(indexX, indexY)
					dataPoint = dataPointSet.addPoint()
					measurementX = dataPoint.coordinate(0)
					measurementX.setValue(binCenterX)
					measurementX.setErrorPlus(0.0)
					measurementX.setErrorMinus(0.0)
					measurementY = dataPoint.coordinate(1)
					measurementY.setValue(binCenterY)
					measurementY.setErrorPlus(0.0)
					measurementY.setErrorMinus(0.0)
					measurementZ = dataPoint.coordinate(2)
					measurementZ.setValue(binHeight)
					measurementZ.setErrorPlus(binError)
					measurementZ.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IHistogram2D') and (type(data3) in types.StringTypes):
			name = data1
			histogram = data2
			options = optionAnalyzer(data3)
			title = histogram.title()
			dimension = 3
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension, options)
			axisX = histogram.xAxis()
			axisY = histogram.yAxis()
			for indexX in range(axisX.bins()):
				for indexY in range(axisY.bins()):
					binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
					binCenterY = (axisY.binLowerEdge(indexY) + axisY.binUpperEdge(indexY)) / 2.0
					binHeight = histogram.binHeight(indexX, indexY)
					binError = histogram.binError(indexX, indexY)
					dataPoint = dataPointSet.addPoint()
					measurementX = dataPoint.coordinate(0)
					measurementX.setValue(binCenterX)
					measurementX.setErrorPlus(0.0)
					measurementX.setErrorMinus(0.0)
					measurementY = dataPoint.coordinate(1)
					measurementY.setValue(binCenterY)
					measurementY.setErrorPlus(0.0)
					measurementY.setErrorMinus(0.0)
					measurementZ = dataPoint.coordinate(2)
					measurementZ.setValue(binHeight)
					measurementZ.setErrorPlus(binError)
					measurementZ.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IHistogram3D') and (data3 == None):
			name = data1
			histogram = data2
			title = histogram.title()
			dimension = 4
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			axisX = histogram.xAxis()
			axisY = histogram.yAxis()
			axisZ = histogram.zAxis()
			for indexX in range(axisX.bins()):
				for indexY in range(axisY.bins()):
					for indexZ in range(axisZ.bins()):
						binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
						binCenterY = (axisY.binLowerEdge(indexY) + axisY.binUpperEdge(indexY)) / 2.0
						binCenterZ = (axisZ.binLowerEdge(indexZ) + axisZ.binUpperEdge(indexZ)) / 2.0
						binHeight = histogram.binHeight(indexX, indexY, indexZ)
						binError = histogram.binError(indexX, indexY, indexZ)
						dataPoint = dataPointSet.addPoint()
						measurementX = dataPoint.coordinate(0)
						measurementX.setValue(binCenterX)
						measurementX.setErrorPlus(0.0)
						measurementX.setErrorMinus(0.0)
						measurementY = dataPoint.coordinate(1)
						measurementY.setValue(binCenterY)
						measurementY.setErrorPlus(0.0)
						measurementY.setErrorMinus(0.0)
						measurementZ = dataPoint.coordinate(2)
						measurementZ.setValue(binCenterZ)
						measurementZ.setErrorPlus(0.0)
						measurementZ.setErrorMinus(0.0)
						measurementV = dataPoint.coordinate(3)
						measurementV.setValue(binHeight)
						measurementV.setErrorPlus(binError)
						measurementV.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IHistogram3D') and (type(data3) in types.StringTypes):
			name = data1
			histogram = data2
			options = optionAnalyzer(data3)
			title = histogram.title()
			dimension = 4
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension, options)
			axisX = histogram.xAxis()
			axisY = histogram.yAxis()
			axisZ = histogram.zAxis()
			for indexX in range(axisX.bins()):
				for indexY in range(axisY.bins()):
					for indexZ in range(axisZ.bins()):
						binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
						binCenterY = (axisY.binLowerEdge(indexY) + axisY.binUpperEdge(indexY)) / 2.0
						binCenterZ = (axisZ.binLowerEdge(indexZ) + axisZ.binUpperEdge(indexZ)) / 2.0
						binHeight = histogram.binHeight(indexX, indexY, indexZ)
						binError = histogram.binError(indexX, indexY, indexZ)
						dataPoint = dataPointSet.addPoint()
						measurementX = dataPoint.coordinate(0)
						measurementX.setValue(binCenterX)
						measurementX.setErrorPlus(0.0)
						measurementX.setErrorMinus(0.0)
						measurementY = dataPoint.coordinate(1)
						measurementY.setValue(binCenterY)
						measurementY.setErrorPlus(0.0)
						measurementY.setErrorMinus(0.0)
						measurementZ = dataPoint.coordinate(2)
						measurementZ.setValue(binCenterZ)
						measurementZ.setErrorPlus(0.0)
						measurementZ.setErrorMinus(0.0)
						measurementV = dataPoint.coordinate(3)
						measurementV.setValue(binHeight)
						measurementV.setErrorPlus(binError)
						measurementV.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'ICloud1D') and (data3 == None):
			name = data1
			cloud = data2
			title = cloud.title()
			dimension = 2
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			for index in range(cloud.entries()):
				binCenterX = cloud.value(index)
				binHeight = cloud.weight(index)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binHeight)
				measurementY.setErrorPlus(0.0)
				measurementY.setErrorMinus(0.0)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'ICloud1D') and (type(data3) in types.StringTypes):
			name = data1
			cloud = data2
			options = optionAnalyzer(data3)
			title = cloud.title()
			dimension = 2
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension, options)
			for index in range(cloud.entries()):
				binCenterX = cloud.value(index)
				binHeight = cloud.weight(index)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binHeight)
				measurementY.setErrorPlus(0.0)
				measurementY.setErrorMinus(0.0)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'ICloud2D') and (data3 == None):
			name = data1
			cloud = data2
			title = cloud.title()
			dimension = 3
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			for index in range(cloud.entries()):
				binCenterX = cloud.valueX(index)
				binCenterY = cloud.valueY(index)
				binHeight = cloud.weight(index)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binCenterY)
				measurementY.setErrorPlus(0.0)
				measurementY.setErrorMinus(0.0)
				measurementZ = dataPoint.coordinate(2)
				measurementZ.setValue(binHeight)
				measurementZ.setErrorPlus(0.0)
				measurementZ.setErrorMinus(0.0)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'ICloud2D') and (type(data3) in types.StringTypes):
			name = data1
			cloud = data2
			options = optionAnalyzer(data3)
			title = cloud.title()
			dimension = 3
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension, options)
			for index in range(cloud.entries()):
				binCenterX = cloud.valueX(index)
				binCenterY = cloud.valueY(index)
				binHeight = cloud.weight(index)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binCenterY)
				measurementY.setErrorPlus(0.0)
				measurementY.setErrorMinus(0.0)
				measurementZ = dataPoint.coordinate(2)
				measurementZ.setValue(binHeight)
				measurementZ.setErrorPlus(0.0)
				measurementZ.setErrorMinus(0.0)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'ICloud3D') and (data3 == None):
			name = data1
			cloud = data2
			title = cloud.title()
			dimension = 4
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			for index in range(cloud.entries()):
				binCenterX = cloud.valueX(index)
				binCenterY = cloud.valueY(index)
				binCenterZ = cloud.valueZ(index)
				binHeight = cloud.weight(index)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binCenterY)
				measurementY.setErrorPlus(0.0)
				measurementY.setErrorMinus(0.0)
				measurementZ = dataPoint.coordinate(2)
				measurementZ.setValue(binCenterZ)
				measurementZ.setErrorPlus(0.0)
				measurementZ.setErrorMinus(0.0)
				measurementV = dataPoint.coordinate(2)
				measurementV.setValue(binHeight)
				measurementV.setErrorPlus(0.0)
				measurementV.setErrorMinus(0.0)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'ICloud3D') and (type(data3) in types.StringTypes):
			name = data1
			cloud = data2
			options = optionAnalyzer(data3)
			title = cloud.title()
			dimension = 4
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension, options)
			for index in range(cloud.entries()):
				binCenterX = cloud.valueX(index)
				binCenterY = cloud.valueY(index)
				binCenterZ = cloud.valueZ(index)
				binHeight = cloud.weight(index)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binCenterY)
				measurementY.setErrorPlus(0.0)
				measurementY.setErrorMinus(0.0)
				measurementZ = dataPoint.coordinate(2)
				measurementZ.setValue(binCenterZ)
				measurementZ.setErrorPlus(0.0)
				measurementZ.setErrorMinus(0.0)
				measurementV = dataPoint.coordinate(2)
				measurementV.setValue(binHeight)
				measurementV.setErrorPlus(0.0)
				measurementV.setErrorMinus(0.0)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IProfile1D') and (data3 == None):
			name = data1
			histogram = data2
			title = histogram.title()
			dimension = 2
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			axisX = histogram.axis()
			for indexX in range(axisX.bins()):
				binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
				binHeight = histogram.binHeight(indexX)
				binError = histogram.binError(indexX)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binHeight)
				measurementY.setErrorPlus(binError)
				measurementY.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IProfile1D') and (type(data3) in types.StringTypes):
			name = data1
			histogram = data2
			options = optionAnalyzer(data3)
			title = histogram.title()
			dimension = 2
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension, options)
			axisX = histogram.axis()
			for indexX in range(axisX.bins()):
				binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
				binHeight = histogram.binHeight(indexX)
				binError = histogram.binError(indexX)
				dataPoint = dataPointSet.addPoint()
				measurementX = dataPoint.coordinate(0)
				measurementX.setValue(binCenterX)
				measurementX.setErrorPlus(0.0)
				measurementX.setErrorMinus(0.0)
				measurementY = dataPoint.coordinate(1)
				measurementY.setValue(binHeight)
				measurementY.setErrorPlus(binError)
				measurementY.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IProfile2D') and (data3 == None):
			name = data1
			histogram = data2
			title = histogram.title()
			dimension = 3
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
			axisX = histogram.xAxis()
			axisY = histogram.yAxis()
			for indexX in range(axisX.bins()):
				for indexY in range(axisY.bins()):
					binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
					binCenterY = (axisY.binLowerEdge(indexY) + axisY.binUpperEdge(indexY)) / 2.0
					binHeight = histogram.binHeight(indexX, indexY)
					binError = histogram.binError(indexX, indexY)
					dataPoint = dataPointSet.addPoint()
					measurementX = dataPoint.coordinate(0)
					measurementX.setValue(binCenterX)
					measurementX.setErrorPlus(0.0)
					measurementX.setErrorMinus(0.0)
					measurementY = dataPoint.coordinate(1)
					measurementY.setValue(binCenterY)
					measurementY.setErrorPlus(0.0)
					measurementY.setErrorMinus(0.0)
					measurementZ = dataPoint.coordinate(2)
					measurementZ.setValue(binHeight)
					measurementZ.setErrorPlus(binError)
					measurementZ.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		elif (type(data1) in types.StringTypes) and (data2.__class__.__name__ == 'IProfile2D') and (type(data3) in types.StringTypes):
			name = data1
			histogram = data2
			options = optionAnalyzer(data3)
			title = histogram.title()
			dimension = 3
			dataPointSet = IDataPointSet(os.path.basename(name), title, dimension, options)
			axisX = histogram.xAxis()
			axisY = histogram.yAxis()
			for indexX in range(axisX.bins()):
				for indexY in range(axisY.bins()):
					binCenterX = (axisX.binLowerEdge(indexX) + axisX.binUpperEdge(indexX)) / 2.0
					binCenterY = (axisY.binLowerEdge(indexY) + axisY.binUpperEdge(indexY)) / 2.0
					binHeight = histogram.binHeight(indexX, indexY)
					binError = histogram.binError(indexX, indexY)
					dataPoint = dataPointSet.addPoint()
					measurementX = dataPoint.coordinate(0)
					measurementX.setValue(binCenterX)
					measurementX.setErrorPlus(0.0)
					measurementX.setErrorMinus(0.0)
					measurementY = dataPoint.coordinate(1)
					measurementY.setValue(binCenterY)
					measurementY.setErrorPlus(0.0)
					measurementY.setErrorMinus(0.0)
					measurementZ = dataPoint.coordinate(2)
					measurementZ.setValue(binHeight)
					measurementZ.setErrorPlus(binError)
					measurementZ.setErrorMinus(binError)
			self._tree._mkObject(name, dataPointSet)
			return dataPointSet
		else:
			raise IllegalArgumentException()

	def createX(self, data1, data2, data3, data4 = None, data5 = None):
		if (type(data1) in types.StringTypes) and hasattr(data2, '__iter__') and hasattr(data3, '__iter__') and (data4 == None) and (data5 == None):
			name = data1
			title = data1
			x = data2
			xep = data3
			xem = data3
		elif (type(data1) in types.StringTypes) and hasattr(data2, '__iter__') and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and (data5 == None):
			name = data1
			title = data1
			x = data2
			xep = data3
			xem = data4
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and (data5 == None):
			name = data1
			title = data2
			x = data3
			xep = data4
			xem = data4
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__'):
			name = data1
			title = data2
			x = data3
			xep = data4
			xem = data5
		else:
			raise IllegalArgumentException()

		dimension = 2
		dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)

		for indexX in range(len(x)):
			dataPoint = dataPointSet.addPoint()
			measurementX = dataPoint.coordinate(0)
			measurementX.setValue(x[indexX])
			measurementX.setErrorPlus(xep[indexX])
			measurementX.setErrorMinus(xem[indexX])
			measurementY = dataPoint.coordinate(1)
			measurementY.setValue(indexX)
			measurementY.setErrorPlus(0.0)
			measurementY.setErrorMinus(0.0)
		self._tree._mkObject(name, dataPointSet)
		return dataPointSet

	def createY(self, data1, data2, data3, data4 = None, data5 = None):
		if (type(data1) in types.StringTypes) and hasattr(data2, '__iter__') and hasattr(data3, '__iter__') and (data4 == None) and (data5 == None):
			name = data1
			title = data1
			y = data2
			yep = data3
			yem = data3
		elif (type(data1) in types.StringTypes) and hasattr(data2, '__iter__') and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and (data5 == None):
			name = data1
			title = data1
			y = data2
			yep = data3
			yem = data4
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and (data5 == None):
			name = data1
			title = data2
			y = data3
			yep = data4
			yem = data4
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__'):
			name = data1
			title = data2
			y = data3
			yep = data4
			yem = data5
		else:
			raise IllegalArgumentException()

		dimension = 2
		dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)

		for indexY in range(len(y)):
			dataPoint = dataPointSet.addPoint()
			measurementX = dataPoint.coordinate(0)
			measurementX.setValue(indexY)
			measurementX.setErrorPlus(0.0)
			measurementX.setErrorMinus(0.0)
			measurementY = dataPoint.coordinate(1)
			measurementY.setValue(y[indexY])
			measurementY.setErrorPlus(yep[indexY])
			measurementY.setErrorMinus(yem[indexY])
		self._tree._mkObject(name, dataPointSet)
		return dataPointSet

	def createXY(self, data1, data2, data3, data4, data5, data6 = None, data7 = None, data8 = None):
		if (type(data1) in types.StringTypes) and hasattr(data2, '__iter__') and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and (data6 == None) and (data7 == None) and (data8 == None):
			name = data1
			title = data1
			x = data2
			y = data3
			xep = data4
			yep = data5
			xem = data4
			yem = data5
		elif (type(data1) in types.StringTypes) and hasattr(data2, '__iter__') and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and hasattr(data6, '__iter__') and hasattr(data7, '__iter__') and (data8 == None):
			name = data1
			title = data1
			x = data2
			y = data3
			xep = data4
			yep = data5
			xem = data6
			yem = data7
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and hasattr(data6, '__iter__') and (data7 == None) and (data8 == None):
			name = data1
			title = data2
			x = data3
			y = data4
			xep = data5
			yep = data6
			xem = data5
			yem = data6
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and hasattr(data6, '__iter__') and hasattr(data7, '__iter__') and hasattr(data8, '__iter__'):
			name = data1
			title = data2
			x = data3
			y = data4
			xep = data5
			yep = data6
			xem = data7
			yem = data8
		else:
			raise IllegalArgumentException()

		dimension = 2
		dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)

		for indexX in range(len(x)):
			dataPoint = dataPointSet.addPoint()
			measurementX = dataPoint.coordinate(0)
			measurementX.setValue(x[indexX])
			measurementX.setErrorPlus(xep[indexX])
			measurementX.setErrorMinus(xem[indexX])
			measurementY = dataPoint.coordinate(1)
			measurementY.setValue(y[indexX])
			measurementY.setErrorPlus(yep[indexX])
			measurementY.setErrorMinus(yem[indexX])
		self._tree._mkObject(name, dataPointSet)
		return dataPointSet

	def createXYZ(self, data1, data2, data3, data4, data5, data6, data7, data8 = None, data9 = None, data10 = None, data11 = None):
		if (type(data1) in types.StringTypes) and hasattr(data2, '__iter__') and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and hasattr(data6, '__iter__') and hasattr(data7, '__iter__') and (data8 == None) and (data9 == None) and (data10 == None) and (data11 == None):
			name = data1
			title = data1
			x = data2
			y = data3
			z = data4
			xep = data5
			yep = data6
			zep = data7
			xem = data5
			yem = data6
			zem = data7
		elif (type(data1) in types.StringTypes) and hasattr(data2, '__iter__') and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and hasattr(data6, '__iter__') and hasattr(data7, '__iter__') and hasattr(data8, '__iter__') and hasattr(data9, '__iter__') and hasattr(data10, '__iter__') and (data11 == None):
			name = data1
			title = data1
			x = data2
			y = data3
			z = data4
			xep = data5
			yep = data6
			zep = data7
			xem = data8
			yem = data9
			zem = data10
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and hasattr(data6, '__iter__') and hasattr(data7, '__iter__') and hasattr(data8, '__iter__') and (data9 == None) and (data10 == None) and (data11 == None):
			name = data1
			title = data2
			x = data3
			y = data4
			z = data5
			xep = data6
			yep = data7
			zep = data8
			xem = data6
			yem = data7
			zem = data8
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and hasattr(data3, '__iter__') and hasattr(data4, '__iter__') and hasattr(data5, '__iter__') and hasattr(data6, '__iter__') and hasattr(data7, '__iter__') and hasattr(data8, '__iter__') and hasattr(data9, '__iter__') and hasattr(data10, '__iter__') and hasattr(data11, '__iter__'):
			name = data1
			title = data2
			x = data3
			y = data4
			z = data5
			xep = data6
			yep = data7
			zep = data8
			xem = data9
			yem = data10
			zem = data11
		else:
			raise IllegalArgumentException()

		dimension = 3
		dataPointSet = IDataPointSet(os.path.basename(name), title, dimension)

		for indexX in range(len(x)):
			dataPoint = dataPointSet.addPoint()
			measurementX = dataPoint.coordinate(0)
			measurementX.setValue(x[indexX])
			measurementX.setErrorPlus(xep[indexX])
			measurementX.setErrorMinus(xem[indexX])
			measurementY = dataPoint.coordinate(1)
			measurementY.setValue(y[indexX])
			measurementY.setErrorPlus(yep[indexX])
			measurementY.setErrorMinus(yem[indexX])
			measurementZ = dataPoint.coordinate(2)
			measurementZ.setValue(z[indexX])
			measurementZ.setErrorPlus(zep[indexX])
			measurementZ.setErrorMinus(zem[indexX])
		self._tree._mkObject(name, dataPointSet)
		return dataPointSet

	def _createCopy(self, name, dataPointSet):
		title = dataPointSet.title()
		dimension = dataPointSet.dimension()
		newDataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
		for offset in range(dataPointSet.size()):
			newDataPointSet.addPoint(dataPointSet.point(offset))
		return newDataPointSet

	def createCopy(self, name, dataPointSet):
		newDataPointSet = self._createCopy(os.path.basename(name), dataPointSet)
		self._tree._mkObject(name, newDataPointSet)
		return newDataPointSet

	def destroy(self, dataPointSet):
		self._tree._rmObject(dataPointSet)

	def add(self, name, dataPointSet1, dataPointSet2):
		if dataPointSet1.size() != dataPointSet2.size():
			raise IllegalArgumentException()
		if dataPointSet1.dimension() != dataPointSet2.dimension():
			raise IllegalArgumentException()
		title = '%s + %s' % (dataPointSet1.title(), dataPointSet2.title())
		dimension = dataPointSet1.dimension()
		newDataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
		for offset in range(dataPointSet1.size()):
			dataPoint = newDataPointSet.addPoint()
			dataPoint1 = dataPointSet1.point(offset)
			dataPoint2 = dataPointSet2.point(offset)
			for index in range(dimension):
				measurement = dataPoint.coordinate(index)
				measurement1 = dataPoint1.coordinate(index)
				measurement2 = dataPoint2.coordinate(index)
				measurement.setValue(measurement1.value() + measurement2.value())
				measurement.setErrorPlus(sqrt(measurement1.errorPlus()**2 + measurement2.errorPlus()**2))
				measurement.setErrorMinus(sqrt(measurement1.errorMinus()**2 + measurement2.errorMinus()**2))
		self._tree._mkObject(name, newDataPointSet)
		return newDataPointSet

	def subtract(self, name, dataPointSet1, dataPointSet2):
		if dataPointSet1.size() != dataPointSet2.size():
			raise IllegalArgumentException()
		if dataPointSet1.dimension() != dataPointSet2.dimension():
			raise IllegalArgumentException()
		title = '%s - %s' % (dataPointSet1.title(), dataPointSet2.title())
		dimension = dataPointSet1.dimension()
		newDataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
		for offset in range(dataPointSet1.size()):
			dataPoint = newDataPointSet.addPoint()
			dataPoint1 = dataPointSet1.point(offset)
			dataPoint2 = dataPointSet2.point(offset)
			for index in range(dimension):
				measurement = dataPoint.coordinate(index)
				measurement1 = dataPoint1.coordinate(index)
				measurement2 = dataPoint2.coordinate(index)
				measurement.setValue(measurement1.value() - measurement2.value())
				measurement.setErrorPlus(sqrt(measurement1.errorPlus()**2 + measurement2.errorPlus()**2))
				measurement.setErrorMinus(sqrt(measurement1.errorMinus()**2 + measurement2.errorMinus()**2))
		self._tree._mkObject(name, newDataPointSet)
		return newDataPointSet

	def multiply(self, name, dataPointSet1, dataPointSet2):
		if dataPointSet1.size() != dataPointSet2.size():
			raise IllegalArgumentException()
		if dataPointSet1.dimension() != dataPointSet2.dimension():
			raise IllegalArgumentException()
		title = '%s * %s' % (dataPointSet1.title(), dataPointSet2.title())
		dimension = dataPointSet1.dimension()
		newDataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
		for offset in range(dataPointSet1.size()):
			dataPoint = newDataPointSet.addPoint()
			dataPoint1 = dataPointSet1.point(offset)
			dataPoint2 = dataPointSet2.point(offset)
			for index in range(dimension):
				measurement = dataPoint.coordinate(index)
				measurement1 = dataPoint1.coordinate(index)
				measurement2 = dataPoint2.coordinate(index)
				measurement.setValue(measurement1.value() * measurement2.value())
				measurement.setErrorPlus(sqrt((measurement1.errorPlus() * measurement2.value())**2 + (measurement2.errorPlus() * measurement1.value())**2))
				measurement.setErrorMinus(sqrt((measurement1.errorMinus() * measurement2.value())**2 + (measurement2.errorMinus() * measurement1.value())**2))
		self._tree._mkObject(name, newDataPointSet)
		return newDataPointSet

	def divide(self, name, dataPointSet1, dataPointSet2):
		if dataPointSet1.size() != dataPointSet2.size():
			raise IllegalArgumentException()
		if dataPointSet1.dimension() != dataPointSet2.dimension():
			raise IllegalArgumentException()
		title = '%s / %s' % (dataPointSet1.title(), dataPointSet2.title())
		dimension = dataPointSet1.dimension()
		newDataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
		for offset in range(dataPointSet1.size()):
			dataPoint = newDataPointSet.addPoint()
			dataPoint1 = dataPointSet1.point(offset)
			dataPoint2 = dataPointSet2.point(offset)
			for index in range(dimension):
				measurement = dataPoint.coordinate(index)
				measurement1 = dataPoint1.coordinate(index)
				measurement2 = dataPoint2.coordinate(index)
				measurement.setValue(measurement1.value() / measurement2.value())
				measurement.setErrorPlus(sqrt((measurement1.errorPlus() * measurement2.value())**2 + (measurement2.errorPlus() * measurement1.value())**2) / measurement2.value()**2)
				measurement.setErrorMinus(sqrt((measurement1.errorMinus() * measurement2.value())**2 + (measurement2.errorMinus() * measurement1.value())**2) / measurement2.value()**2)
		self._tree._mkObject(name, newDataPointSet)
		return newDataPointSet

	def weightedMean(self, name, dataPointSet1, dataPointSet2):
		if dataPointSet1.size() != dataPointSet2.size():
			raise IllegalArgumentException()
		if dataPointSet1.dimension() != dataPointSet2.dimension():
			raise IllegalArgumentException()
		title = 'weighted mean of %s and %s' % (dataPointSet1.title(), dataPointSet2.title())
		dimension = dataPointSet1.dimension()
		newDataPointSet = IDataPointSet(os.path.basename(name), title, dimension)
		for offset in range(dataPointSet1.size()):
			dataPoint = newDataPointSet.addPoint()
			dataPoint1 = dataPointSet1.point(offset)
			dataPoint2 = dataPointSet2.point(offset)
			if dataPoint1.errorPlus() != dataPoint1.errorMinus():
				raise IllegalArgumentException('There are asymmetric errors.')
			else:
				error1 = dataPoint1.errorPlus()**2
			if dataPoint2.errorPlus() != dataPoint2.errorMinus():
				raise IllegalArgumentException('There are asymmetric errors.')
			else:
				error2 = dataPoint2.errorPlus()**2
			for index in range(dimension):
				measurement = dataPoint.coordinate(index)
				measurement1 = dataPoint1.coordinate(index)
				measurement2 = dataPoint2.coordinate(index)
				measurement.setValue((measurement1.value() * error2 + measurement2.value() * error1) / (error1 + error2))
				measurement.setErrorPlus(sqrt((error1 * error2) / (error1 + error2)))
				measurement.setErrorMinus(measurement.errorPlus())
		self._tree._mkObject(name, newDataPointSet)
		return newDataPointSet


