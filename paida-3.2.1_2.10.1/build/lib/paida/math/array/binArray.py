"""Array classes for bin data.

These don't like negative index."""

from paida.paida_core.PAbsorber import *
from types import TupleType, IntType
from UserList import UserList

class binArray2(UserList):
	def __init__(self, sizeX, sizeY):
		UserList.__init__(self, [0.0])
		self.data *= sizeX * sizeY
		self.sizeX = sizeX
		self.sizeY = sizeY
		self.lenY = sizeX

	def reset(self):
		self.data = [0.0] * (self.sizeX * self.sizeY)

	def sum(self):
		return sum(self.data)

	def sumRange(self, i, j):
		return sum(self.data[i:j])

	def sumInRange(self):
		return self.sum() - self.sumOutRange()

	def sumOutRange(self):
		data = self.data
		if self.sizeY == 1:
			return data[0] + data[1]
		else:
			result = 0.0
			lenY = self.lenY
			for x in [0, 1]:
				for y in range(2, self.sizeY):
					result += data[y * lenY + x]
			for x in range(2, self.sizeX):
				for y in [0, 1]:
					result += data[y * lenY + x]
			for x in [0, 1]:
				for y in [0, 1]:
					result += data[y * lenY + x]
			return result

	def __getitem__(self, s):
		if isinstance(s, TupleType):
			return self.data[s[1] * self.lenY + s[0]]
		elif isinstance(s, IntType):
			return self.data[s]
		else:
			raise RuntimeError

	def __setitem__(self, s, data):
		if isinstance(s, TupleType):
			self.data[s[1] * self.lenY + s[0]] = data
		else:
			raise RuntimeError

	def getIndex(self, x, y):
		return y * self.lenY + x

	def set(self, i, data):
		self.data[i] = data

	def size(self):
		return self.sizeX, self.sizeY

	def length(self):
		return self.lenY

	def scale(self, factor):
		data = self.data
		for i in range(len(data)):
			data[i] *= factor

	def fill(self, sx, sy, weight):
		self.data[sy * self.lenY + sx] += weight

	def add(self, a):
		if len(a.data) != len(self.data):
			raise TypeError

		data = self.data
		data2 = a.data
		for i in range(len(data)):
			data[i] += data2[i]

	def subtract(self, a):
		if len(a.data) != len(self.data):
			raise TypeError

		data = self.data
		data2 = a.data
		for i in range(len(data)):
			data[i] -= data2[i]

	def multiply(self, a):
		if len(a.data) != len(self.data):
			raise TypeError

		data = self.data
		data2 = a.data
		for i in range(len(data)):
			data[i] *= data2[i]

	def multiplySquared(self, a):
		if len(a.data) != len(self.data):
			raise TypeError

		data = self.data
		data2 = a.data
		for i in range(len(data)):
			data[i] *= data2[i]**2

class binArray3(UserList):
	def __init__(self, sizeX, sizeY, sizeZ):
		UserList.__init__(self, [0.0])
		self.data *= sizeX * sizeY * sizeZ
		self.sizeX = sizeX
		self.sizeY = sizeY
		self.sizeZ = sizeZ
		self.lenZ = sizeX * sizeY
		self.lenY = sizeX

	def reset(self):
		self.data = [0.0] * (self.sizeX * self.sizeY * self.sizeZ)

	def sum(self):
		return sum(self.data)

	def sumRange(self, i, j):
		return sum(self.data[i:j])

	def sumInRange(self):
		return self.sum() - self.sumOutRange()

	def sumOutRange(self):
		data = self.data
		if self.sizeY == 1:
			### self.sizeZ must be one.
			return data[0] + data[1]
		else:
			result = 0.0
			lenY = self.lenY
			lenZ = self.lenZ
			if self.sizeZ == 1:
				### 2D array.
				for x in [0, 1]:
					for y in range(2, self.sizeY):
						result += data[y * lenY + x]
				for x in range(2, self.sizeX):
					for y in [0, 1]:
						result += data[y * lenY + x]
				for x in [0, 1]:
					for y in [0, 1]:
						result += data[y * lenY + x]
				return result
			else:
				### 3D array.
				sizeX = self.sizeX
				sizeY = self.sizeY
				sizeZ = self.sizeZ
				for x in [0, 1]:
					for y in range(2, sizeY):
						offset = y * lenY + x
						for z in range(2, sizeZ):
							result += data[z * lenZ + offset]
				for x in range(2, sizeX):
					for y in [0, 1]:
						offset = y * lenY + x
						for z in range(2, sizeZ):
							result += data[z * lenZ + offset]
				for x in range(2, sizeX):
					for y in range(2, sizeY):
						offset = y * lenY + x
						for z in [0, 1]:
							result += data[z * lenZ + offset]
				for x in [0, 1]:
					for y in [0, 1]:
						offset = y * lenY + x
						for z in range(2, sizeZ):
							result += data[z * lenZ + offset]
				for x in [0, 1]:
					for y in range(2, sizeY):
						offset = y * lenY + x
						for z in [0, 1]:
							result += data[z * lenZ + offset]
				for x in range(2, sizeX):
					for y in [0, 1]:
						offset = y * lenY + x
						for z in [0, 1]:
							result += data[z * lenZ + offset]
				for x in [0, 1]:
					for y in [0, 1]:
						offset = y * lenY + x
						for z in [0, 1]:
							result += data[z * lenZ + offset]
				return result

	def __getitem__(self, s):
		if isinstance(s, TupleType):
			return self.data[s[2] * self.lenZ + s[1] * self.lenY + s[0]]
		elif isinstance(s, IntType):
			return self.data[s]
		else:
			raise RuntimeError

	def __setitem__(self, s, data):
		if isinstance(s, TupleType):
			self.data[s[2] * self.lenZ + s[1] * self.lenY + s[0]] = data
		else:
			raise RuntimeError

	def getIndex(self, x, y, z):
		return z * self.lenZ + y * self.lenY + x

	def set(self, i, data):
		self.data[i] = data

	def size(self):
		return self.sizeX, self.sizeY, self.sizeZ

	def length(self):
		return self.lenY, self.lenZ

	def scale(self, factor):
		data = self.data
		for i in range(len(data)):
			data[i] *= factor

	def fill(self, sx, sy, sz, weight):
		self.data[sz * self.lenZ + sy * self.lenY + sx] += weight

	def add(self, a):
		if len(a.data) != len(self.data):
			raise TypeError

		data = self.data
		data2 = a.data
		for i in range(len(data)):
			data[i] += data2[i]

	def subtract(self, a):
		if len(a.data) != len(self.data):
			raise TypeError

		data = self.data
		data2 = a.data
		for i in range(len(data)):
			data[i] -= data2[i]

	def multiply(self, a):
		if len(a.data) != len(self.data):
			raise TypeError

		data = self.data
		data2 = a.data
		for i in range(len(data)):
			data[i] *= data2[i]

	def multiplySquared(self, a):
		if len(a.data) != len(self.data):
			raise TypeError

		data = self.data
		data2 = a.data
		for i in range(len(data)):
			data[i] *= data2[i]**2
