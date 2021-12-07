from paida.paida_core.PAbsorber import *
from paida.paida_core.ITuple import *
import paida.paida_core.ITuple
from paida.paida_core.IFilter import *
from paida.paida_core.IEvaluator import *
from paida.paida_core.PExceptions import *
from paida.paida_core.PUtilities import optionAnalyzer, _Shlex
from paida.paida_core import PTypes

import xml.sax.saxutils
import types
import copy

class ITupleFactory(object):
	def __init__(self, tree):
		self._tree = tree

	def create(self, name, title, data1, data2 = None, data3 = None):
		tupleObject = self._create(name, title, data1, data2, data3)
		self._tree._mkObject(name, tupleObject)
		return tupleObject

	def _create(self, name, title, data1, data2 = None, data3 = None):
		if hasattr(data1, '__iter__') and hasattr(data2, '__iter__') and (data3 == None):
			columnNames = data1
			columnTypes = data2
			columnString = self._createColumnString(columnTypes, columnNames)
			optionString = ''
		elif hasattr(data1, '__iter__') and hasattr(data2, '__iter__') and (type(data3) in types.StringTypes):
			columnNames = data1
			columnTypes = data2
			columnString = self._createColumnString(columnTypes, columnNames)
			optionString = data3
		elif (type(data1) in types.StringTypes) and (data2 == None) and (data3 == None):
			columnString = data1
			optionString = ''
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and (data3 == None):
			columnString = data1
			optionString = data2

		[dummy, analyzedOption, columnNames, columnDefaults, columnConverters] = self._parseColumnString(columnString, optionString)
		ituple = ITuple(name, title, analyzedOption, columnNames, columnDefaults, columnConverters)
		return ituple

	def _createColumnString(self, columnTypes, columnNames):
		columnString = ''
		for i, columnType in enumerate(columnTypes):
			columnString += '%s %s, ' % (columnType.TYPE, columnNames[i])
		return columnString[:-2]

	def _parseColumnString(self, columnString, optionString):
		### Jython2.1 does not understand xml.sax.saxutils.unescape()
		#columnString = xml.sax.saxutils.unescape(columnString, {'&quot;': '"'})
		columnString = columnString.replace('&amp;', '&')
		columnString = columnString.replace('&lt;', '<')
		columnString = columnString.replace('&gt;', '>')
		columnString = columnString.replace('&quot;', '"')

		parser = _Shlex(columnString, omitQuotes = True, omitSpaces = True)
		result, token = self._parseFromTuple(parser, '')
		result[1] = optionAnalyzer(optionString)
		return result

	def _parseFromTuple(self, parser, token):
		if token == '(':
			### Option strings.
			optionString = ''
			while 1:
				token = parser.get_token()
				if token == ')':
					token = parser.get_token()
					break
				else:
					optionString += token
		else:
			optionString = None
		analyzedOption = optionAnalyzer(optionString)

		tupleName = token
		token = parser.get_token()
		if token == '=':
			### Pop '{'.
			token = parser.get_token()
			token = parser.get_token()

		columnNames = []
		columnDefaults = []
		columnConverters = []
		breakFlag = False
		while 1:
			### Nested tuple?
			if token in ['ITuple']:
				[itupleName, ianalyzedOption, icolumnNames, icolumnDefaults, icolumnConverters], token = self._parseFromTuple(parser, parser.get_token())
				columnNames.append(itupleName)
				columnDefaults.append(None)
				columnConverters.append([ianalyzedOption, icolumnNames, icolumnDefaults, icolumnConverters])
				continue
			elif token == '}':
				token = parser.get_token()
				if token in [',', ';']:
					token = parser.get_token()
				break
			else:
				### Type check.
				if token in ['int', 'short', 'byte']:
					converter = int
					columnName = parser.get_token()
				elif token in ['long']:
					converter = long
					columnName = parser.get_token()
				elif token in ['float', 'double']:
					converter = float
					columnName = parser.get_token()
				elif token in ['char', 'string']:
					converter = str
					columnName = parser.get_token()
				elif token in ['boolean']:
					converter = bool
					columnName = parser.get_token()
				elif token in ['Object']:
					converter = paida.paida_core.ITuple._converterObject
					columnName = parser.get_token()
				elif token == parser.eof:
					break
				else:
					converter = currentConverter
					columnName = token
				currentConverter = converter

				### Default exists?
				token = parser.get_token()
				if token == '=':
					tempDefault = parser.get_token()
					if tempDefault in [',', ';']:
						columnDefault = None
						token = parser.get_token()
					elif tempDefault == '}':
						columnDefault = None
						token = parser.get_token()
						if token in [',', ';']:
							token = parser.get_token()
						breakFlag = True
					elif tempDefault == parser.eof:
						columnDefault = None
						breakFlag = True
					else:
						if tempDefault in ['+', '-']:
							tempDefault += parser.get_token()
						columnDefault = converter(tempDefault)
						token = parser.get_token()
						if token in [',', ';']:
							token = parser.get_token()
						elif token == '}':
							token = parser.get_token()
							if token in [',', ';']:
								token = parser.get_token()
							breakFlag = True
						elif token == parser.eof:
							breakFlag = True
						else:
							RuntimeError, 'Unknown character "%s"' % token
				elif token in [',', ';']:
					columnDefault = None
					token = parser.get_token()
				elif token == '}':
					columnDefault = None
					token = parser.get_token()
					if token in [',', ';']:
						token = parser.get_token()
					breakFlag = True
				elif token == parser.eof:
					columnDefault = None
					breakFlag = True
				else:
					raise RuntimeError, 'Unknown character "%s"' % token

				columnNames.append(columnName)
				columnDefaults.append(columnDefault)
				columnConverters.append(converter)
				if breakFlag:
					break

		return [tupleName, analyzedOption, columnNames, columnDefaults, columnConverters], token

	def createChained(self, name, title, dataList):
		if dataList == []:
			raise IllegalArgumentException()
		elif isinstance(dataList[0], types.StringTypes):
			tupleObjects = []
			for item in dataList:
				tupleObjects.append(self._tree.find(item))
		elif isinstance(dataList[0], ITuple):
			tupleObjects = dataList
		else:
			raise IllegalArgumentException()

		firstTuple = tupleObjects[0]
		analyzedOption = firstTuple._analyzedOption
		columnNames = firstTuple._columnNames
		columnDefaults = firstTuple._columnDefaults
		columnConverters = firstTuple._columnConverters
		chainedTuple = ITuple(name, title, analyzedOption, columnNames, columnDefaults, columnConverters)
		for tupleObject in tupleObjects:
			chainedTuple._rows.extend(tupleObject._rows)

		self._tree._mkObject(name, chainedTuple)
		return chainedTuple

	def createFiltered(self, name, tupleObject, filterObject, columnNames = None):
		if columnNames == None:
			columnIndices = range(tupleObject.columns())
		else:
			columnIndices = []
			for columnName in columnNames:
				columnIndices.append(tupleObject.findColumn(columnName))
		analyzedOption = tupleObject._analyzedOption
		_columnNames = []
		_columnDefaults = []
		_columnConverters = []
		for columnIndex in columnIndices:
			_columnNames.append(tupleObject._columnNames[columnIndex])
			_columnDefaults.append(tupleObject._columnDefaults[columnIndex])
			_columnConverters.append(tupleObject._columnConverters[columnIndex])
		newTuple = ITuple(name, name, analyzedOption, _columnNames, _columnDefaults, _columnConverters)

		dcopy = copy.deepcopy
		tupleObjectRows = tupleObject._rows
		newTupleObjectRows = newTuple._rows
		_globals = globals()
		filterObject.initialize(tupleObject)
		_code = filterObject._code

		if (filterObject._startingRow == None) and (filterObject._rowsToProcess == None):
			if columnNames:
				for _row in tupleObjectRows:
					if eval(_code, _globals, {'_row': _row}):
						newRowData = []
						for columnIndex in columnIndices:
							newRowData.append(_row[columnIndex])
						newTupleObjectRows.append(dcopy(newRowData))
			else:
				for _row in tupleObjectRows:
					if eval(_code, _globals, {'_row': _row}):
						newTupleObjectRows.append(dcopy(_row))
		else:
			if filterObject._startingRow == None:
				startingRow = 0
			else:
				startingRow = filterObject._startingRow
			if filterObject._rowsToProcess == None:
				endingRow = len(tupleObject._rows)
			else:
				endingRow = startingRow + filterObject._rowsToProcess
			if columnNames:
				for rowIndex in range(startingRow, endingRow):
					_row = tupleObjectRows[rowIndex]
					if eval(_code, _globals, {'_row': _row}):
						newRowData = []
						for columnIndex in columnIndices:
							newRowData.append(_row[columnIndex])
						newTupleObjectRows.append(dcopy(newRowData))
			else:
				for rowIndex in range(startingRow, endingRow):
					_row = tupleObjectRows[rowIndex]
					if eval(_code, _globals, {'_row': _row}):
						newTupleObjectRows.append(dcopy(_row))
		return newTuple

	def createFilter(self, expression, rowsToProcess = None, startingRow = None):
		if (rowsToProcess == None) and (startingRow == None):
			return IFilter(expression)
		elif isinstance(rowsToProcess, types.IntType) and (startingRow == None):
			return IFilter(expression, rowsToProcess)
		elif isinstance(rowsToProcess, types.IntType) and isinstance(startingRow, types.IntType):
			return IFilter(expression, rowsToProcess, startingRow)
		else:
			raise IllegalArgumentException()

	def createEvaluator(self, expression):
		return IEvaluator(expression)
