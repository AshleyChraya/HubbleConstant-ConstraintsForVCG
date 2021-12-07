from paida.paida_core.PAbsorber import *
from paida.paida_core.IProfile import *
from paida.paida_core.IAxis import *
from paida.paida_core.PExceptions import *

from math import sqrt

class IProfile2D(IProfile):

	def __init__(self, name, title, binEdges, fixedBinning, lowerValue, upperValue, option = {}):
		IProfile.__init__(self, title, binEdges)
		self._setName(name)
		self._setOption(option)
		self._axis.append(IAxis(binEdges[0], fixedBinning))
		self._axis.append(IAxis(binEdges[1], fixedBinning))
		self._setLowerValue(lowerValue)
		self._setUpperValue(upperValue)

	def fill(self, x, y, z, weight = 1.0):
		i = self._innerIndex(2 + self._axis[0].coordToIndex(x), 2 + self._axis[1].coordToIndex(y))
		self._binEntries.data[i] += 1
		self._binSumOfWeights.data[i] += weight
		self._binSumOfTorquesX.data[i] += x * weight
		self._binSumOfTorquesY.data[i] += y * weight
		self._binSumOfTorquesZ.data[i] += z * weight
		self._binSumOfInertialsX.data[i] += x**2 * weight
		self._binSumOfInertialsY.data[i] += y**2 * weight
		self._binSumOfInertialsZ.data[i] += z**2 * weight

	def _getStatisticSet(self):
		weights = self._sumWeights()
		torquesX = self._sumTorquesX()
		torquesY = self._sumTorquesY()

		entries = self.entries()

		try:
			meanX = torquesX / weights
		except ZeroDivisionError:
			meanX = 0.0

		try:
			meanY = torquesY / weights
		except ZeroDivisionError:
			meanY = 0.0

		try:
			result = (self._sumInertialsX() - torquesX**2 / weights) / weights
			if self._meps2 < result < 0.0:
				rmsX = 0.0
			else:
				rmsX = sqrt(result)
		except ZeroDivisionError:
			rmsX = 0.0

		try:
			result = (self._sumInertialsY() - torquesY**2 / weights) / weights
			if self._meps2 < result < 0.0:
				rmsY = 0.0
			else:
				rmsY = sqrt(result)
		except ZeroDivisionError:
			rmsY = 0.0

		return [entries, meanX, meanY, rmsX, rmsY]

	def _getDataSet(self, i):
		weights = self._binSumOfWeights.data[i]

		try:
			binError = sqrt(abs(self._binSumOfTorquesZ.data[i]) / weights**2)
		except ZeroDivisionError:
			binError = 0.0

		try:
			binMeanX = self._binSumOfTorquesX.data[i] / weights
		except ZeroDivisionError:
			binMeanX = 0.0

		try:
			binMeanY = self._binSumOfTorquesY.data[i] / weights
		except ZeroDivisionError:
			binMeanY = 0.0

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

		try:
			result = (self._binSumOfInertialsZ.data[i] - self._binSumOfTorquesZ.data[i]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				binRmsZ = 0.0
			else:
				binRmsZ = sqrt(result)
		except ZeroDivisionError:
			binRmsZ = 0.0

		return [weights, binError, binMeanX, binMeanY, binRmsX, binRmsY, binRmsZ]

	def binMeanX(self, indexX, indexY):
		indexX += 2
		indexY += 2
		try:
			return self._binSumOfTorquesX[indexX, indexY] / self._binSumOfWeights[indexX, indexY]
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def binMeanY(self, indexX, indexY):
		indexX += 2
		indexY += 2
		try:
			return self._binSumOfTorquesY[indexX, indexY] / self._binSumOfWeights[indexX, indexY]
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def binEntries(self, indexX, indexY):
		try:
			return self._binEntries[2 + indexX, 2 + indexY]
		except:
			raise IllegalArgumentException()

	def binEntriesX(self, indexX):
		indexX += 2
		result = 0.0
		binEntries = self._binEntries
		try:
			for indexY in range(self._sizeY):
				result += binEntries[indexX, indexY]
		except:
			raise IllegalArgumentException()
		else:
			return result

	def binEntriesY(self, indexY):
		indexY += 2
		result = 0.0
		binEntries = self._binEntries
		try:
			for indexX in range(self._sizeX):
				result += binEntries[indexX, indexY]
		except:
			raise IllegalArgumentException()
		else:
			return result

	def binHeight(self, indexX, indexY):
		indexX += 2
		indexY += 2
		try:
			return self._binSumOfTorquesZ[indexX, indexY] / self._binSumOfWeights[indexX, indexY]
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def binHeightX(self, indexX):
		indexX += 2
		binHeight = self.binHeight
		result = 0.0
		try:
			for indexY in range(self._sizeY):
				result += binHeight(indexX, indexY)
			return result
		except:
			raise IllegalArgumentException()

	def binHeightY(self, indexY):
		indexY += 2
		binHeight = self.binHeight
		result = 0.0
		try:
			for indexX in range(self._sizeX):
				result += binHeight(indexX, indexY)
			return result
		except:
			raise IllegalArgumentException()

	def binError(self, indexX, indexY):
		indexX += 2
		indexY += 2
		try:
			return sqrt(abs(self._binSumOfTorquesZ[indexX, indexY]) / self._binSumOfWeights[indexX, indexY]**2)
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def _binError2(self, indexX, indexY):
		indexX += 2
		indexY += 2
		try:
			return abs(self._binSumOfTorquesZ[indexX, indexY]) / self._binSumOfWeights[indexX, indexY]**2
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def binRms(self, indexX, indexY):
		indexX += 2
		indexY += 2
		weights = self._binSumOfWeights[indexX, indexY]
		try:
			result = (self._binSumOfInertialsZ[indexX, indexY] - self._binSumOfTorquesZ[indexX, indexY]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def _binRmsX(self, indexX, indexY):
		indexX += 2
		indexY += 2
		weights = self._binSumOfWeights[indexX, indexY]
		try:
			result = (self._binSumOfInertialsX[indexX, indexY] - self._binSumOfTorquesX[indexX, indexY]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def _binRmsY(self, indexX, indexY):
		indexX += 2
		indexY += 2
		weights = self._binSumOfWeights[indexX, indexY]
		try:
			result = (self._binSumOfInertialsY[indexX, indexY] - self._binSumOfTorquesY[indexX, indexY]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def meanX(self):
		try:
			return self._sumTorquesX() / self._sumWeights()
		except ZeroDivisionError:
			return 0.0

	def meanY(self):
		try:
			return self._sumTorquesY() / self._sumWeights()
		except ZeroDivisionError:
			return 0.0

	def rmsX(self):
		weights = self._sumWeights()
		try:
			result = (self._sumInertialsX() - self._sumTorquesX()**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def rmsY(self):
		weights = self._sumWeights()
		try:
			result = (self._sumInertialsY() - self._sumTorquesY()**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def xAxis(self):
		return self._axis[0]

	def yAxis(self):
		return self._axis[1]

	def coordToIndexX(self, coord):
		return self._axis[0].coordToIndex(coord)

	def coordToIndexY(self, coord):
		return self._axis[1].coordToIndex(coord)

	def add(self, profile):
		if not isinstance(profile, IProfile2D):
			raise IllegalArgumentException()
		if self._axis[0]._edgeList != profile._axis[0]._edgeList:
			raise IllegalArgumentException()
		if self._axis[1]._edgeList != profile._axis[1]._edgeList:
			raise IllegalArgumentException()
		self._add(profile)

	def sumBinHeights(self):
		result = 0.0
		binHeight = self.binHeight
		for x in range(self._sizeX - 2):
			for y in range(self._sizeY - 2):
				result += binHeight(x, y)
		return result

	def sumExtraBinHeights(self):
		result = 0.0
		binHeight = self.binHeight
		for x in [-2, -1]:
			for y in range(self._sizeY - 2):
				result += binHeight(x, y)
		for x in range(self._sizeX - 2):
			for y in [-2, -1]:
				result += binHeight(x, y)
		for x in [-2, -1]:
			for y in [-2, -1]:
				result += binHeight(x, y)
		return result

	def sumAllBinHeights(self):
		result = 0.0
		binHeight = self.binHeight
		for x in range(-2, self._sizeX - 2):
			for y in range(-2, self._sizeY - 2):
				result += binHeight(x, y)
		return result

	def minBinHeight(self):
		binHeight = self.binHeight
		result = binHeight(0, 0)
		for x in range(self._sizeX - 2):
			for y in range(self._sizeY - 2):
				result = min(result, binHeight(x, y))
		return result

	def maxBinHeight(self):
		binHeight = self.binHeight
		result = binHeight(0, 0)
		for x in range(self._sizeX - 2):
			for y in range(self._sizeY - 2):
				result = max(result, binHeight(x, y))
		return result
