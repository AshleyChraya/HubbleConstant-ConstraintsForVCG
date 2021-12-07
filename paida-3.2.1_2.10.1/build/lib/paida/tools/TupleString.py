"""This module will make it easy to create a complex ITuple.

If you want to generate a string like
"int data0 = 0, ITuple testTuple = {float data1 = 1.0, float data2 = 2.0, float data3}, int data4 = 5"
the following code will do it.

from paida.tools import TupleString
from paida import PTypes

tuple0 = TupleString.create()
tuple0.addColumn(PTypes.Integer, 'data0', 0)
tuple1 = tuple0.addColumn(PTypes.ITuple, 'testTuple')
tuple1.addColumn(PTypes.Float, 'data1', 1.0)
tuple1.addColumn(PTypes.Float, 'data2', 2.0)
tuple1.addColumn(PTypes.String, 'data3', 'testString')
tuple0.addColumn(PTypes.Integer, 'data4', 5)

columnString = tuple0.getString()
print columnString

from paida import IAnalysisFactory
analysisFactory = IAnalysisFactory.create()
treeFactory = analysisFactory.createTreeFactory()
tree = treeFactory.create()
tupleFactory = analysisFactory.createTupleFactory(tree)
complexTuple = tupleFactory.create('complex tuple', 'Complex Tuple', columnString)
"""

from paida.paida_core import PTypes
import xml.sax.saxutils

class TupleItem:
	def __init__(self):
		self.columns = []

	def addColumn(self, columnType, columnName, defaultValue = None):
		if columnType == PTypes.ITuple:
			tupleItem = TupleItem()
			self.columns.append((columnType, columnName, tupleItem))
			return tupleItem
		else:
			self.columns.append((columnType, columnName, defaultValue))
			return None

	def getString(self):
		return xml.sax.saxutils.escape(self._getString(self, ''), {'"': '&quot;'})

	def _getString(self, tupleItem, tupleString):
		for (columnType, columnName, defaultValue) in tupleItem.columns:
			if columnType == PTypes.ITuple:
				tupleString += ', %s %s = {%s}' % (columnType.TYPE, columnName, self._getString(defaultValue, ''))
			else:
				if defaultValue == None:
					tupleString += ', %s %s' % (columnType.TYPE, columnName)
				else:
					if (columnType == PTypes.String) or (columnType == PTypes.Character):
						tupleString += ', %s %s = "%s"' % (columnType.TYPE, columnName, defaultValue)
					else:
						tupleString += ', %s %s = %s' % (columnType.TYPE, columnName, defaultValue)
		if tupleString.startswith(', '):
			return tupleString[2:]
		else:
			return tupleString

def createTuple():
	print 'Warning:'
	print 'createTuple() will be removed'
	print 'use create() alternatively'
	return create()

def create():
	return TupleItem()
