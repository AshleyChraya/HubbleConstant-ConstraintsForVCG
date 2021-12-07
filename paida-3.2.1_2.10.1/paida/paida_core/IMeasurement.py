from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import *

class IMeasurement:

	def __init__(self):
		self._values = [0.0] * 3

	def value(self):
		return self._values[0]

	def errorMinus(self):
		return self._values[1]

	def errorPlus(self):
		return self._values[2]

	def setValue(self, value):
		self._values[0] = float(value)

	def setErrorMinus(self, errorMinus):
		if errorMinus < 0.0:
			raise IllegalArgumentException()
		self._values[1] = float(errorMinus)

	def setErrorPlus(self, errorPlus):
		if errorPlus < 0.0:
			raise IllegalArgumentException()
		self._values[2] = float(errorPlus)
