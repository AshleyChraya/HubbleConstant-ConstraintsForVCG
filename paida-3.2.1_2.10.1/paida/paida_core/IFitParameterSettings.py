from paida.paida_core.PAbsorber import *
from paida.paida_core.IRangeSet import *

class IFitParameterSettings:
	def __init__(self, name):
		self._name = name
		self._stepSize = None
		self._lowerBound = IRangeSet._NINF
		self._upperBound = IRangeSet._PINF
		self._isBound = False
		self._isFixed = False
		self._expressionBound = None

	def reset(self):
		self._stepSize = None
		self._lowerBound = IRangeSet._NINF
		self._upperBound = IRangeSet._PINF
		self._isBound = False
		self._isFixed = False
		self._expressionBound = None

	def stepSize(self):
		return self._stepSize
	
	def upperBound(self):
		return self._upperBound

	def lowerBound(self):
		return self._lowerBound

	def isBound(self):
		return self._isBound

	def isFixed(self):
		return self._isFixed
	
	def setStepSize(self, step):
		self._stepSize = float(step)

	def setBounds(self, lo, up):
		self._lowerBound = float(lo)
		self._upperBound = float(up)
		self._isBound = True
		self._expressionBound = '(not (%s < %s < %s))' % (self._lowerBound, self._name, self._upperBound)

	def removeBounds(self):
		self._lowerBound = IRangeSet._NINF
		self._upperBound = IRangeSet._PINF
		self._isBound = False
		self._expressionBound = None
	
	def setFixed(self, isFixed):
		self._isFixed = bool(isFixed)
	
	def setLowerBound(self, lowerBound):
		self._lowerBound = float(lowerBound)
		self._isBound = True
		self._expressionBound = '(not (%s < %s < %s))' % (self._lowerBound, self._name, self._upperBound)
		
	def setUpperBound(self, UpperBound):
		self._UpperBound = float(UpperBound)
		self._isBound = True
		self._expressionBound = '(not (%s < %s < %s))' % (self._lowerBound, self._name, self._upperBound)
