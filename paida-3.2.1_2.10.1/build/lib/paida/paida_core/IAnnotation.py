from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import *

import types

class IAnnotation:
	titleKey = 'Title'

	def __init__(self):
		self._data = []
		self._titleKey = []

	def addItem(self, key, value, sticky = False):
		if key in self._titleKey:
			raise IllegalArgumentException()
		else:
			self._titleKey.append(key)
			self._data.append([value, sticky])

	def _addItem(self, key, value, sticky):
		if key in self._titleKey:
			self._data[self._titleKey.index(key)] = [value, sticky]
		else:
			self._titleKey.append(key)
			self._data.append([value, sticky])

	def removeItem(self, key):
		self._removeItem(key, False)

	def _removeItem(self, key, inner = False):
		if key in self._titleKey:
			i = self._titleKey.index(key)
			if self._data[i][1] == True:
				if inner == False:
					raise IllegalArgumentException()
			else:
				self._titleKey.remove(key)
				self._data.remove(self._data[i])
		else:
			if inner == False:
				raise IllegalArgumentException()

	def value(self, data):
		if isinstance(data, types.StringType):
			key = data
			if key in self._titleKey:
				return self._data[self._titleKey.index(key)][0]
			else:
				raise IllegalArgumentException('"%s" is not in %s.' % (key, self._titleKey))
		elif isinstance(data, types.IntType):
			if 0 <= data < len(self._titleKey):
				return self._data[data][0]
			else:
				raise IllegalArgumentException('Beyond range.')
		else:
			raise IllegalArgumentException()

	def setValue(self, key, value):
		if key in self._titleKey:
			self._data[self._titleKey.index(key)][0] = value
		else:
			raise IllegalArgumentException()

	def setSticky(self, key, sticky):
		if key in self._titleKey:
			self._data[self._titleKey.index(key)][1] = bool(sticky)
		else:
			raise IllegalArgumentException()

	def _sticky(self, index):
		return self._data[index][1]

	def size(self):
		return len(self._titleKey)

	def key(self, index):
		return self._titleKey[index]

	def reset(self):
		for key in self._titleKey:
			try:
				self._removeItem(key, True)
			except IllegalArgumentException:
				pass
