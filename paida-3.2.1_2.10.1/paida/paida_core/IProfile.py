from paida.paida_core.PAbsorber import *
from paida.paida_core.IBaseHistogram import *
from paida.math.array.binArray import binArray2

class IProfile(IBaseHistogram):

	def __init__(self, title, binEdges):
		IBaseHistogram.__init__(self, title)
		self._sizeX = len(binEdges[0]) + 1
		self._sizeY = len(binEdges[1]) + 1
		self._reset()

	def reset(self):
		IBaseHistogram.reset(self)
		self._reset()

	def _reset(self):
		sizeX = self._sizeX
		sizeY = self._sizeY
		self._binEntries = binArray2(sizeX, sizeY)
		self._binSumOfWeights = binArray2(sizeX, sizeY)
		self._binSumOfInertialsX = binArray2(sizeX, sizeY)
		self._binSumOfInertialsY = binArray2(sizeX, sizeY)
		self._binSumOfInertialsZ = binArray2(sizeX, sizeY)
		self._binSumOfTorquesX = binArray2(sizeX, sizeY)
		self._binSumOfTorquesY = binArray2(sizeX, sizeY)
		self._binSumOfTorquesZ = binArray2(sizeX, sizeY)

	def _innerIndex(self, innerX, innerY):
		return self._binEntries.getIndex(innerX, innerY)

	def _setLowerValue(self, value):
		self._lowerValue = value

	def _getLowerValue(self):
		return self._lowerValue

	def _setUpperValue(self, value):
		self._upperValue = value

	def _getUpperValue(self):
		return self._upperValue

	def allEntries(self):
		return self._binEntries.sum()

	def entries(self):
		return self._binEntries.sumInRange()

	def extraEntries(self):
		return self._binEntries.sumOutRange()

	def _sumWeights(self):
		return self._binSumOfWeights.sum()

	def _sumInertialsX(self):
		return self._binSumOfInertialsX.sum()

	def _sumInertialsY(self):
		return self._binSumOfInertialsY.sum()

	def _sumInertialsZ(self):
		return self._binSumOfInertialsZ.sum()

	def _sumInertials(self):
		return [self._sumInertialsX(), self._sumInertialsY(), self._sumInertialsZ()]

	def _sumTorquesX(self):
		return self._binSumOfTorquesX.sum()

	def _sumTorquesY(self):
		return self._binSumOfTorquesY.sum()

	def _sumTorquesZ(self):
		return self._binSumOfTorquesZ.sum()

	def _sumTorques(self):
		return [self._sumTorquesX(), self._sumTorquesY(), self._sumTorquesZ()]

	def _add(self, hist):
		self._binEntries.add(hist._binEntries)
		self._binSumOfWeights.add(hist._binSumOfWeights)
		self._binSumOfInertialsX.add(hist._binSumOfInertialsX)
		self._binSumOfInertialsY.add(hist._binSumOfInertialsY)
		self._binSumOfInertialsZ.add(hist._binSumOfInertialsZ)
		self._binSumOfTorquesX.add(hist._binSumOfTorquesX)
		self._binSumOfTorquesY.add(hist._binSumOfTorquesY)
		self._binSumOfTorquesZ.add(hist._binSumOfTorquesZ)
