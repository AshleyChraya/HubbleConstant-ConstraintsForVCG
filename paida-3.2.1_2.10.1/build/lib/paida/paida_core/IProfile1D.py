from paida.paida_core.PAbsorber import *
from paida.paida_core.IProfile import *
from paida.paida_core.IAxis import *
from paida.paida_core.PExceptions import *

from math import sqrt

class IProfile1D(IProfile):

	def __init__(self, name, title, binEdges, fixedBinning, lowerValue, upperValue, option = {}):
		IProfile.__init__(self, title, binEdges)
		self._setName(name)
		self._setOption(option)
		self._axis.append(IAxis(binEdges[0], fixedBinning))
		self._setLowerValue(lowerValue)
		self._setUpperValue(upperValue)

	def fill(self, x, y, weight = 1.0):
		i = self._innerIndex(2 + self._axis[0].coordToIndex(x), 0)
		self._binEntries.data[i] += 1
		self._binSumOfWeights.data[i] += weight
		self._binSumOfTorquesX.data[i] += x * weight
		self._binSumOfTorquesY.data[i] += y * weight
		self._binSumOfInertialsX.data[i] += x**2 * weight
		self._binSumOfInertialsY.data[i] += y**2 * weight

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

		try:
			binError = sqrt(abs(self._binSumOfTorquesY.data[i]) / weights**2)
		except ZeroDivisionError:
			binError = 0.0

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

		try:
			result = (self._binSumOfInertialsY.data[i] - self._binSumOfTorquesY.data[i]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				binRmsY = 0.0
			else:
				binRmsY = sqrt(result)
		except ZeroDivisionError:
			binRmsY = 0.0

		return [weights, binError, binMeanX, binRmsX, binRmsZ]

	def binMean(self, indexX):
		indexX += 2
		try:
			return self._binSumOfTorquesX[indexX, 0] / self._binSumOfWeights[indexX, 0]
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def binEntries(self, indexX):
		try:
			return self._binEntries[2 + indexX, 0]
		except:
			raise IllegalArgumentException()

	def binHeight(self, indexX):
		indexX += 2
		try:
			return self._binSumOfTorquesY[indexX, 0] / self._binSumOfWeights[indexX, 0]
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def binError(self, indexX):
		indexX += 2
		try:
			return sqrt(abs(self._binSumOfTorquesY[indexX, 0]) / self._binSumOfWeights[indexX, 0]**2)
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def _binError2(self, indexX):
		indexX += 2
		try:
			return abs(self._binSumOfTorquesY[indexX, 0]) / self._binSumOfWeights[indexX, 0]**2
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def binRms(self, indexX):
		indexX += 2
		weights = self._binSumOfWeights[indexX, 0]
		try:
			result = (self._binSumOfInertialsY[indexX, 0] - self._binSumOfTorquesY[indexX, 0]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def _binRms(self, indexX):
		indexX += 2
		weights = self._binSumOfWeights[indexX, 0]
		try:
			result = (self._binSumOfInertialsX[indexX, 0] - self._binSumOfTorquesX[indexX, 0]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

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

	def coordToIndex(self, coord):
		return self._axis[0].coordToIndex(coord)

	def add(self, profile):
		if not isinstance(profile, IProfile1D):
			raise IllegalArgumentException()
		if self._axis[0]._edgeList != profile._axis[0]._edgeList:
			raise IllegalArgumentException()
		self._add(profile)

	def sumBinHeights(self):
		result = 0.0
		binHeight = self.binHeight
		for x in range(self._sizeX - 2):
			result += binHeight(x)
		return result

	def sumExtraBinHeights(self):
		result = 0.0
		binHeight = self.binHeight
		for x in [-2, -1]:
			result += binHeight(x)
		return result

	def sumAllBinHeights(self):
		result = 0.0
		binHeight = self.binHeight
		for x in range(-2, self._sizeX - 2):
			result += binHeight(x)
		return result

	def minBinHeight(self):
		binHeight = self.binHeight
		result = binHeight(0)
		for x in range(self._sizeX - 2):
			result = min(result, binHeight(x))
		return result

	def maxBinHeight(self):
		binHeight = self.binHeight
		result = binHeight(0)
		for x in range(self._sizeX - 2):
			result = max(result, binHeight(x))
		return result
