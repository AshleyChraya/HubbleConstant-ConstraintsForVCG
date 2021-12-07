from paida.paida_core.PAbsorber import *
from paida.paida_core.IHistogram import *
from paida.paida_core.IAxis import *
from paida.paida_core.PExceptions import *

from math import sqrt

class IHistogram1D(IHistogram):
	def __init__(self, name, title, binEdges, fixedBinning, option = {}):
		IHistogram.__init__(self, title, binEdges)
		self._setName(name)
		self._setOption(option)
		self._axis.append(IAxis(binEdges[0], fixedBinning))

	def _localReset(self):
		sizeX = self._sizeX
		sizeY = self._sizeY
		sizeZ = self._sizeZ
		self._binSumOfTorquesX = binArray3(sizeX, sizeY, sizeZ)
		self._binSumOfTorquesY = binArray3(0, 0, 0)
		self._binSumOfTorquesZ = binArray3(0, 0, 0)
		self._binSumOfInertialsX = binArray3(sizeX, sizeY, sizeZ)
		self._binSumOfInertialsY = binArray3(0, 0, 0)
		self._binSumOfInertialsZ = binArray3(0, 0, 0)

	def fill(self, x, weight = 1.0):
		i = self._innerIndex(2 + self._axis[0].coordToIndex(x), 0, 0)
		self._binEntries.data[i] += 1
		self._binSumOfWeights.data[i] += weight
		self._binSumOfErrors.data[i] += weight**2
		self._binSumOfTorquesX.data[i] += x * weight
		self._binSumOfInertialsX.data[i] += x**2 * weight

	def _getStatisticSet(self):
		weights = self._sumWeights()
		torquesX = self._sumTorquesX()

		entries = self.entries()

		try:
			meanX = torquesX / weights
		except ZeroDivisionError:
			meanX = 0.0

		try:
			result = (self._sumInertialsX() - torquesX**2 / weights) / weights
			if self._meps2 < result < 0.0:
				rmsX = 0.0
			else:
				rmsX = sqrt(result)
		except ZeroDivisionError:
			rmsX = 0.0

		return [entries, meanX, rmsX]

	def _getDataSet(self, i):
		weights = self._binSumOfWeights.data[i]

		result = self._binSumOfErrors.data[i]
		if self._meps2 < result < 0.0:
			error = 0.0
		else:
			error = sqrt(result)

		try:
			binMeanX = self._binSumOfTorquesX.data[i] / weights
		except ZeroDivisionError:
			binMeanX = 0.0

		try:
			result = (self._binSumOfInertialsX.data[i] - self._binSumOfTorquesX.data[i]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				binRmsX = 0.0
			else:
				binRmsX = sqrt(result)
		except ZeroDivisionError:
			binRmsX = 0.0

		return [weights, error, binMeanX, binRmsX]

	def binMean(self, indexX):
		indexX += 2
		try:
			return self._binSumOfTorquesX[indexX, 0, 0] / self._binSumOfWeights[indexX, 0, 0]
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def _binRms(self, indexX):
		indexX += 2
		weights = self._binSumOfWeights[indexX, 0, 0]
		try:
			result = (self._binSumOfInertialsX[indexX, 0, 0] - self._binSumOfTorquesX[indexX, 0, 0]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def binEntries(self, indexX):
		try:
			return int(self._binEntries[2 + indexX, 0, 0])
		except:
			raise IllegalArgumentException()

	def binHeight(self, indexX):
		try:
			return self._binSumOfWeights[2 + indexX, 0, 0]
		except:
			raise IllegalArgumentException()

	def binError(self, indexX):
		result = self._binSumOfErrors[2 + indexX, 0, 0]
		if self._meps2 < result < 0.0:
			return 0.0
		else:
			return sqrt(result)

	def _binError2(self, indexX):
		return self._binSumOfErrors[2 + indexX, 0, 0]

	def mean(self):
		try:
			return self._sumTorquesX() / self._sumWeights()
		except ZeroDivisionError:
			return 0.0

	def rms(self):
		weights = self._sumWeights()
		try:
			result = (self._sumInertialsX() - self._sumTorquesX()**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def axis(self):
		return self._axis[0]

	def axisX(self):
		return self.axis()

	def coordToIndex(self, coord):
		return self._axis[0].coordToIndex(coord)

	def add(self, hist):
		if isinstance(hist, IHistogram1D):
			if self._axis[0]._edgeList != hist._axis[0]._edgeList:
				raise IllegalArgumentException()
			self._add(hist)
		else:
			raise IllegalArgumentException()
