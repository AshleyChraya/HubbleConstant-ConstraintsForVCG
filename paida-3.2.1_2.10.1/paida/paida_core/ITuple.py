from paida.paida_core.PAbsorber import *
from paida.paida_core.IAnnotation import *
from paida.paida_core.PExceptions import *

import paida.paida_core.IBaseHistogram
import paida.paida_core.PUtilities
import paida.paida_core.PTypes as PAIDA_Types

import math
import types

def _converterObject(data):
	return data

class ITuple(object):
	__slots__ = ('_rowBuffer', '_rowIndex', '_rows', '_columnConverters', '_columnDefaults', '_columnNames', '_name', '_analyzedOption', '_annotation')

	def __init__(self, name, title, analyzedOption, columnNames, columnDefaults, columnConverters):
		self._annotation = IAnnotation()
		self._annotation.addItem('Title', title, True)

		self._name = name
		self._analyzedOption = analyzedOption
		self._columnNames = columnNames
		self._columnDefaults = columnDefaults
		self._columnConverters = columnConverters

		self._rowBuffer = columnDefaults[:]
		self._rows = []
		self._rowIndex = -1

	def _getOption(self):
		return self._analyzedOption

	def _setOptionString(self, optionString):
		self._analyzedOption = paida.paida_core.PUtilities.optionAnalyzer(optionString)

	def _getOptionString(self):
		return paida.paida_core.PUtilities.optionConstructor(self._analyzedOption)

	def annotation(self):
		return self._annotation

	def title(self):
		return self.annotation().value('Title')

	def setTitle(self, title):
		self.annotation().setValue('Title', title)

	def fill(self, data1, data2 = None):
		if data2 == None:
			for columnIndex, converter in enumerate(self._columnConverters):
				self._rowBuffer[columnIndex] = converter(data1[columnIndex])
		else:
			self._rowBuffer[data1] = self._columnConverters[data1](data2)

	def addRow(self):
		self._rows.append(self._rowBuffer)
		self._rowBuffer = self._columnDefaults[:]

	def resetRow(self):
		self._rowBuffer = self._columnDefaults[:]

	def reset(self):
		self._annotation.reset()
		self._rowBuffer = self._columnDefaults[:]
		self._rows = []
		self._rowIndex = -1

	def rows(self):
		return len(self._rows)

	def start(self):
		self._rowIndex = -1

	def skip(self, nRows):
		if nRows < 0:
			raise ValueError, 'Must be positive.'
		elif self._rowIndex + nRows >= len(self._rows):
			raise ValueError, 'Beyond the rows range.'
		else:
			return self._rowIndex + nRows

	def next(self):
		if self._rowIndex + 1 >= len(self._rows):
			return False
		else:
			self._rowIndex += 1
			return True

	def setRow(self, rowIndex):
		if rowIndex >= len(self._rows):
			raise ValueError, 'Beyond the rows range.'
		else:
			self._rowIndex = rowIndex

	def findColumn(self, columnName):
		return self._columnNames.index(columnName)

	def getDouble(self, columnIndex):
		if self._rowIndex == -1:
			return float(self._rowBuffer[columnIndex])
		else:
			return float(self._rows[self._rowIndex][columnIndex])

	def getFloat(self, columnIndex):
		if self._rowIndex == -1:
			return float(self._rowBuffer[columnIndex])
		else:
			return float(self._rows[self._rowIndex][columnIndex])

	def getInt(self, columnIndex):
		if self._rowIndex == -1:
			return int(self._rowBuffer[columnIndex])
		else:
			return int(self._rows[self._rowIndex][columnIndex])

	def getShort(self, columnIndex):
		if self._rowIndex == -1:
			return int(self._rowBuffer[columnIndex])
		else:
			return int(self._rows[self._rowIndex][columnIndex])

	def getLong(self, columnIndex):
		if self._rowIndex == -1:
			return long(self._rowBuffer[columnIndex])
		else:
			return long(self._rows[self._rowIndex][columnIndex])

	def getChar(self, columnIndex):
		if self._rowIndex == -1:
			return str(self._rowBuffer[columnIndex])
		else:
			return str(self._rows[self._rowIndex][columnIndex])

	def getByte(self, columnIndex):
		if self._rowIndex == -1:
			return int(self._rowBuffer[columnIndex])
		else:
			return int(self._rows[self._rowIndex][columnIndex])

	def getBoolean(self, columnIndex):
		if self._rowIndex == -1:
			return bool(self._rowBuffer[columnIndex])
		else:
			return bool(self._rows[self._rowIndex][columnIndex])

	def getString(self, columnIndex):
		if self._rowIndex == -1:
			return str(self._rowBuffer[columnIndex])
		else:
			return str(self._rows[self._rowIndex][columnIndex])

	def getObject(self, columnIndex):
		if self._rowIndex == -1:
			return self._rowBuffer[columnIndex]
		else:
			return self._rows[self._rowIndex][columnIndex]

	def getTuple(self, columnIndex):
		if self._rowIndex == -1:
			if self._rowBuffer[columnIndex] == None:
				tupleRowsData = []
				self._rowBuffer[columnIndex] = tupleRowsData
			else:
				tupleRowsData = self._rowBuffer[columnIndex]
		else:
			tupleRowsData = self._rows[self._rowIndex][columnIndex]

		tupleColumnsData = self._columnConverters[columnIndex]
		name = self._columnNames[columnIndex]
		newTuple = ITuple(name, name, tupleColumnsData[0], tupleColumnsData[1], tupleColumnsData[2], tupleColumnsData[3])
		newTuple._rows = tupleRowsData
		return newTuple

	def columns(self):
		return len(self._columnNames)

	def columnName(self, columnIndex):
		return self._columnNames[columnIndex]

	def columnNames(self):
		return self._columnNames[:]

	def columnType(self, columnIndex):
		columnConverter = self._columnConverters[columnIndex]
		if columnConverter == int:
			return PAIDA_Types.Integer
		elif columnConverter == long:
			return PAIDA_Types.Long
		elif columnConverter == float:
			return PAIDA_Types.Double
		elif columnConverter == str:
			return PAIDA_Types.String
		elif columnConverter == bool:
			return PAIDA_Types.Boolean
		elif columnConverter == _converterObject:
			return PAIDA_Types.Object
		else:
			### ITuple.
			return PAIDA_Types.ITuple

	def columnTypes(self):
		result = []
		for columnIndex in range(self.columns()):
			result.append(self.columnType(columnIndex))
		return result

	def columnMin(self, columnIndex):
		result = self._rows[0][columnIndex]
		for row in self._rows:
			result = min(result, row[columnIndex])
		return float(result)

	def columnMax(self, columnIndex):
		result = self._rows[0][columnIndex]
		for row in self._rows:
			result = max(result, row[columnIndex])
		return float(result)

	def columnMean(self, columnIndex):
		_sum = 0.0
		for row in self._rows:
			_sum += float(row[columnIndex])
		try:
			return _sum / len(self._rows)
		except ZeroDivisionError:
			return 0.0

	def columnRms(self, columnIndex):
		nRows = len(self._rows)
		_sum = 0.0
		_square = 0.0
		for row in self._rows:
			data = float(row[columnIndex])
			_sum += data
			_square += data**2
		try:
			result = (_square - _sum**2 / nRows) / nRows
			if paida.paida_core.IBaseHistogram.IBaseHistogram._meps2 < result < 0.0:
				return 0.0
			else:
				return math.sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def project(self, histogram, data1 = None, data2 = None, data3 = None, data4 = None, data5 = None):
		histogramName = histogram.__class__.__name__
		data1Name = data1.__class__.__name__
		data2Name = data2.__class__.__name__
		data3Name = data3.__class__.__name__
		data4Name = data4.__class__.__name__
		data5Name = data5.__class__.__name__
		histogramFill = histogram.fill
		currentRowIndex = self._rowIndex

		if histogramName in ['IHistogram1D', 'ICloud1D']:
			if (data1Name == 'IEvaluator') and (data2Name in ['NoneType', 'org.python.core.PyNone']) and (data3Name in ['NoneType', 'org.python.core.PyNone']) and (data4Name in ['NoneType', 'org.python.core.PyNone']) and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				filterObject = None
				weightObject = None
			elif (data1Name == 'IEvaluator') and (data2Name == 'IFilter') and (data3Name in ['NoneType', 'org.python.core.PyNone']) and (data4Name in ['NoneType', 'org.python.core.PyNone']) and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				filterObject = data2
				weightObject = None
			elif (data1Name == 'IEvaluator') and (data2Name == 'IEvaluator') and (data3Name in ['NoneType', 'org.python.core.PyNone']) and (data4Name in ['NoneType', 'org.python.core.PyNone']) and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				filterObject = None
				weightObject = data2
			elif (data1Name == 'IEvaluator') and (data2Name == 'IFilter') and (data3Name == 'IEvaluator') and (data4Name in ['NoneType', 'org.python.core.PyNone']) and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				filterObject = data2
				weightObject = data3
			else:
				raise IllegalArgumentException()

			evaluatorX.initialize(self)
			evaluatDoubleX = evaluatorX.evaluateDouble
			self.start()
			if (filterObject == None) and (weightObject == None):
				while self.next():
					histogramFill(evaluatDoubleX())
			elif (filterObject != None) and (weightObject == None):
				filterObject.initialize(self)
				filterAccept = filterObject.accept
				while self.next():
					if filterAccept():
						histogramFill(evaluatDoubleX())
			elif (filterObject == None) and (weightObject != None):
				weightObject.initialize(self)
				weightDouble = weightObject.evaluateDouble
				while self.next():
					histogramFill(evaluatDoubleX(), weightDouble())
			else:
				filterObject.initialize(self)
				filterAccept = filterObject.accept
				weightObject.initialize(self)
				weightDouble = weightObject.evaluateDouble
				while self.next():
					if filterAccept():
						histogramFill(evaluatDoubleX(), weightDouble())

		elif histogramName in ['IHistogram2D', 'ICloud2D', 'IProfile1D']:
			if (data1Name == 'IEvaluator') and (data2Name == 'IEvaluator') and (data3Name in ['NoneType', 'org.python.core.PyNone']) and (data4Name in ['NoneType', 'org.python.core.PyNone']) and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				evaluatorY = data2
				filterObject = None
				weightObject = None
			elif (data1Name == 'IEvaluator') and (data2Name == 'IEvaluator') and (data3Name == 'IFilter') and (data4Name in ['NoneType', 'org.python.core.PyNone']) and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				evaluatorY = data2
				filterObject = data3
				weightObject = None
			elif (data1Name == 'IEvaluator') and (data2Name == 'IEvaluator') and (data3Name == 'IEvaluator') and (data4Name in ['NoneType', 'org.python.core.PyNone']) and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				evaluatorY = data2
				filterObject = None
				weightObject = data3
			elif (data1Name == 'IEvaluator') and (data2Name == 'IEvaluator') and (data3Name == 'IFilter') and (data4Name == 'IEvaluator') and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				evaluatorY = data2
				filterObject = data3
				weightObject = data4
			else:
				raise IllegalArgumentException()

			evaluatorX.initialize(self)
			evaluatDoubleX = evaluatorX.evaluateDouble
			evaluatorY.initialize(self)
			evaluatDoubleY = evaluatorY.evaluateDouble
			self.start()
			if (filterObject == None) and (weightObject == None):
				while self.next():
					histogramFill(evaluatDoubleX(), evaluatDoubleY())
			elif (filterObject != None) and (weightObject == None):
				filterObject.initialize(self)
				filterAccept = filterObject.accept
				while self.next():
					if filterAccept():
						histogramFill(evaluatDoubleX(), evaluatDoubleY())
			elif (filterObject == None) and (weightObject != None):
				weightObject.initialize(self)
				weightDouble = weightObject.evaluateDouble
				while self.next():
					histogramFill(evaluatDoubleX(), evaluatDoubleY(), weightDouble())
			else:
				filterObject.initialize(self)
				filterAccept = filterObject.accept
				weightObject.initialize(self)
				weightDouble = weightObject.evaluateDouble
				while self.next():
					if filterAccept():
						histogramFill(evaluatDoubleX(), evaluatDoubleY(), weightDouble())

		elif histogramName in ['IHistogram3D', 'ICloud3D', 'IProfile2D']:
			if (data1Name == 'IEvaluator') and (data2Name == 'IEvaluator') and (data3Name == 'IEvaluator') and (data4Name in ['NoneType', 'org.python.core.PyNone']) and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				evaluatorY = data2
				evaluatorZ = data3
				filterObject = None
				weightObject = None
			elif (data1Name == 'IEvaluator') and (data2Name == 'IEvaluator') and (data3Name == 'IEvaluator') and (data4Name == 'IFilter') and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				evaluatorY = data2
				evaluatorZ = data3
				filterObject = data4
				weightObject = None
			elif (data1Name == 'IEvaluator') and (data2Name == 'IEvaluator') and (data3Name == 'IEvaluator') and (data4Name == 'IEvaluator') and (data5Name in ['NoneType', 'org.python.core.PyNone']):
				evaluatorX = data1
				evaluatorY = data2
				evaluatorZ = data3
				filterObject = None
				weightObject = data4
			elif (data1Name == 'IEvaluator') and (data2Name == 'IEvaluator') and (data3Name == 'IEvaluator') and (data4Name == 'IFilter') and (data5Name == 'IEvaluator'):
				evaluatorX = data1
				evaluatorY = data2
				evaluatorZ = data3
				filterObject = data4
				weightObject = data5
			else:
				raise IllegalArgumentException()

			evaluatorX.initialize(self)
			evaluatDoubleX = evaluatorX.evaluateDouble
			evaluatorY.initialize(self)
			evaluatDoubleY = evaluatorY.evaluateDouble
			evaluatorZ.initialize(self)
			evaluatDoubleZ = evaluatorZ.evaluateDouble
			self.start()
			if (filterObject == None) and (weightObject == None):
				while self.next():
					histogramFill(evaluatDoubleX(), evaluatDoubleY(), evaluatDoubleZ())
			elif (filterObject != None) and (weightObject == None):
				filterObject.initialize(self)
				filterAccept = filterObject.accept
				while self.next():
					if filterAccept():
						histogramFill(evaluatDoubleX(), evaluatDoubleY(), evaluatDoubleZ())
			elif (filterObject == None) and (weightObject != None):
				weightObject.initialize(self)
				weightDouble = weightObject.evaluateDouble
				while self.next():
					histogramFill(evaluatDoubleX(), evaluatDoubleY(), evaluatDoubleZ(), weightDouble())
			else:
				filterObject.initialize(self)
				filterAccept = filterObject.accept
				weightObject.initialize(self)
				weightDouble = weightObject.evaluateDouble
				while self.next():
					if filterAccept():
						histogramFill(evaluatDoubleX(), evaluatDoubleY(), evaluatDoubleZ(), weightDouble())

		else:
			raise IllegalArgumentException()

		self._rowIndex = currentRowIndex
