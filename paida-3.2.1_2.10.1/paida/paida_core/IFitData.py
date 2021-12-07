from paida.paida_core.PAbsorber import *
from paida.paida_core.IRangeSet import *
from paida.paida_core.PExceptions import *
from paida.paida_core.IHistogram1D import *
from paida.paida_core.IHistogram2D import *
from paida.paida_core.IHistogram3D import *
from paida.paida_core.ICloud1D import *
from paida.paida_core.ICloud2D import *
from paida.paida_core.ICloud3D import *
from paida.paida_core.IProfile1D import *
from paida.paida_core.IProfile2D import *
from paida.paida_core.IDataPointSet import *
from paida.paida_core.ITuple import *
from paida.paida_core.IEvaluator import *
import paida.paida_core.PTypes as PTypes

import types

class IFitData:
	def __init__(self):
		self._connection = []
		self._range = []
		self._binned = None
		self._dataDescription = ''

	def create1DConnection(self, data1, data2 = None, data3 = None):
		centers = []
		weights = []
		errorsP = []
		errorsM = []
		if isinstance(data1, IHistogram1D) and (data2 == None) and (data3 == None):
			self._binned = True
			histogram = data1
			xAxis = histogram.axis()
			for xBinNumber in range(xAxis.bins()):
				weight = histogram.binHeight(xBinNumber)
				if weight == 0.0:
					xCenter = (xAxis.binLowerEdge(xBinNumber) + xAxis.binUpperEdge(xBinNumber)) / 2.0
				else:
					xCenter = histogram.binMean(xBinNumber)
				centers.append([xCenter])
				weights.append(weight)
				error = histogram._binError2(xBinNumber)
				errorsP.append(error)
				errorsM.append(error)

		elif isinstance(data1, ICloud1D) and (data2 == None) and (data3 == None):
			self._binned = False
			cloud = data1
			for entryNumber in range(cloud.entries()):
				xCenter = cloud.value(entryNumber)
				centers.append([xCenter])
				weights.append(None)
				errorsP.append(None)
				errorsM.append(None)

		elif isinstance(data1, IProfile1D) and (data2 == None) and (data3 == None):
			self._binned = True
			profile = data1
			xAxis = profile.axis()
			for xBinNumber in range(xAxis.bins()):
				weight = profile.binHeight(xBinNumber)
				if weight == 0.0:
					xCenter = (xAxis.binLowerEdge(xBinNumber) + xAxis.binUpperEdge(xBinNumber)) / 2.0
				else:
					xCenter = profile.binMean(xBinNumber)
				centers.append([xCenter])
				weights.append(weight)
				error = profile._binError2(xBinNumber)
				errorsP.append(error)
				errorsM.append(error)

		elif isinstance(data1, IDataPointSet) and isinstance(data2, types.IntType) and isinstance(data3, types.IntType):
			self._binned = True
			dataPointSet = data1
			xIndex = data2
			valIndex = data3
			for offset in range(dataPointSet.size()):
				dataPoint = dataPointSet.point(offset)
				x = dataPoint.coordinate(xIndex)
				y = dataPoint.coordinate(valIndex)
				centers.append([x.value()])
				weights.append(y.value())
				errorsP.append(y.errorPlus()**2)
				errorsM.append(y.errorMinus()**2)

		else:
			raise TypeError('Invalid arguments.')

		self._connection = [centers, weights, errorsP, errorsM]
		self._range.append(IRangeSet())

	def create2DConnection(self, data1, data2 = None, data3 = None, data4 = None):
		centers = []
		weights = []
		errorsP = []
		errorsM = []
		if isinstance(data1, IHistogram2D) and (data2 == None) and (data3 == None) and (data4 == None):
			self._binned = True
			histogram = data1
			xAxis = histogram.xAxis()
			yAxis = histogram.yAxis()
			for xBinNumber in range(xAxis.bins()):
				for yBinNumber in range(yAxis.bins()):
					weight = histogram.binHeight(xBinNumber, yBinNumber)
					if weight == 0.0:
						xCenter = (xAxis.binLowerEdge(xBinNumber) + xAxis.binUpperEdge(xBinNumber)) / 2.0
						yCenter = (yAxis.binLowerEdge(yBinNumber) + yAxis.binUpperEdge(yBinNumber)) / 2.0
					else:
						xCenter = histogram.binMeanX(xBinNumber, yBinNumber)
						yCenter = histogram.binMeanY(xBinNumber, yBinNumber)
					centers.append([xCenter, yCenter])
					weights.append(weight)
					error = histogram._binError2(xBinNumber, yBinNumber)
					errorsP.append(error)
					errorsM.append(error)

		elif isinstance(data1, IHistogram2D) and isinstance(data2, types.IntType) and isinstance(data3, types.IntType) and (data4 == None):
			self._binned = True
			histogram = data1
			xIndex = data2
			yIndex = data3
			xAxis = histogram.xAxis()
			yAxis = histogram.yAxis()
			for xBinNumber in range(xAxis.bins()):
				for yBinNumber in range(yAxis.bins()):
					weight = histogram.binHeight(xBinNumber, yBinNumber)
					if weight == 0.0:
						xCenter = (xAxis.binLowerEdge(xBinNumber) + xAxis.binUpperEdge(xBinNumber)) / 2.0
						yCenter = (yAxis.binLowerEdge(yBinNumber) + yAxis.binUpperEdge(yBinNumber)) / 2.0
					else:
						xCenter = histogram.binMeanX(xBinNumber, yBinNumber)
						yCenter = histogram.binMeanY(xBinNumber, yBinNumber)
					center = [None, None]
					center[xIndex] = xCenter
					center[yIndex] = yCenter
					centers.append(center)
					weights.append(weight)
					error = histogram._binError2(xBinNumber, yBinNumber)
					errorsP.append(error)
					errorsM.append(error)

		elif isinstance(data1, ICloud2D) and (data2 == None) and (data3 == None) and (data4 == None):
			self._binned = False
			cloud = data1
			for entryNumber in range(cloud.entries()):
				xCenter = cloud.valueX(entryNumber)
				yCenter = cloud.valueY(entryNumber)
				centers.append([xCenter, yCenter])
				weights.append(None)
				errorsP.append(None)
				errorsM.append(None)

		elif isinstance(data1, ICloud2D) and isinstance(data2, types.IntType) and isinstance(data3, types.IntType) and (data4 == None):
			self._binned = False
			cloud = data1
			xIndex = data2
			yIndex = data3
			for entryNumber in range(cloud.entries()):
				center = [None, None]
				center[xIndex] = cloud.valueX(entryNumber)
				center[yIndex] = cloud.valueY(entryNumber)
				centers.append(center)
				weights.append(None)
				errorsP.append(None)
				errorsM.append(None)

		elif isinstance(data1, IProfile2D) and (data2 == None) and (data3 == None) and (data4 == None):
			self._binned = True
			profile = data1
			xAxis = profile.xAxis()
			yAxis = profile.yAxis()
			for xBinNumber in range(xAxis.bins()):
				for yBinNumber in range(yAxis.bins()):
					weight = profile.binHeight(xBinNumber, yBinNumber)
					if weight == 0.0:
						xCenter = (xAxis.binLowerEdge(xBinNumber) + xAxis.binUpperEdge(xBinNumber)) / 2.0
						yCenter = (yAxis.binLowerEdge(yBinNumber) + yAxis.binUpperEdge(yBinNumber)) / 2.0
					else:
						xCenter = profile.binMeanX(xBinNumber, yBinNumber)
						yCenter = profile.binMeanY(xBinNumber, yBinNumber)
					centers.append([xCenter, yCenter])
					weights.append(weight)
					error = profile._binError2(xBinNumber, yBinNumber)
					errorsP.append(error)
					errorsM.append(error)

		elif isinstance(data1, IProfile2D) and isinstance(data2, types.IntType) and isinstance(data3, types.IntType) and (data4 == None):
			self._binned = True
			profile = data1
			xIndex = data2
			yIndex = data3
			xAxis = profile.xAxis()
			yAxis = profile.yAxis()
			for xBinNumber in range(xAxis.bins()):
				for yBinNumber in range(yAxis.bins()):
					weight = profile.binHeight(xBinNumber, yBinNumber)
					if weight == 0.0:
						xCenter = (xAxis.binLowerEdge(xBinNumber) + xAxis.binUpperEdge(xBinNumber)) / 2.0
						yCenter = (yAxis.binLowerEdge(yBinNumber) + yAxis.binUpperEdge(yBinNumber)) / 2.0
					else:
						xCenter = profile.binMeanX(xBinNumber, yBinNumber)
						yCenter = profile.binMeanY(xBinNumber, yBinNumber)
					center = [None, None]
					center[xIndex] = xCenter
					center[yIndex] = yCenter
					centers.append(center)
					weights.append(weight)
					error = profile._binError2(xBinNumber, yBinNumber)
					errorsP.append(error)
					errorsM.append(error)

		elif isinstance(data1, IDataPointSet) and isinstance(data2, types.IntType) and isinstance(data3, types.IntType) and isinstance(data4, types.IntType):
			self._binned = True
			dataPointSet = data1
			xIndex = data2
			yIndex = data3
			valIndex = data4
			for offset in range(dataPointSet.size()):
				dataPoint = dataPointSet.point(offset)
				x = dataPoint.coordinate(xIndex)
				y = dataPoint.coordinate(yIndex)
				z = dataPoint.coordinate(valIndex)
				centers.append([x.value(), y.value()])
				weights.append(z.value())
				errorsP.append(z.errorPlus()**2)
				errorsM.append(z.errorMinus()**2)

		else:
			raise TypeError('Invalid arguments.')

		self._connection = [centers, weights, errorsP, errorsM]
		self._range.append(IRangeSet())
		self._range.append(IRangeSet())

	def create3DConnection(self, data1, data2 = None, data3 = None, data4 = None, data5 = None):
		centers = []
		weights = []
		errorsP = []
		errorsM = []
		if isinstance(data1, IHistogram3D) and (data2 == None) and (data3 == None) and (data4 == None) and (data5 == None):
			self._binned = True
			histogram = data1
			xAxis = histogram.xAxis()
			yAxis = histogram.yAxis()
			zAxis = histogram.zAxis()
			for xBinNumber in range(xAxis.bins()):
				for yBinNumber in range(yAxis.bins()):
					for zBinNumber in range(zAxis.bins()):
						weight = histogram.binHeight(xBinNumber, yBinNumber, zBinNumber)
						if weight == 0.0:
							xCenter = (xAxis.binLowerEdge(xBinNumber) + xAxis.binUpperEdge(xBinNumber)) / 2.0
							yCenter = (yAxis.binLowerEdge(yBinNumber) + yAxis.binUpperEdge(yBinNumber)) / 2.0
							zCenter = (zAxis.binLowerEdge(zBinNumber) + zAxis.binUpperEdge(zBinNumber)) / 2.0
						else:
							xCenter = histogram.binMeanX(xBinNumber, yBinNumber, zBinNumber)
							yCenter = histogram.binMeanY(xBinNumber, yBinNumber, zBinNumber)
							zCenter = histogram.binMeanZ(xBinNumber, yBinNumber, zBinNumber)
						centers.append([xCenter, yCenter, zCenter])
						weights.append(weight)
						error = histogram._binError2(xBinNumber, yBinNumber, zBinNumber)
						errorsP.append(error)
						errorsM.append(error)

		elif isinstance(data1, IHistogram3D) and isinstance(data2, types.IntType) and isinstance(data3, types.IntType) and isinstance(data4, types.IntType) and (data5 == None):
			self._binned = True
			histogram = data1
			xIndex = data2
			yIndex = data3
			zIndex = data4
			xAxis = histogram.xAxis()
			yAxis = histogram.yAxis()
			zAxis = histogram.zAxis()
			for xBinNumber in range(xAxis.bins()):
				for yBinNumber in range(yAxis.bins()):
					for zBinNumber in range(zAxis.bins()):
						weight = histogram.binHeight(xBinNumber, yBinNumber, zBinNumber)
						if weight == 0.0:
							xCenter = (xAxis.binLowerEdge(xBinNumber) + xAxis.binUpperEdge(xBinNumber)) / 2.0
							yCenter = (yAxis.binLowerEdge(yBinNumber) + yAxis.binUpperEdge(yBinNumber)) / 2.0
							zCenter = (zAxis.binLowerEdge(zBinNumber) + zAxis.binUpperEdge(zBinNumber)) / 2.0
						else:
							xCenter = histogram.binMeanX(xBinNumber, yBinNumber, zBinNumber)
							yCenter = histogram.binMeanY(xBinNumber, yBinNumber, zBinNumber)
							zCenter = histogram.binMeanZ(xBinNumber, yBinNumber, zBinNumber)
						center = [None, None, None]
						center[xIndex] = xCenter
						center[yIndex] = yCenter
						center[zIndex] = zCenter
						centers.append(center)
						weights.append(weight)
						error = histogram._binError2(xBinNumber, yBinNumber, zBinNumber)
						errorsP.append(error)
						errorsM.append(error)

		elif isinstance(data1, ICloud3D) and (data2 == None) and (data3 == None) and (data4 == None) and (data5 == None):
			self._binned = False
			cloud = data1
			for entryNumber in range(cloud.entries()):
				xCenter = cloud.valueX(entryNumber)
				yCenter = cloud.valueY(entryNumber)
				zCenter = cloud.valueZ(entryNumber)
				centers.append([xCenter, yCenter, zCenter])
				weights.append(None)
				errorsP.append(None)
				errorsM.append(None)

		elif isinstance(data1, ICloud3D) and isinstance(data2, types.IntType) and isinstance(data3, types.IntType) and isinstance(data4, types.IntType) and (data5 == None):
			self._binned = False
			cloud = data1
			xIndex = data2
			yIndex = data3
			zIndex = data4
			for entryNumber in range(cloud.entries()):
				center = [None, None, None]
				center[xIndex] = cloud.valueX(entryNumber)
				center[yIndex] = cloud.valueY(entryNumber)
				center[zIndex] = cloud.valueZ(entryNumber)
				centers.append(center)
				weights.append(None)
				errorsP.append(None)
				errorsM.append(None)

		elif isinstance(data1, IDataPointSet) and isinstance(data2, types.IntType) and isinstance(data3, types.IntType) and isinstance(data4, types.IntType) and isinstance(data5, types.IntType):
			self._binned = True
			dataPointSet = data1
			xIndex = data2
			yIndex = data3
			zIndex = data4
			valIndex = data5
			for offset in range(dataPointSet.size()):
				dataPoint = dataPointSet.point(offset)
				x = dataPoint.coordinate(xIndex)
				y = dataPoint.coordinate(yIndex)
				z = dataPoint.coordinate(zIndex)
				val = dataPoint.coordinate(valIndex)
				centers.append([x.value(), y.value(), z.value()])
				weights.append(val.value())
				errorsP.append(val.errorPlus()**2)
				errorsM.append(val.errorMinus()**2)

		else:
			raise TypeError('Invalid arguments.')

		self._connection = [centers, weights, errorsP, errorsM]
		self._range.append(IRangeSet())
		self._range.append(IRangeSet())
		self._range.append(IRangeSet())

	def createConnection(self, data1 = None, data2 = None, data3 = None):
		centers = []
		weights = []
		errorsP = []
		errorsM = []
		if isinstance(data1, ITuple) and hasattr(data2, '__iter__') and (data3 == None):
			self._binned = False
			iTuple = data1
			colData = data2
			length = iTuple.rows()
			if length == -1:
				raise TypeError('This ITuple has no row.')
			iTuple.start()
			if isinstance(colData[0], types.StringTypes):
				columnIndices = []
				evaluatorCs = []
				for columnName in colData:
					columnIndex = iTuple.findColumn(columnName)
					columnIndices.append(columnIndex)
					columnType = iTuple.columnType(columnIndex)
					if columnType == PTypes.Double:
						evaluatorCs.append(iTuple.getDouble)
					elif columnType == PTypes.Float:
						evaluatorCs.append(iTuple.getFloat)
					elif columnType == PTypes.Int:
						evaluatorCs.append(iTuple.getInt)
					elif columnType == PTypes.Short:
						evaluatorCs.append(iTuple.getShort)
					elif columnType == PTypes.Long:
						evaluatorCs.append(iTuple.getLong)
					elif columnType == PTypes.Char:
						evaluatorCs.append(iTuple.getChar)
					elif columnType == PTypes.Byte:
						evaluatorCs.append(iTuple.getByte)
					elif columnType == PTypes.Boolean:
						evaluatorCs.append(iTuple.getBoolean)
					elif columnType == PTypes.String:
						evaluatorCs.append(iTuple.getString)
					elif columnType == PTypes.Object:
						evaluatorCs.append(iTuple.getObject)
					elif columnType == PTypes.Tuple:
						evaluatorCs.append(iTuple.getTuple)
					else:
						raise TypeError('Illegal column type %s' % columnType)
				while iTuple.next():
					center = []
					for i, columnIndex in enumerate(columnIndices):
						center.append(evaluatorCs[i](columnIndex))
					centers.append(center)
					weights.append(None)
					errorsP.append(None)
					errorsM.append(None)
			elif isinstance(colData[0], IEvaluator):
				evaluatorCs = []
				for evaluator in colData:
					evaluator.initialize(iTuple)
					evaluatorCs.append(evaluator.evaluateDouble)
				while iTuple.next():
					center = []
					for evaluatorC in evaluatorCs:
						center.append(evaluatorC())
					centers.append(center)
					weights.append(None)
					errorsP.append(None)
					errorsM.append(None)
			else:
				raise TypeError('Illegal list data type.')

			self._connection = [centers, weights, errorsP, errorsM]
			for i in range(len(colData)):
				self._range.append(IRangeSet())

		elif isinstance(data1, IDataPointSet) and hasattr(data2, '__iter__') and isinstance(data3, types.IntType):
			self._binned = True
			dataPointSet = data1
			indices = data2
			valIndex = data3
			for offset in range(dataPointSet.size()):
				dataPoint = dataPointSet.point(offset)
				val = dataPoint.coordinate(valIndex)
				center = []
				if indices == []:
					center.append(offset)
				else:
					for i in indices:
						center.append(dataPoint.coordinate(i).value())
				centers.append(center)
				weights.append(val.value())
				errorsP.append(val.errorPlus()**2)
				errorsM.append(val.errorMinus()**2)
			self._connection = [centers, weights, errorsP, errorsM]
			for i in range(len(indices)):
				self._range.append(IRangeSet())

		else:
			raise TypeError('Invalid arguments.')

	def reset(self):
		self._connection = []
		self._range = []
		self._binned = None
		self._dataDescription = ''

	def dimension(self):
		return len(self._range)

	def dataDescription(self):
		return self._dataDescription

	def range(self, i):
		try:
			return self._range[i]
		except IndexError:
			raise TypeError('The Range[%d] does not exist.' % i)
