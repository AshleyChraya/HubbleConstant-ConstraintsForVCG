from paida.paida_core.PAbsorber import *
from paida.paida_core.IMeasurement import *

class IDataPoint:

	def __init__(self, dimension):
		self._dimension = dimension
		self._measurement = []
		for i in range(dimension):
			self._measurement.append(IMeasurement())

	def coordinate(self, coord):
		return self._measurement[coord]

	def dimension(self):
		return self._dimension
