from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import *

import types

class InfinityBase:
	def __abs__(self):
		return InfinityPositive()

	def __nonzero__(self):
		return True

	def __radd__(self, v):
		return self.__add__(v)

	def __rsub__(self, v):
		return -self.__sub__(v)

	def __rmul__(self, v):
		return self.__mul__(v)

	def __rdiv__(self, v):
		if type(v) == types.IntType:
			return 0
		elif type(v) == types.LongType:
			return 0L
		elif type(v) == types.FloatType:
			return 0.0
		else:
			raise RuntimeException("Inf cannot divide %s" % (type(v)))

class InfinityPositive(InfinityBase):
	def __add__(self, v):
		return InfinityPositive()

	def __div__(self, v):
		if v > 0:
			return InfinityPositive()
		else:
			return InfinityNegative()

	def __float__(self):
		return InfinityPositive()

	def __floordiv__(self, v):
		return InfinityPositive()

	def __int__(self):
		return InfinityPositive()

	def __long__(self):
		return InfinityPositive()

	def __mul__(sefl, v):
		if v > 0:
			return InfinityPositive()
		else:
			return InfinityNegative()

	def __neg__(self):
		return InfinityNegative()

	def __pos__(self):
		return InfinityPositive()

	def __pow__(self, v):
		return InfinityPositive()

	def __sub__(self, v):
		return InfinityPositive()

	def __truediv__(self, v):
		if v > 0:
			return InfinityPositive()
		else:
			return InfinityNegative()

	def __rpow__(self, v):
		if v < 0:
			raise RuntimeException("negative value power by positive Inf")
		elif v == 0:
			if type(v) == types.IntType:
				return 0
			elif type(v) == types.LongType:
				return 0L
			elif type(v) == types.FloatType:
				return 0.0
			else:
				raise RuntimeException()
		elif 0 < v < 1:
			return 0.0
		elif v == 1:
			if type(v) == types.IntType:
				return 1
			elif type(v) == types.LongType:
				return 1L
			elif type(v) == types.FloatType:
				return 1.0
			else:
				raise RuntimeException()
		elif 1 < v:
			return InfinityPositive()
		else:
			raise RuntimeException()

	def __lt__(self, v):
		return False

	def __le__(self, v):
		if isinstance(v, InfinityPositive) == True:
			return True
		else:
			return False

	def __eq__(self, v):
		if isinstance(v, InfinityPositive) == True:
			return True
		else:
			return False

	def __ne__(self, v):
		if isinstance(v, InfinityPositive) == True:
			return False
		else:
			return True

	def __gt__(self, v):
		if isinstance(v, InfinityPositive) == True:
			return False
		else:
			return True

	def __ge__(self, v):
		return True

class InfinityNegative(InfinityBase):
	def __add__(self, v):
		return InfinityNegative()

	def __div__(self, v):
		if v > 0:
			return InfinityNegative()
		else:
			return InfinityPositive()

	def __float__(self):
		return InfinityNegative()

	def __floordiv__(self, v):
		return InfinityNegative()

	def __int__(self):
		return InfinityNegative()

	def __long__(self):
		return InfinityNegative()

	def __mul__(sefl, v):
		if v > 0:
			return InfinityNegative()
		else:
			return InfinityPositive()

	def __neg__(self):
		return InfinityPositive()

	def __pos__(self):
		return InfinityNegative()

	def __pow__(self, v):
		if type(v) == types.IntType:
			if (v % 2) == 0:
				return InfinityPositive()
			else:
				return InfinityNegative()
		else:
			raise RuntimeException("negative Inf cannot be raised to a fractional power")

	def __sub__(self, v):
		return InfinityNegative()

	def __truediv__(self, v):
		if v > 0:
			return InfinityNegative()
		else:
			return InfinityPositive()

	def __rpow__(self, v):
		if v < 0:
			raise RuntimeException("negative value power by negative Inf")
		elif v == 0:
			raise RuntimeException("zero power by negative Inf")
		elif 0 < v < 1:
			return InfinityPositive()
		elif v == 1:
			if type(v) == types.IntType:
				return 1
			elif type(v) == types.LongType:
				return 1L
			elif type(v) == types.FloatType:
				return 1.0
			else:
				raise RuntimeException()
		elif 1 < v:
			if type(v) == types.IntType:
				return 0
			elif type(v) == types.LongType:
				return 0L
			elif type(v) == types.FloatType:
				return 0.0
			else:
				raise RuntimeException()
		else:
			raise RuntimeException()

	def __lt__(self, v):
		if isinstance(v, InfinityNegative) == True:
			return False
		else:
			return True

	def __le__(self, v):
		return True

	def __eq__(self, v):
		if isinstance(v, InfinityNegative) == True:
			return True
		else:
			return False

	def __ne__(self, v):
		if isinstance(v, InfinityNegative) == True:
			return False
		else:
			return True

	def __gt__(self, v):
		return False

	def __ge__(self, v):
		if isinstance(v, InfinityNegative) == True:
			return True
		else:
			return False

