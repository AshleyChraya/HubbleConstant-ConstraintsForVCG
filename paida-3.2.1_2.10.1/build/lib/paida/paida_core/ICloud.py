from paida.paida_core.PAbsorber import *
from paida.paida_core.IBaseHistogram import *
from paida.paida_core.PExceptions import *

import copy

class ICloud(IBaseHistogram):

	def __init__(self, title, nMax = -1):
		IBaseHistogram.__init__(self, title)
		self._nMax = nMax
		self._entryList = [[], []]
		self._histogram = None
		self._isConverted = False

		self._lowerEdges = [0.0, 0.0, 0.0]
		self._upperEdges = [0.0, 0.0, 0.0]
		self._sumOfWeights = 0.0
		self._sumOfTorques = [0.0, 0.0, 0.0]
		self._sumOfInertials = [0.0, 0.0, 0.0]

	def reset(self):
		IBaseHistogram.reset(self)
		self._entryList = [[], []]
		self._histogram = None
		self._isConverted = False

		self._lowerEdges = [0.0, 0.0, 0.0]
		self._upperEdges = [0.0, 0.0, 0.0]
		self._sumOfWeights = 0.0
		self._sumOfTorques = [0.0, 0.0, 0.0]
		self._sumOfInertials = [0.0, 0.0, 0.0]

	def _copyContents(self, icloud):
		icloud._entryList = copy.deepcopy(self._entryList)
		icloud._lowerEdges = self._lowerEdges[:]
		icloud._upperEdges = self._upperEdges[:]
		icloud._sumOfWeights = self._sumOfWeights
		icloud._sumOfTorques = self._sumOfTorques[:]
		icloud._sumOfInertials = self._sumOfInertials[:]
		if self.isConverted():
			icloud.convertToHistogram()
		return icloud

	def entries(self):
		return len(self._entryList[0])

	def maxEntries(self):
		return self._nMax

	def sumOfWeights(self):
		return self._sumOfWeights

	def convertToHistogram(self):
		if self.isConverted():
			raise AlreadyConvertedException()
		else:
			pass

	def isConverted(self):
		return self._isConverted

	def scale(self, scaleFactor):
		floatScaleFactor = float(scaleFactor)
		if floatScaleFactor <= 0.0:
			raise IllegalArgumentException()
		else:
			weights = self._entryList[1]
			for i in range(self.entries()):
				weights[i] *= floatScaleFactor
		self._sumOfWeights *= floatScaleFactor
		sumOfTorques = self._sumOfTorques
		sumOfInertials = self._sumOfInertials
		for i in range(3):
			sumOfTorques[i] *= floatScaleFactor
			sumOfInertials[i] *= floatScaleFactor

	def _convertedName(self):
		return 'converted_%s' % self._getName()
