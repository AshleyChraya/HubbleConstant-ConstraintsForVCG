from paida.paida_core.PAbsorber import *
from paida.paida_core.IHistogram import *
from paida.paida_core.IAxis import *
from paida.paida_core.PExceptions import *

from math import sqrt

class IHistogram3D(IHistogram):
	def __init__(self, name, title, binEdges, fixedBinning, option = {}):
		IHistogram.__init__(self, title, binEdges)
		self._setName(name)
		self._setOption(option)
		self._axis.append(IAxis(binEdges[0], fixedBinning))
		self._axis.append(IAxis(binEdges[1], fixedBinning))
		self._axis.append(IAxis(binEdges[2], fixedBinning))

	def _localReset(self):
		sizeX = self._sizeX
		sizeY = self._sizeY
		sizeZ = self._sizeZ
		self._binSumOfTorquesX = binArray3(sizeX, sizeY, sizeZ)
		self._binSumOfTorquesY = binArray3(sizeX, sizeY, sizeZ)
		self._binSumOfTorquesZ = binArray3(sizeX, sizeY, sizeZ)
		self._binSumOfInertialsX = binArray3(sizeX, sizeY, sizeZ)
		self._binSumOfInertialsY = binArray3(sizeX, sizeY, sizeZ)
		self._binSumOfInertialsZ = binArray3(sizeX, sizeY, sizeZ)

	def fill(self, x, y, z, weight = 1.0):
		i = self._innerIndex(2 + self._axis[0].coordToIndex(x), 2 + self._axis[1].coordToIndex(y), 2 + self._axis[2].coordToIndex(z))
		self._binEntries.data[i] += 1
		self._binSumOfWeights.data[i] += weight
		self._binSumOfErrors.data[i] += weight**2
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
		torquesZ = self._sumTorquesZ()

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
			meanZ = torquesZ / weights
		except ZeroDivisionError:
			meanZ = 0.0

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

		try:
			result = (self._sumInertialsZ() - torquesZ**2 / weights) / weights
			if self._meps2 < result < 0.0:
				rmsZ = 0.0
			else:
				rmsZ = sqrt(result)
		except ZeroDivisionError:
			rmsZ = 0.0

		return [entries, meanX, meanY, meanZ, rmsX, rmsY, rmsZ]

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
			binMeanY = self._binSumOfTorquesY.data[i] / weights
		except ZeroDivisionError:
			binMeanY = 0.0

		try:
			binMeanZ = self._binSumOfTorquesZ.data[i] / weights
		except ZeroDivisionError:
			binMeanZ = 0.0

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

		return [weights, error, binMeanX, binMeanY, binMeanZ, binRmsX, binRmsY, binRmsZ]

	def binMeanX(self, indexX, indexY, indexZ):
		indexX += 2
		indexY += 2
		indexZ += 2
		try:
			return self._binSumOfTorquesX[indexX, indexY, indexZ] / self._binSumOfWeights[indexX, indexY, indexZ]
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def binMeanY(self, indexX, indexY, indexZ):
		indexX += 2
		indexY += 2
		indexZ += 2
		try:
			return self._binSumOfTorquesY[indexX, indexY, indexZ] / self._binSumOfWeights[indexX, indexY, indexZ]
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def binMeanZ(self, indexX, indexY, indexZ):
		indexX += 2
		indexY += 2
		indexZ += 2
		try:
			return self._binSumOfTorquesZ[indexX, indexY, indexZ] / self._binSumOfWeights[indexX, indexY, indexZ]
		except ZeroDivisionError:
			return 0.0
		except:
			raise IllegalArgumentException()

	def _binRmsX(self, indexX, indexY, indexZ):
		indexX += 2
		indexY += 2
		indexZ += 2
		weights = self._binSumOfWeights[indexX, indexY, indexZ]
		try:
			result = (self._binSumOfInertialsX[indexX, indexY, indexZ] - self._binSumOfTorquesX[indexX, indexY, indexZ]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def _binRmsY(self, indexX, indexY, indexZ):
		indexX += 2
		indexY += 2
		indexZ += 2
		weights = self._binSumOfWeights[indexX, indexY, indexZ]
		try:
			result = (self._binSumOfInertialsY[indexX, indexY, indexZ] - self._binSumOfTorquesY[indexX, indexY, indexZ]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def _binRmsZ(self, indexX, indexY, indexZ):
		indexX += 2
		indexY += 2
		indexZ += 2
		weights = self._binSumOfWeights[indexX, indexY, indexZ]
		try:
			result = (self._binSumOfInertialsZ[indexX, indexY, indexZ] - self._binSumOfTorquesZ[indexX, indexY, indexZ]**2 / weights) / weights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def binEntries(self, indexX, indexY, indexZ):
		try:
			return int(self._binEntries[2 + indexX, 2 + indexY, 2 + indexZ])
		except:
			raise IllegalArgumentException()

	def binEntriesX(self, indexX):
		result = 0.0
		binEntries = self._binEntries
		try:
			for indexY in range(self._sizeY):
				for indexZ in range(self._sizeZ):
					result += binEntries[2 + indexX, indexY, indexZ]
		except:
			raise IllegalArgumentException()
		else:
			return int(result)

	def binEntriesY(self, indexY):
		result = 0.0
		binEntries = self._binEntries
		try:
			for indexX in range(self._sizeX):
				for indexZ in range(self._sizeZ):
					result += binEntries[indexX, 2 + indexY, indexZ]
		except:
			raise IllegalArgumentException()
		else:
			return int(result)

	def binEntriesZ(self, indexZ):
		result = 0.0
		binEntries = self._binEntries
		try:
			for indexX in range(self._sizeX):
				for indexY in range(self._sizeY):
					result += binEntries[indexX, indexY, 2 + indexZ]
		except:
			raise IllegalArgumentException()
		else:
			return int(result)

	def binHeight(self, indexX, indexY, indexZ):
		try:
			return self._binSumOfWeights[2 + indexX, 2 + indexY, 2 + indexZ]
		except:
			raise IllegalArgumentException()

	def binHeightX(self, indexX):
		result = 0.0
		binSumOfWeights = self._binSumOfWeights
		try:
			for indexY in range(self._sizeY):
				for indexZ in range(self._sizeZ):
					result += binSumOfWeights[2 + indexX, indexY, indexZ]
		except:
			raise IllegalArgumentException()
		else:
			return result

	def binHeightY(self, indexY):
		result = 0.0
		binSumOfWeights = self._binSumOfWeights
		try:
			for indexX in range(self._sizeX):
				for indexZ in range(self._sizeZ):
					result += binSumOfWeights[indexX, 2 + indexY, indexZ]
		except:
			raise IllegalArgumentException()
		else:
			return result

	def binHeightZ(self, indexZ):
		result = 0.0
		binSumOfWeights = self._binSumOfWeights
		try:
			for indexX in range(self._sizeX):
				for indexY in range(self._sizeY):
					result += binSumOfWeights[indexX, indexY, 2 + indexZ]
		except:
			raise IllegalArgumentException()
		else:
			return result

	def binError(self, indexX, indexY, indexZ):
		result = self._binSumOfErrors[2 + indexX, 2 + indexY, 2 + indexZ]
		if self._meps2 < result < 0.0:
			return 0.0
		else:
			return sqrt(result)

	def _binError2(self, indexX, indexY, indexZ):
		return self._binSumOfErrors[2 + indexX, 2 + indexY, 2 + indexZ]

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

	def meanZ(self):
		try:
			return self._sumTorquesZ() / self._sumWeights()
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

	def rmsZ(self):
		weights = self._sumWeights()
		try:
			result = (self._sumInertialsZ() - self._sumTorquesZ()**2 / weights) / weights
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

	def zAxis(self):
		return self._axis[2]

	def coordToIndexX(self, coord):
		return self._axis[0].coordToIndex(coord)

	def coordToIndexY(self, coord):
		return self._axis[1].coordToIndex(coord)

	def coordToIndexZ(self, coord):
		return self._axis[2].coordToIndex(coord)

	def add(self, hist):
		if isinstance(hist, IHistogram3D):
			if self._axis[0]._edgeList != hist._axis[0]._edgeList:
				raise IllegalArgumentException()
			if self._axis[1]._edgeList != hist._axis[1]._edgeList:
				raise IllegalArgumentException()
			if self._axis[2]._edgeList != hist._axis[2]._edgeList:
				raise IllegalArgumentException()
			self._add(hist)
		else:
			raise IllegalArgumentException()
