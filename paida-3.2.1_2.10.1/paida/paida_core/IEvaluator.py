from paida.paida_core.PAbsorber import *
import paida.paida_core.PUtilities
from math import *

class IEvaluator:
	def __init__(self, expression):
		self._expression = expression

	def _convertExpression(self, expression, tupleObject):
		replaces = {}
		columnNames = tupleObject.columnNames()
		for columnIndex, columnName in enumerate(columnNames):
			replaces[columnName] = '_row[%d]' % columnIndex
		return paida.paida_core.PUtilities.cExpressionConverter(expression, replaces)

	def initialize(self, tupleObject):
		self._tupleObject = tupleObject
		self._tupleRows = tupleObject._rows
		self._code = compile(self._convertExpression(self._expression, tupleObject), 'IEvaluator.py', 'eval')
		self._globals = globals()

	def evaluateDouble(self):
		return float(eval(self._code, self._globals, {'_row': self._tupleRows[self._tupleObject._rowIndex]}))

	def expression(self):
		return self._expression
