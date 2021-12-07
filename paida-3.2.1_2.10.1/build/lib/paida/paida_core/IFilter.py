from paida.paida_core.PAbsorber import *
import paida.paida_core.PUtilities

class IFilter:
	def __init__(self, expression, rowsToProcess = None, startingRow = None):
		self._expression = expression
		self._rowsToProcess = rowsToProcess
		self._startingRow = startingRow

	def _convertExpression(self, expression, tupleObject):
		replaces = {}
		columnNames = tupleObject.columnNames()
		for columnIndex, columnName in enumerate(columnNames):
			replaces[columnName] = '_row[%d]' % columnIndex
		return paida.paida_core.PUtilities.cExpressionConverter(expression, replaces)

	def initialize(self, tupleObject):
		self._tupleObject = tupleObject
		self._tupleRows = tupleObject._rows
		self._code = compile(self._convertExpression(self._expression, tupleObject), 'IFilter.py', 'eval')
		self._globals = globals()
		if self._startingRow != None:
			tupleObject.setRow(self._startingRow)
		self._count = 0

	def accept(self):
		if self._rowsToProcess == None:
			return bool(eval(self._code, self._globals, {'_row': self._tupleRows[self._tupleObject._rowIndex]}))
		else:
			if self._count >= self._rowsToProcess:
				raise IndexError, "Reached to the specified rowsToProcess."
			else:
				self._count += 1
				return bool(eval(self._code, self._globals, {'_row': self._tupleRows[self._tupleObject._rowIndex]}))

	def expression(self):
		return self._expression
