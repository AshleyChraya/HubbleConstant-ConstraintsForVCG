from paida.paida_core.PAbsorber import *
from paida.paida_core.ICloud import *
from paida.paida_core.IHistogram3D import *
from paida.paida_core.PExceptions import *

import types

class ICloud3D(ICloud):

	def __init__(self, name, title, nMax = -1, option = {}):
		ICloud.__init__(self, title, nMax)
		self._setName(name)
		self._setOption(option)
		self._axis.append(None)
		self._axis.append(None)
		self._axis.append(None)

	def reset(self):
		ICloud.reset(self)

	def fill(self, x, y, z, weight = 1.0):
		if self._isConverted:
			self._histogram.fill(x, y, z, weight)
			return
		else:
			if (self._nMax == -1) or (self.entries() < self._nMax):
				x = float(x)
				y = float(y)
				z = float(z)
				weight = float(weight)

				if self.entries() == 0:
					self._lowerEdges = [x, y, z]
					self._upperEdges = [x, y, z]
				else:
					if x < self._lowerEdges[0]:
						self._lowerEdges[0] = x
					elif x > self._upperEdges[0]:
						self._upperEdges[0] = x
					if y < self._lowerEdges[1]:
						self._lowerEdges[1] = y
					elif y > self._upperEdges[1]:
						self._upperEdges[1] = y
					if z < self._lowerEdges[2]:
						self._lowerEdges[2] = z
					elif z > self._upperEdges[2]:
						self._upperEdges[2] = z

				self._entryList[0].append([x, y, z])
				self._entryList[1].append(weight)
				self._sumOfWeights += weight
				self._sumOfTorques[0] += x * weight
				self._sumOfInertials[0] += x**2 * weight
				self._sumOfTorques[1] += y * weight
				self._sumOfInertials[1] += y**2 * weight
				self._sumOfTorques[2] += z * weight
				self._sumOfInertials[2] += z**2 * weight
			else:
				option = self._getOption()
				if (option.has_key('autoConvert')) and (option['autoConvert'] == False):
					return
				else:
					self.convertToHistogram()
					self._histogram.fill(x, y, z, weight)
					return

	def lowerEdgeX(self):
		return self._lowerEdges[0]

	def upperEdgeX(self):
		return self._upperEdges[0]

	def lowerEdgeY(self):
		return self._lowerEdges[1]

	def upperEdgeY(self):
		return self._upperEdges[1]

	def lowerEdgeZ(self):
		return self._lowerEdges[2]

	def upperEdgeZ(self):
		return self._upperEdges[2]

	def valueX(self, indexNumber):
		try:
			return self._entryList[0][indexNumber][0]
		except IndexError:
			raise IllegalArgumentException('IndexError: list index out of range')

	def valueY(self, indexNumber):
		try:
			return self._entryList[0][indexNumber][1]
		except IndexError:
			raise IllegalArgumentException('IndexError: list index out of range')

	def valueZ(self, indexNumber):
		try:
			return self._entryList[0][indexNumber][2]
		except IndexError:
			raise IllegalArgumentException('IndexError: list index out of range')

	def weight(self, indexNumber):
		try:
			return self._entryList[1][indexNumber]
		except IndexError:
			raise IllegalArgumentException('IndexError: list index out of range')

	def meanX(self):
		try:
			return self._sumOfTorques[0] / self._sumOfWeights
		except ZeroDivisionError:
			return 0.0

	def meanY(self):
		try:
			return self._sumOfTorques[1] / self._sumOfWeights
		except ZeroDivisionError:
			return 0.0

	def meanZ(self):
		try:
			return self._sumOfTorques[2] / self._sumOfWeights
		except ZeroDivisionError:
			return 0.0

	def rmsX(self):
		try:
			result = (self._sumOfInertials[0] - self._sumOfTorques[0]**2 / self._sumOfWeights) / self._sumOfWeights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def rmsY(self):
		try:
			result = (self._sumOfInertials[1] - self._sumOfTorques[1]**2 / self._sumOfWeights) / self._sumOfWeights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def rmsZ(self):
		try:
			result = (self._sumOfInertials[2] - self._sumOfTorques[2]**2 / self._sumOfWeights) / self._sumOfWeights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def convert(self, data1, data2, data3, data4 = None, data5 = None, data6 = None, data7 = None, data8 = None, data9 = None):
		if self.isConverted() == True:
			raise AlreadyConvertedException()
		else:
			if hasattr(data1, '__iter__') and hasattr(data2, '__iter__') and hasattr(data3, '__iter__') and (data4 == None) and (data5 == None) and (data6 == None) and (data7 == None) and (data8 == None) and (data9 == None):
				binEdgesX = data1
				binEdgesY = data2
				binEdgesZ = data3
				binEdges = [binEdgesX, binEdgesY, binEdgesZ]
				self._histogram = IHistogram3D(self._convertedName(), self.title(), binEdges, False)
			elif isinstance(data1, types.IntType) and isinstance(data2, types.FloatType) and isinstance(data3, types.FloatType) and isinstance(data4, types.IntType) and isinstance(data5, types.FloatType) and isinstance(data6, types.FloatType) and isinstance(data7, types.IntType) and isinstance(data8, types.FloatType) and isinstance(data9, types.FloatType):
				nBinsX = data1
				lowerEdgeX = data2
				upperEdgeX = data3
				nBinsY = data4
				lowerEdgeY = data5
				upperEdgeY = data6
				nBinsZ = data7
				lowerEdgeZ = data8
				upperEdgeZ = data9
				self._histogram = self._getRawHistogram(nBinsX, lowerEdgeX, upperEdgeX, nBinsY, lowerEdgeY, upperEdgeY, nBinsZ, lowerEdgeZ, upperEdgeZ)
			else:
				raise IllegalArgumentException()

			self.fillHistogram(self._histogram)
			self._isConverted = True

	def _getRawHistogram(self, nBinsX, lowerEdgeX, upperEdgeX, nBinsY, lowerEdgeY, upperEdgeY, nBinsZ, lowerEdgeZ, upperEdgeZ):
		if lowerEdgeX == upperEdgeX:
			lowerEdgeX -= 5.0
			upperEdgeX += 5.0
		if lowerEdgeY == upperEdgeY:
			lowerEdgeY -= 5.0
			upperEdgeY += 5.0
		if lowerEdgeZ == upperEdgeZ:
			lowerEdgeZ -= 5.0
			upperEdgeZ += 5.0
		binWidthX = (upperEdgeX - lowerEdgeX) / (nBinsX - 1)
		binWidthY = (upperEdgeY - lowerEdgeY) / (nBinsY - 1)
		binWidthZ = (upperEdgeZ - lowerEdgeZ) / (nBinsZ - 1)
		binEdgesX = []
		binEdgesY = []
		binEdgesZ = []
		for i in range(nBinsX + 1):
			binEdgesX.append(lowerEdgeX + i * binWidthX)
		for i in range(nBinsY + 1):
			binEdgesY.append(lowerEdgeY + i * binWidthY)
		for i in range(nBinsZ + 1):
			binEdgesZ.append(lowerEdgeZ + i * binWidthZ)
		binEdges = [binEdgesX, binEdgesY, binEdgesZ]
		return IHistogram3D(self._convertedName(), self.title(), binEdges, True)

	def convertToHistogram(self):
		ICloud.convertToHistogram(self)
		option = self._getOption()
		if option.has_key('nBinsX'):
			nBinsX = int(option['nBinsX'])
		else:
			nBinsX = 50
		if option.has_key('nBinsY'):
			nBinsY = int(option['nBinsY'])
		else:
			nBinsY = 50
		if option.has_key('nBinsZ'):
			nBinsZ = int(option['nBinsZ'])
		else:
			nBinsZ = 50
		self.convert(nBinsX, self.lowerEdgeX(), self.upperEdgeX(), nBinsY, self.lowerEdgeY(), self.upperEdgeY(), nBinsZ, self.lowerEdgeZ(), self.upperEdgeZ())
	
	def histogram(self):
		if self.isConverted() == False:
			raise RuntimeException()
		else:
			return self._histogram

	def fillHistogram(self, histogram):
		position = self._entryList[0]
		weight = self._entryList[1]
		for i in range(self.entries()):
			histogram.fill(position[i][0], position[i][1], position[i][2], weight[i])