class IRangeSet:
	_NINF = InfinityNegative()
	_PINF = InfinityPositive()

	def __init__(self):
		self._rangeList = [[self._NINF, self._PINF]]

	def lowerBounds(self):
		result = []
		for rangeItem in self._rangeList:
			result.append(rangeItem[0])
		return result

	def upperBounds(self):
		result = []
		for rangeItem in self._rangeList:
			result.append(rangeItem[1])
		return result

	def include(self, xMin, xMax):
		lowerBounds = self.lowerBounds()
		upperBounds = self.upperBounds()
		lowerBounds.append(float(xMin))
		upperBounds.append(float(xMax))
		lowerBounds.sort()
		upperBounds.sort()
		currentLower = lowerBounds[0]
		currentUpper = upperBounds[0]
		result = []
		for i in range(len(lowerBounds)):
			if (lowerBounds[i] <= currentUpper) and (upperBounds[i] > currentUpper):
				currentUpper = upperBounds[i]
			elif (lowerBounds[i] > currentUpper) and (upperBounds[i] > currentUpper):
				result.append([currentLower, currentUpper])
				currentLower = lowerBounds[i]
				currentUpper = upperBounds[i]
			elif (lowerBounds[i] <= currentUpper) and (upperBounds[i] <= currentUpper):
				pass
			else:
				###If this case happens, it means miss-implementation.
				raise RuntimeException()
		result.append([currentLower, currentUpper])
		self._rangeList = result

	def exclude(self, xMin, xMax):
		result = []
		floatXMin = float(xMin)
		floatXMax = float(xMax)
		for rangeItem in self._rangeList:
			if rangeItem[1] <= floatXMin:
				result.append([rangeItem[0], rangeItem[1]])
			elif (rangeItem[0] < floatXMin) and (floatXMin < rangeItem[1] <= floatXMax):
				result.append([rangeItem[0], floatXMin])
			elif (rangeItem[0] < floatXMin) and (rangeItem[1] > floatXMax):
				result.append([rangeItem[0], floatXMin])
				result.append([floatXMax, rangeItem[1]])
			elif (floatXMin <= rangeItem[0] < floatXMax) and (rangeItem[1] <= floatXMax):
				pass
			elif (floatXMin <= rangeItem[0] < floatXMax) and (floatXMax < rangeItem[1]):
				result.append([floatXMax, rangeItem[1]])
			elif floatXMax <= rangeItem[0]:
				result.append([rangeItem[0], rangeItem[1]])
			else:
				###If this case happens, it means miss-implementation.
				raise RuntimeException()
		self._rangeList = result

	def includeAll(self):
		self._rangeList = [[self._NINF, self._PINF]]
	
	def excludeAll(self):
		self._rangeList = []

	def isInRange(self, point):
		floatPoint = float(point)
		for rangeItem in self._rangeList:
			if rangeItem[0] <= floatPoint <= rangeItem[1]:
				return True
		return False
	
	def size(self):
		return len(self._rangeList)

	def PLUS_INF(self):
		return self._PINF

	def MINUS_INF(self):
		return self._NINF
