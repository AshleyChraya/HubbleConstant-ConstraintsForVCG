from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import *
from paida.paida_core.IRangeSet import IRangeSet

class IAxis:

	OVERFLOW_BIN = -1
	UNDERFLOW_BIN = -2

	def __init__(self, edgeList, isFixedBinning):
		self._edgeList = edgeList
		self._isFixedBinning = isFixedBinning
		self._bins = len(self._edgeList) - 1
		self._length = edgeList[-1] - edgeList[0]

	def _getEdges(self):
		return self._edgeList

	def _binEdges(self, binIndex):
		if binIndex == self.OVERFLOW_BIN:
			return self._edgeList[-1], IRangeSet._PINF
		elif binIndex == self.UNDERFLOW_BIN:
			return IRangeSet._NINF, self._edgeList[0]
		else:
			return self._edgeList[binIndex], self._edgeList[binIndex + 1]

	def binLowerEdge(self, binIndex):
		if binIndex == self.OVERFLOW_BIN:
			return self._edgeList[-1]
		elif binIndex == self.UNDERFLOW_BIN:
			return IRangeSet._NINF
		else:
			return self._edgeList[binIndex]

	def binUpperEdge(self, binIndex):
		if binIndex == self.OVERFLOW_BIN:
			return IRangeSet._PINF
		elif binIndex == self.UNDERFLOW_BIN:
			return self._edgeList[0]
		else:
			return self._edgeList[binIndex + 1]

	def bins(self):
		return self._bins

	def binWidth(self, binIndex):
		if binIndex in [self.OVERFLOW_BIN, self.UNDERFLOW_BIN]:
			return IRangeSet._PINF
		else:
			return self._edgeList[binIndex + 1] - self._edgeList[binIndex]

	def coordToIndex(self, coord):
		edgeList = self._edgeList
		if coord < edgeList[0]:
			return self.UNDERFLOW_BIN
		elif coord >= edgeList[-1]:
			return self.OVERFLOW_BIN
		else:
			if self._isFixedBinning:
				return int(self._bins * (coord - edgeList[0]) / self._length)
			else:
				for i in range(self._bins):
					if edgeList[i] <= coord < edgeList[i + 1]:
						return i

	def isFixedBinning(self):
		return self._isFixedBinning

	def lowerEdge(self):
		return self._edgeList[0]

	def upperEdge(self):
		return self._edgeList[-1]
