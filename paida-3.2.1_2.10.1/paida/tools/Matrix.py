"""Matrix tool module.

Usage:

from paida.tools import Matrix
### Create 2*2 matrix.
result1 = Matrix.create([[1.0, 2.0], [3.0, 4.0]])
### Create 3*3 linked matrix.
result2 = Matrix.create([[1.0, 2.0, 3.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0]], link = True)
### Create 2*2 unit matrix.
result3 = Matrix.createUnit(2)
"""

from paida.math.array.matrix import matrix

def create(data, link = None):
	if link == None:
		return matrix(data)
	else:
		return matrix(data, link)

def createUnit(dimension, link = None):
	result = []
	for i in range(dimension):
		temp = [0.0] * dimension
		temp[i] = 1.0
		result.append(temp)
	return create(result, link)
