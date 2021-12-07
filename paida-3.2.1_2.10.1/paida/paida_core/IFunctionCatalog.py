from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import *

import types
import cPickle

class IFunctionCatalog:
	def __init__(self):
		self._catalog = []

	def add(self, nameId, data):
		try:
			if type(data) == types.StringType:
				codeletString = data
			elif data.__class__.__name__ == 'IFunction':
				function = data
				codeletString = function.codeletString()
			else:
				raise IllegalArgumentException()
		except:
			return False

		nameList = self.list()
		if nameId in nameList:
			self._catalog[nameList.index(nameId)] = [nameId, codeletString]
		else:
			self._catalog.append([nameId, codeletString])
		return True

	def _getCodeletString(self, nameId):
		return self._catalog[self.list().index(nameId)][1]

	def list(self):
		result = []
		for item in self._catalog:
			result.append(item[0])
		return result

	def remove(self, nameId):
		nameList = self.list()
		if nameId in nameList:
			self._catalog.remove(self._catalog[nameList.index(nameId)])
		else:
			raise IllegalArgumentException('The nameId "%s" does not exist.' % nameId)

	def storeAll(self, nameOnDisk):
		file = open(nameOnDisk, 'w')
		cPickle.dump(self._catalog, file)
		file.close()

	def loadAll(self, nameOnDisk):
		file = open(nameOnDisk, 'r')
		self._catalog = cPickle.load(file)
		file.close()
