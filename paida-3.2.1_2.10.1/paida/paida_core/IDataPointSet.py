from paida.paida_core.PAbsorber import *
from paida.paida_core.IAnnotation import *
from paida.paida_core.IDataPoint import *
from paida.paida_core.PExceptions import *

class IDataPointSet:

	def __init__(self, name, title, dimension, options = {}):
		self._annotation = IAnnotation()
		self._annotation.addItem('Title', title, True)
		self._name = name
		self._dimension = dimension
		self._dataPoint = []
		self._options = options

	def annotation(self):
		return self._annotation

	def title(self):
		return self._annotation.value('Title')

	def setTitle(self, title):
		try:
			self._annotation.setValue('Title', title)
		except IllegalArgumentException:
			raise IllegalArgumentException()

	def dimension(self):
		return self._dimension

	def clear(self):
		self._dataPoint = []

	def size(self):
		return len(self._dataPoint)

	def point(self, index):
		return self._dataPoint[index]

	def addPoint(self, point = None):
		if point == None:
			newDataPoint = IDataPoint(self.dimension())
			self._dataPoint.append(newDataPoint)
			return newDataPoint
		else:
			dimension = self.dimension()
			if point.dimension() == dimension:
				newDataPoint = IDataPoint(dimension)
				for i in range(dimension):
					measurement = point.coordinate(i)
					newMeasurement = newDataPoint.coordinate(i)
					newMeasurement.setValue(measurement.value())
					newMeasurement.setErrorPlus(measurement.errorPlus())
					newMeasurement.setErrorMinus(measurement.errorMinus())
				self._dataPoint.append(newDataPoint)
			else:
				raise IllegalArgumentException("The point's dimension does not math with this dataPointSet.")

	def removePoint(self, index):
		if 0 <= index < self.size():
			self._dataPoint.remove(self._dataPoint[index])
		else:
			raise IllegalArgumentException('The point index is invalid.')

	def lowerExtent(self, coord):
		if 0 <= coord < self.dimension():
			if self.size() == 0:
				raise IllegalArgumentException('The size is still zero.')
			else:
				measurement0 = self._dataPoint[0].coordinate(coord)
				lower = measurement0.value() - measurement0.errorMinus()
				for dataPoint in self._dataPoint[1:]:
					measurement = dataPoint.coordinate(coord)
					lower = min(lower, measurement.value() - measurement.errorMinus())
				return lower
		else:
			raise IllegalArgumentException('The coordinate index is invalid.')

	def upperExtent(self, coord):
		if 0 <= coord < self.dimension():
			if self.size() == 0:
				raise IllegalArgumentException('The size is still zero.')
			else:
				measurement0 = self._dataPoint[0].coordinate(coord)
				upper = measurement0.value() + measurement0.errorPlus()
				for dataPoint in self._dataPoint[1:]:
					measurement = dataPoint.coordinate(coord)
					upper = max(upper, measurement.value() + measurement.errorPlus())
				return upper
		else:
			raise IllegalArgumentException('The coordinate index is invalid.')

	def scale(self, scaleFactor):
		self.scaleValues(scaleFactor)
		self.scaleErrors(scaleFactor)

	def scaleValues(self, scaleFactor):
		dimension = self.dimension()
		for dataPoint in self._dataPoint:
			for coord in range(dimension):
				measurement = dataPoint.coordinate(coord)
				measurement.setValue(measurement.value() * scaleFactor)
	
	def scaleErrors(self, scaleFactor):
		dimension = self.dimension()
		for dataPoint in self._dataPoint:
			for coord in range(dimension):
				measurement = dataPoint.coordinate(coord)
				measurement.setErrorPlus(measurement.errorPlus() * scaleFactor)
				measurement.setErrorMinus(measurement.errorMinus() * scaleFactor)

	def setCoordinate(self, coord, values, errors1, errors2 = None):
		if (coord < 0) or (coord >= self.dimension()):
			raise IllegalArgumentException('The coordinate index is invalid.')
		if errors2 == None:
			errors2 = errors1
		length = len(values)
		if (length != len(errors1)) and (length != len(errors2)):
			raise IllegalArgumentException('The arrays of values, plus errors and minus errors do not have the same length.')

		size = self.size()
		if size == 0:
			for i , value in enumerate(values):
				data = self.addPoint().coordinate(coord)
				data.setValue(value)
				data.setErrorPlus(errors1[i])
				data.setErrorMinus(errors2[i])
		else:
			if length != size:
				raise IllegalArgumentException('The size of values/errors does not match with this dataPointSet.')
			else:
				for i in range(size):
					data = self.point(i).coordinate(coord)
					data.setValue(values[i])
					data.setErrorPlus(errors1[i])
					data.setErrorMinus(errors2[i])
