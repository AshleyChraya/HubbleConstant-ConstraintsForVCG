from paida.paida_core.PAbsorber import *
from paida.paida_core.ICloud import *
from paida.paida_core.IHistogram1D import *
from paida.paida_core.PExceptions import *

import types

class ICloud1D(ICloud):

	def __init__(self, name, title, nMax = -1, option = {}):
		ICloud.__init__(self, title, nMax)
		self._setName(name)
		self._setOption(option)
		self._axis.append(None)

	def reset(self):
		ICloud.reset(self)

	def fill(self, x, weight = 1.0):
		if self._isConverted:
			self._histogram.fill(x, weight)
			return
		else:
			if (self._nMax == -1) or (self.entries() < self._nMax):
				x = float(x)
				weight = float(weight)

				if self.entries() == 0:
					self._lowerEdges = [x, 0.0, 0.0]
					self._upperEdges = [x, 0.0, 0.0]
				else:
					if x < self._lowerEdges[0]:
						self._lowerEdges[0] = x
					elif x > self._upperEdges[0]:
						self._upperEdges[0] = x

				self._entryList[0].append([x])
				self._entryList[1].append(weight)
				self._sumOfWeights += weight
				self._sumOfTorques[0] += x * weight
				self._sumOfInertials[0] += x**2 * weight
			else:
				option = self._getOption()
				if (option.has_key('autoConvert')) and (option['autoConvert'] == False):
					return
				else:
					self.convertToHistogram()
					self._histogram.fill(x, weight)
					return

	def lowerEdge(self):
		return self._lowerEdges[0]

	def upperEdge(self):
		return self._upperEdges[0]

	def value(self, indexNumber):
		try:
			return self._entryList[0][indexNumber][0]
		except IndexError:
			raise IllegalArgumentException('IndexError: list index out of range')

	def weight(self, indexNumber):
		try:
			return self._entryList[1][indexNumber]
		except IndexError:
			raise IllegalArgumentException('IndexError: list index out of range')

	def mean(self):
		try:
			return self._sumOfTorques[0] / self._sumOfWeights
		except ZeroDivisionError:
			return 0.0

	def rms(self):
		try:
			result = (self._sumOfInertials[0] - self._sumOfTorques[0]**2 / self._sumOfWeights) / self._sumOfWeights
			if self._meps2 < result < 0.0:
				return 0.0
			else:
				return sqrt(result)
		except ZeroDivisionError:
			return 0.0

	def convert(self, data1, data2 = None, data3 = None):
		if self.isConverted() == True:
			raise AlreadyConvertedException()
		else:
			if hasattr(data1, '__iter__') and (data2 == None) and (data3 == None):
				binEdgesX = data1
				binEdgesY = []
				binEdgesZ = []
				binEdges = [binEdgesX, binEdgesY, binEdgesZ]
				self._histogram = IHistogram1D(self._convertedName(), self.title(), binEdges, False)
			elif isinstance(data1, types.IntType) and isinstance(data2, types.FloatType) and isinstance(data3, types.FloatType):
				nBinsX = data1
				lowerEdgeX = data2
				upperEdgeX = data3
				self._histogram = self._getRawHistogram(nBinsX, lowerEdgeX, upperEdgeX)
			else:
				raise IllegalArgumentException()

			self.fillHistogram(self._histogram)
			self._isConverted = True

	def _getRawHistogram(self, nBinsX, lowerEdgeX, upperEdgeX):
		if lowerEdgeX == upperEdgeX:
			lowerEdgeX -= 5.0
			upperEdgeX += 5.0
		binWidthX = (upperEdgeX - lowerEdgeX) / (nBinsX - 1)
		binEdgesX = []
		binEdgesY = []
		binEdgesZ = []
		for i in range(nBinsX + 1):
			binEdgesX.append(lowerEdgeX + i * binWidthX)
		binEdges = [binEdgesX, binEdgesY, binEdgesZ]
		return IHistogram1D(self._convertedName(), self.title(), binEdges, True)

	def convertToHistogram(self):
		ICloud.convertToHistogram(self)
		option = self._getOption()
		if option.has_key('nBinsX'):
			nBinsX = int(option['nBinsX'])
		else:
			nBinsX = 50
		self.convert(nBinsX, self.lowerEdge(), self.upperEdge())

	def histogram(self):
		if self.isConverted() == False:
			raise RuntimeException()
		else:
			return self._histogram

	def fillHistogram(self, histogram):
		position = self._entryList[0]
		weight = self._entryList[1]
		for i in range(self.entries()):
			histogram.fill(position[i][0], weight[i])
