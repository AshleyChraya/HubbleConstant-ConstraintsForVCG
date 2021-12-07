from paida.paida_core.PAbsorber import *
from paida.paida_core.IBaseHistogram import *
from paida.paida_core.PExceptions import *
from paida.math.array.binArray import binArray3

class IHistogram(IBaseHistogram):
	def __init__(self, title, binEdges):
		IBaseHistogram.__init__(self, title)
		self._sizeX = len(binEdges[0]) + 1
		self._sizeY = len(binEdges[1]) + 1
		self._sizeZ = len(binEdges[2]) + 1
		self._reset()

	def reset(self):
		IBaseHistogram.reset(self)
		self._reset()

	def _reset(self):
		sizeX = self._sizeX
		sizeY = self._sizeY
		sizeZ = self._sizeZ
		self._binEntries = binArray3(sizeX, sizeY, sizeZ)
		self._binSumOfWeights = binArray3(sizeX, sizeY, sizeZ)
		self._binSumOfErrors = binArray3(sizeX, sizeY, sizeZ)
		self._localReset()

	def _innerIndex(self, innerX, innerY, innerZ):
		return self._binEntries.getIndex(innerX, innerY, innerZ)

	def allEntries(self):
		return int(self._binEntries.sum())

	def entries(self):
		return int(self._binEntries.sumInRange())

	def extraEntries(self):
		return int(self._binEntries.sumOutRange())

	def _sumWeights(self):
		return self._binSumOfWeights.sum()

	def _sumErrors(self):
		return self._binSumOfErrors.sum()

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

	def equivalentBinEntries(self):
		try:
			return self._sumWeights()**2 / self._sumErrors()
		except ZeroDivisionError:
			return 0.0

	def sumAllBinHeights(self):
		return self._binSumOfWeights.sum()

	def sumBinHeights(self):
		return self._binSumOfWeights.sumInRange()

	def sumExtraBinHeights(self):
		return self._binSumOfWeights.sumOutRange()

	def minBinHeight(self):
		if self._sizeY == 1:
			rangeY = [0]
		else:
			rangeY = range(2, self._sizeY)
		if self._sizeZ == 1:
			rangeZ = [0]
		else:
			rangeZ = range(2, self._sizeZ)

		binSumOfWeights = self._binSumOfWeights
		result = binSumOfWeights[2, rangeY[0], rangeZ[0]]
		for x in range(2, self._sizeX):
			for y in rangeY:
				for z in rangeZ:
					result = min(result, binSumOfWeights[x, y, z])
		return result

	def maxBinHeight(self):
		if self._sizeY == 1:
			rangeY = [0]
		else:
			rangeY = range(2, self._sizeY)
		if self._sizeZ == 1:
			rangeZ = [0]
		else:
			rangeZ = range(2, self._sizeZ)

		binSumOfWeights = self._binSumOfWeights
		result = binSumOfWeights[2, rangeY[0], rangeZ[0]]
		for x in range(2, self._sizeX):
			for y in rangeY:
				for z in rangeZ:
					result = max(result, binSumOfWeights[x, y, z])
		return result

	def scale(self, factor):
		if factor < 0:
			raise IllegalArgumentException()
		else:
			factor = float(factor)

		self._binSumOfWeights.scale(factor)
		self._binSumOfErrors.scale(factor**2)
		self._binSumOfTorquesX.scale(factor)
		self._binSumOfTorquesY.scale(factor)
		self._binSumOfTorquesZ.scale(factor)
		self._binSumOfInertialsX.scale(factor)
		self._binSumOfInertialsY.scale(factor)
		self._binSumOfInertialsZ.scale(factor)

	def _add(self, hist):
		self._binEntries.add(hist._binEntries)
		self._binSumOfWeights.add(hist._binSumOfWeights)
		self._binSumOfErrors.add(hist._binSumOfErrors)
		self._binSumOfTorquesX.add(hist._binSumOfTorquesX)
		self._binSumOfTorquesY.add(hist._binSumOfTorquesY)
		self._binSumOfTorquesZ.add(hist._binSumOfTorquesZ)
		self._binSumOfInertialsX.add(hist._binSumOfInertialsX)
		self._binSumOfInertialsY.add(hist._binSumOfInertialsY)
		self._binSumOfInertialsZ.add(hist._binSumOfInertialsZ)
