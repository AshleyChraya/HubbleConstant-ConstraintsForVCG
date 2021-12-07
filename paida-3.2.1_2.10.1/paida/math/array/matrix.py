from paida.paida_core.PAbsorber import *
from paida.math.pylapack.dgesv import dgesv

from types import SliceType, TupleType, ListType
from os import linesep
from math import sqrt, hypot
import copy

class matrix:
	def __init__(self, data = None, link = False):
		self.link = link
		if hasattr(data, '__iter__'):
			if not hasattr(data[0], '__iter__'):
				data = [data]
			self._indicesR = range(len(data))
			self._indicesC = range(len(data[0]))
			self.data = copy.deepcopy(data)

	def _createCopyLinked(self, indicesR, indicesC):
		result = matrix(link = True)
		result.data = self.data
		result._indicesR = indicesR[:]
		result._indicesC = indicesC[:]
		return result

	def _createCopyUnlinked(self, indicesR, indicesC):
		result = []
		data = self.data
		for i in indicesR:
			result1 = []
			dataR = data[i]
			for j in indicesC:
				result1.append(dataR[j])
			result.append(result1)
		return matrix(data = result)

	def _format(self, data):
		return `data`

	def __str__(self):
		if len(self._indicesR) == 1:
			dataR = self.data[self._indicesR[0]]
			result = '['
			for j in self._indicesC:
				result += self._format(dataR[j]) + ', '
			result = result[:-2] + ']'
		elif len(self._indicesC) == 1:
			j = self._indicesC[0]
			data = self.data
			result = '['
			for i in self._indicesR:
				result += self._format(data[i][j]) + ','+ linesep
			result = result[:-2] + ']'
		else:
			data = self.data
			result = '[['
			for i in self._indicesR:
				for j in self._indicesC:
					result += self._format(data[i][j]) + ', '
				result = result[:-2] + '],' + linesep + ' ['
			result = result[:-4] + ']'
		return result

	__repr__ = __str__

	def __eq__(self, item):
		if isinstance(item, matrix):
			return self.toList() == item.toList()
		elif hasattr(item, '__iter__'):
			if hasattr(item[0], '__iter__'):
				return self.toList() == item
			else:
				raise RuntimeError
		else:
			raise RuntimeError

	def __len__(self):
		if self.nRows() == 1:
			return self.nColumns()
		elif self.nColumns() == 1:
			return self.nRows()
		else:
			return self.nRows()

	def __getitem__(self, request):
		indicesR = self._indicesR
		indicesC = self._indicesC

		if isinstance(request, SliceType):
			sliceFlag = True

			if request.start == None:
				start = 0
			else:
				start = request.start
			if request.stop == None:
				stop = len(indicesR)
			else:
				stop = min(request.stop, len(indicesR))

			if len(indicesR) == 1:
				newIndicesR = indicesR[:]
				newIndicesC = []
				for j in indicesC[start:stop:request.step]:
					newIndicesC.append(j)
			elif len(indicesC) == 1:
				newIndicesR = []
				newIndicesC = indicesC[:]
				for i in indicesR[start:stop:request.step]:
					newIndicesR.append(i)
			else:
				newIndicesR = []
				newIndicesC = indicesC[:]
				for i in indicesR[start:stop:request.step]:
					newIndicesR.append(i)

		elif isinstance(request, TupleType):
			requestR, requestC = request

			if type(requestR) == SliceType:
				sliceFlag = True

				if requestR.start == None:
					startR = 0
				else:
					startR = requestR.start
				if requestR.stop == None:
					stopR= len(indicesR)
				else:
					stopR = min(requestR.stop, len(indicesR))

				newIndicesR = []
				for i in indicesR[startR:stopR:requestR.step]:
					newIndicesR.append(i)

				if type(requestC) == SliceType:
					if requestC.start == None:
						startC = 0
					else:
						startC = requestC.start
					if requestC.stop == None:
						stopC = len(indicesC)
					else:
						stopC = min(requestC.stop, len(indicesC))

					newIndicesC = []
					for j in indicesC[startC:stopC:requestC.step]:
						newIndicesC.append(j)

				else:
					newIndicesC = [indicesC[requestC]]

			else:
				newIndicesR = [indicesR[requestR]]

				if type(requestC) == SliceType:
					sliceFlag = True

					if requestC.start == None:
						startC = 0
					else:
						startC = requestC.start
					if requestC.stop == None:
						stopC = len(indicesC)
					else:
						stopC = min(requestC.stop, len(indicesC))

					newIndicesC = []
					for j in indicesC[startC:stopC:requestC.step]:
						newIndicesC.append(j)

				else:
					sliceFlag = False
					newIndicesC = [indicesC[requestC]]

		else:
			sliceFlag = False
			if len(indicesR) == 1:
				newIndicesR = indicesR[:]
				newIndicesC = [indicesC[request]]
			elif len(indicesC) == 1:
				newIndicesR = [indicesR[request]]
				newIndicesC = indicesC[:]
			else:
				newIndicesR = [indicesR[request]]
				newIndicesC = indicesC[:]

		if (sliceFlag == False) and (len(newIndicesR) == 1) and (len(newIndicesC) == 1):
			return self.data[newIndicesR[0]][newIndicesC[0]]
		elif self.link:
			return self._createCopyLinked(newIndicesR, newIndicesC)
		else:
			return self._createCopyUnlinked(newIndicesR, newIndicesC)

	def __setitem__(self, request, item):
		data = self.data
		indicesR = self._indicesR
		indicesC = self._indicesC

		if isinstance(request, SliceType):
			if request.start == None:
				start = 0
			else:
				start = request.start
			if request.stop == None:
				stop = len(indicesR)
			else:
				stop = min(request.stop, len(indicesR))

			if len(indicesR) == 1:
				dataR = data[indicesR[0]]
				for m, j in enumerate(indicesC[start:stop:request.step]):
					dataR[j] = item[m]
			elif len(indicesC) == 1:
				j = indicesC[0]
				for m, i in enumerate(indicesR[start:stop:request.step]):
					data[i][j] = item[m]
			else:
				for m, i in enumerate(indicesR[start:stop:request.step]):
					dataR = data[i]
					itemR = item[m]
					for n, j in enumerate(indicesC):
						dataR[j] = itemR[n]

		elif isinstance(request, TupleType):
			requestR, requestC = request
			indicesR = self._indicesR
			indicesC = self._indicesC

			if type(requestR) == SliceType:
				if requestR.start == None:
					startR = 0
				else:
					startR = requestR.start
				if requestR.stop == None:
					stopR= len(indicesR)
				else:
					stopR = min(requestR.stop, len(indicesR))

				if type(requestC) == SliceType:
					if requestC.start == None:
						startC = 0
					else:
						startC = requestC.start
					if requestC.stop == None:
						stopC = len(indicesC)
					else:
						stopC = min(requestC.stop, len(indicesC))

					for m, i in enumerate(indicesR[startR:stopR:requestR.step]):
						dataR = data[i]
						itemR = item[m]
						for n, j in enumerate(indicesC[startC:stopC:requestC.step]):
							dataR[j] = itemR[n]

				else:
					j = indicesC[requestC]
					for m, i in enumerate(indicesR[startR:stopR:requestR.step]):
						data[i][j] = item[m]

			else:
				if type(requestC) == SliceType:
					if requestC.start == None:
						startC = 0
					else:
						startC = requestC.start
					if requestC.stop == None:
						stopC = len(indicesC)
					else:
						stopC = min(requestC.stop, len(indicesC))

					dataR = data[indicesR[requestR]]
					for n, j in enumerate(indicesC[startC:stopC:requestC.step]):
						dataR[j]  = item[n]

				else:
					data[indicesR[requestR]][indicesC[requestC]] = item

		else:
			if len(indicesR) == 1:
				data[indicesR[0]][indicesC[request]] = item
			elif len(indicesC) == 1:
				data[indicesR[request]][indicesC[0]] = item
			else:
				dataR = data[indicesR[request]]
				for n, j in enumerate(indicesC):
					dataR[j] = item[n]

	def __add__(self, item):
		result = []
		data = self.data
		if isinstance(item, matrix):
			indicesR = self._indicesR
			indicesC = self._indicesC
			if item.nRows() == 1:
				### matrix + vector
				for m, i in enumerate(indicesR):
					result1 = []
					dataR = data[i]
					for n, j in enumerate(indicesC):
						result1.append(dataR[j] + item[n])
					result.append(result1)
			elif item.nColumns() == 1:
				### matrix + vector
				for m, i in enumerate(indicesR):
					result1 = []
					itemM = item[m]
					for n, j in enumerate(indicesC):
						result1.append(data[i][j] + itemM)
					result.append(result1)
			else:
				### matrix + matrix
				for m, i in enumerate(indicesR):
					result1 = []
					dataR = data[i]
					itemR = item[m]
					for n, j in enumerate(indicesC):
						result1.append(dataR[j] + itemR[n])
					result.append(result1)
		elif hasattr(item, '__iter__'):
			if hasattr(item[0], '__iter__'):
				return self.__add__(matrix(item))
			else:
				raise RuntimeError
		else:
			### matrix + value
			indicesR = self._indicesR
			indicesC = self._indicesC
			for m, i in enumerate(indicesR):
				result1 = []
				dataR = data[i]
				for n, j in enumerate(indicesC):
					result1.append(dataR[j] + item)
				result.append(result1)
		return matrix(result, link = self.link)

	def __radd__(self, item):
		if isinstance(item, matrix):
			return item.__add__(self)
		elif hasattr(item, '__iter__'):
			if hasattr(item[0], '__iter__'):
				return matrix(item).__add__(self)
			else:
				raise RuntimeError
		else:
			result = self.__add__(item)
			result.link = False
			return result

	def __sub__(self, item):
		result = []
		data = self.data
		if isinstance(item, matrix):
			indicesR = self._indicesR
			indicesC = self._indicesC
			if item.nRows() == 1:
				### matrix - vector
				for m, i in enumerate(indicesR):
					result1 = []
					dataR = data[i]
					for n, j in enumerate(indicesC):
						result1.append(dataR[j] - item[n])
					result.append(result1)
			elif item.nColumns() == 1:
				### matrix - vector
				for m, i in enumerate(indicesR):
					result1 = []
					itemM = item[m]
					for n, j in enumerate(indicesC):
						result1.append(data[i][j] - itemM)
					result.append(result1)
			else:
				### matrix - matrix
				for m, i in enumerate(indicesR):
					result1 = []
					dataR = data[i]
					itemR = item[m]
					for n, j in enumerate(indicesC):
						result1.append(dataR[j] - itemR[n])
					result.append(result1)
		elif hasattr(item, '__iter__'):
			if hasattr(item[0], '__iter__'):
				return self.__sub__(matrix(item))
			else:
				raise RuntimeError
		else:
			### matrix - value
			indicesR = self._indicesR
			indicesC = self._indicesC
			for m, i in enumerate(indicesR):
				result1 = []
				dataR = data[i]
				for n, j in enumerate(indicesC):
					result1.append(dataR[j] - item)
				result.append(result1)
		return matrix(result, link = self.link)

	def __rsub__(self, item):
		if isinstance(item, matrix):
			return item.__sub__(self)
		elif hasattr(item, '__iter__'):
			if hasattr(item[0], '__iter__'):
				return matrix(item).__sub__(self)
			else:
				raise RuntimeError
		else:
			result = self.__sub__(item)
			result.link = False
			return result

	def __mul__(self, item):
		result = []
		data = self.data
		if isinstance(item, matrix):
			indicesR = self._indicesR
			indicesC = self._indicesC
			itemIndicesC = item._indicesC
			for i, a in enumerate(indicesR):
				result1 = []
				for j, b in enumerate(itemIndicesC):
					result2 = 0.0
					for k, c in enumerate(indicesC):
						result2 += data[a][c] * item[k, j]
					result1.append(result2)
				result.append(result1)
		elif hasattr(item, '__iter__'):
			if hasattr(item[0], '__iter__'):
				return self.__mul__(matrix(item))
			else:
				item1 = []
				for value in item:
					item1.append([value])
				return self.__mul__(matrix(item1))
		else:
			indicesR = self._indicesR
			indicesC = self._indicesC
			for m, i in enumerate(indicesR):
				result1 = []
				dataR = data[i]
				for n, j in enumerate(indicesC):
					result1.append(dataR[j] * item)
				result.append(result1)

		return matrix(result, link = self.link)

	def __rmul__(self, item):
		if isinstance(item, matrix):
			return item.__mul__(self)
		elif hasattr(item, '__iter__'):
			if hasattr(item[0], '__iter__'):
				return matrix(item).__mul__(self)
			else:
				return matrix([item]).__mul__(self)
		else:
			result = self.__mul__(item)
			result.link = False
			return result

	def nRows(self):
		return len(self._indicesR)

	def nColumns(self):
		return len(self._indicesC)

	def toList(self):
		if len(self._indicesR) == 1:
			dataR = self.data[self._indicesR[0]]
			result = []
			for j in self._indicesC:
				result.append(dataR[j])
		elif len(self._indicesC) == 1:
			j = self._indicesC[0]
			data = self.data
			result = []
			for i in self._indicesR:
				result.append(data[i][j])
		else:
			data = self.data
			result = []
			for i in self._indicesR:
				result2 = []
				for j in self._indicesC:
					result2.append(data[i][j])
				result.append(result2)
		return result

	def setLink(self, boolean):
		self.link = bool(boolean)

	def inverse(self):
		dimR = self.nRows()
		dimC = self.nColumns()
		if dimR != dimC:
			raise RuntimeError('nRows != nColumns')
		temp = []
		for i in range(dimR):
			temp.append([0.0] * dimR)
		for i in range(dimR):
			temp[i][i] = 1.0
		b = matrix(temp, link = True)
		ipiv = [0] * dimR
		info = [0]
		a = self._createCopyUnlinked(self._indicesR, self._indicesC)
		a.setLink(True)
		dgesv(dimR, dimR, a, None, ipiv, b, None, info)
		if info[0] != 0:
			if self.determinant() == 0:
				raise RuntimeError('Determinant is zero')
			else:
				raise RuntimeError('Failed to get inverse')
		if self.link:
			return b
		else:
			return b._createCopyUnlinked(b._indicesR, b._indicesC)

	def transpose(self):
		result = []
		data = self.data
		for j in self._indicesC:
			result1 = []
			for i in self._indicesR:
				result1.append(data[i][j])
			result.append(result1)
		return matrix(result, self.link)

	def determinant(self):
		if self.nRows() == 1:
			return self.__getitem__((0, 0))
		else:
			result = 0.0
			getterItem = self.__getitem__
			getterCofactor = self.cofactor
			for i in range(self.nRows()):
				result += (-1)**i * getterItem((i, 0)) * getterCofactor(i, 0)
			return result

	def cofactor(self, i, j):
		indicesR = self._indicesR[:]
		indicesC = self._indicesC[:]
		indicesR.remove(indicesR[i])
		indicesC.remove(indicesC[j])
		return self._createCopyLinked(indicesR, indicesC).determinant()

	def eigenvalues(self):
		"""This is based on EigenvalueDecomposition.java in JAMA."""
		n = self.nColumns()
		d = [0.0] * n
		e = [0.0] * n

		issymmetric = True
		for j in range(n):
			if issymmetric:
				for i in range(n):
					if issymmetric:
						issymmetric = (self[i, j] == self[j, i])
					else:
						break
			else:
				break

		if (issymmetric):
			V = self._createCopyUnlinked(self._indicesR, self._indicesC)

			d, e, V = self._tred2(d, e, V)
			d, e, V = self._tql2(d, e, V)
		else:
			tempMatrix = []
			for i in range(n):
				tempMatrix.append([0.0] * n)
			V = matrix(tempMatrix)
			H = self._createCopyUnlinked(self._indicesR, self._indicesC)
			ort = [0.0] * n

			V, H, ort = self._orthes(V, H, ort)
			d, e, V, H = self._hqr2(d, e, V, H)

		eigenvalues = zip(d, e)
		eigenvectors = []
		for j in range(n):
			eigenvector = []
			for i in range(n):
				eigenvector.append(V[i, j])
			eigenvectors.append(eigenvector)

		return eigenvalues, eigenvectors

	def _tred2(self, d, e, V):
		"""This is based on EigenvalueDecomposition.java in JAMA.
		Symmetric Householder reduction to tridiagonal form.
		"""
		n = self.nColumns()

		for j in range(n):
			d[j] = V[n - 1, j]

		for i in range(n - 1, 0, -1):
			scale = 0.0
			h = 0.0
			for k in range(i):
				scale += abs(d[k])
			if (scale == 0.0):
				e[i] = d[i - 1]
				for j in range(i):
					d[j] = V[i - 1, j]
					V[i, j] = 0.0
					V[j, i] = 0.0
			else:
				for k in range(i):
					d[k] /= scale
					h += d[k]**2
				f = d[i - 1]
				g = sqrt(h)
				if (f > 0):
					g = -g
				e[i] = scale * g
				h -= f * g
				d[i - 1] = f - g
				for j in range(i):
					e[j] = 0.0

				for j in range(i):
					f = d[j]
					V[j, i] = f
					g = e[j] + V[j, j] * f
					for k in range(j + 1, i):
						g += V[k, j] * d[k]
						e[k] += V[k, j] * f
					e[j] = g
				f = 0.0
				for j in range(i):
					e[j] /= h
					f += e[j] * d[j]
				hh = f / h / 2.0
				for j in range(i):
					e[j] -= hh * d[j]
				for j in range(i):
					f = d[j]
					g = e[j]
					for k in range(j, i):
						V[k, j] -= (f * e[k] + g * d[k])
					d[j] = V[i - 1, j]
					V[i, j] = 0.0
			d[i] = h

		for i in range(n - 1):
			V[n - 1, i] = V[i, i]
			V[i, i] = 1.0
			h = d[i + 1]
			if (h != 0.0):
				for k in range(i + 1):
					d[k] = V[k, i + 1] / h
				for j in range(i + 1):
					g = 0.0
					for k in range(i + 1):
						g += V[k, i + 1] * V[k, j]
					for k in range(i + 1):
						V[k, j] -= g * d[k]
			for k in range(i + 1):
				V[k, i + 1] = 0.0
		for j in range(n):
			d[j] = V[n - 1, j]
			V[n - 1, j] = 0.0
		V[n - 1, n - 1] = 1.0
		e[0] = 0.0

		return d, e, V

	def _tql2(self, d, e, V):
		"""This is based on EigenvalueDecomposition.java in JAMA.
		Symmetric tridiagonal QL algorithm.
		"""
		n = self.nColumns()

		for i in range(1, n):
			e[i - 1] = e[i]
		e[n - 1] = 0.0

		f = 0.0
		tst1 = 0.0
		eps = pow(2.0, -52.0)
		for l in range(n):
			tst1 = max(tst1, abs(d[l]) + abs(e[l]))
			m = l
			eps_tst1 = eps * tst1
			while (m < n):
				if (abs(e[m]) <= eps_tst1):
					break
				m += 1

			if (m > l):
				iter = 0
				loopFlag = True
				while loopFlag:
					iter += 1;

					g = d[l]
					p = (d[l + 1] - g) / (2.0 * e[l])
					r = hypot(p, 1.0)
					if (p < 0):
						r = -r
					d[l] = e[l] / (p + r)
					d[l + 1] = e[l] * (p + r)
					dl1 = d[l + 1]
					h = g - d[l]
					for i in range(l + 2, n):
						d[i] -= h
					f += h

					p = d[m]
					c = 1.0
					c2 = c
					c3 = c
					el1 = e[l + 1]
					s = 0.0
					s2 = 0.0
					for i in range(m - 1, l - 1, -1):
						c3 = c2
						c2 = c
						s2 = s
						g = c * e[i]
						h = c * p
						r = hypot(p, e[i])
						e[i + 1] = s * r
						s = e[i] / r
						c = p / r
						p = c * d[i] - s * g
						d[i + 1] = h + s * (c * g + s * d[i])

						for k in range(n):
							h = V[k, i + 1]
							V[k, i + 1] = s * V[k, i] + c * h
							V[k, i] = c * V[k, i] - s * h
					p = -s * s2 * c3 * el1 * e[l] / dl1
					e[l] = s * p
					d[l] = c * p

					if abs(e[l]) <= eps_tst1:
						loopFlag = False

			d[l] += f
			e[l] = 0.0 

		for i in range(n - 1):
			k = i
			p = d[i]
			for j in range(i + 1, n):
				if (d[j] < p):
					k = j
					p = d[j]
			if (k != i):
				d[k] = d[i]
				d[i] = p
				for j in range(n):
					p = V[j, i]
					V[j, i] = V[j, k]
					V[j, k] = p

		return d, e, V

	def _orthes(self, V, H, ort):
		"""This is based on EigenvalueDecomposition.java in JAMA.
		Nonsymmetric reduction to Hessenberg form.
		"""
		n = self.nColumns()

		low = 0
		high = n - 1

		for m in range(low + 1, high):
			scale = 0.0
			for i in range(m, high + 1):
				scale += abs(H[i, m-1])
			if (scale != 0.0):
				h = 0.0
				for i in range(high, m - 1, -1):
					ort[i] = H[i, m - 1] / scale
					h += ort[i]**2
				g = sqrt(h)
				if (ort[m] > 0):
					g = -g
				h -= ort[m] * g
				ort[m] -= g

				for j in range(m, n):
					f = 0.0
					for i in range(high, m - 1, -1):
						f += ort[i] * H[i, j]
					f /= h
					for i in range(m, high + 1):
						H[i, j] -= f * ort[i]

				for i in range(high + 1):
					f = 0.0
					for j in range(high, m - 1, -1):
						f += ort[j] * H[i, j]
					f /= h
					for j in range(m, high + 1):
						H[i, j] -= f * ort[j]
				ort[m] *= scale
				H[m, m - 1] = scale * g

		for i in range(n):
			for j in range(n):
				if i == j:
					V[i, j] = 1.0
				else:
					V[i, j] = 0.0

		for m in range(high - 1, low, -1):
			if (H[m, m - 1] != 0.0):
				for i in range(m + 1, high + 1):
					ort[i] = H[i, m - 1]
				for j in range(m, high + 1):
					g = 0.0
					for i in range(m, high + 1):
						g += ort[i] * V[i, j]
					g /= (ort[m] * H[m, m - 1])
					for i in range(m, high + 1):
						V[i, j] += g * ort[i]

		return V, H, ort

	def _hqr2(self, d, e, V, H):
		"""This is based on EigenvalueDecomposition.java in JAMA.
		Nonsymmetric reduction from Hessenberg to real Schur form.
		"""

		nn = self.nColumns()
		n = nn - 1
		low = 0
		high = n
		eps = pow(2.0, -52.0)
		exshift = 0.0
		p=0
		q=0
		r=0
		s=0
		z=0

		norm = 0.0
		for i in range(nn):
			if (i < low or i > high):
				d[i] = H[i, i]
				e[i] = 0.0
			for j in range(max(i - 1, 0), nn):
				norm += abs(H[i, j])

		iter = 0
		while (n >= low):
			l = n
			while (l > low):
				s = abs(H[l - 1, l - 1]) + abs(H[l, l])
				if (s == 0.0):
					s = norm
				if (abs(H[l, l - 1]) < eps * s):
					break
				l -= 1

			if (l == n):
				H[n, n] += exshift
				d[n] = H[n, n]
				e[n] = 0.0
				n -= 1
				iter = 0
			elif (l == n - 1):
				w = H[n, n - 1] * H[n - 1, n]
				p = (H[n - 1, n - 1] - H[n, n]) / 2.0
				q = p * p + w
				z = sqrt(abs(q))
				H[n, n] += exshift
				H[n - 1, n - 1] += exshift
				x = H[n, n]

				if (q >= 0):
					if (p >= 0):
						z = p + z
					else:
						z = p - z
					d[n - 1] = x + z
					d[n] = d[n - 1]
					if (z != 0.0):
						d[n] = x - w / z
					e[n - 1] = 0.0
					e[n] = 0.0
					x = H[n, n - 1]
					s = abs(x) + abs(z)
					p = x / s
					q = z / s
					r = sqrt(p**2 + q**2)
					p /= r
					q /= r

					for j in range(n - 1, nn):
						z = H[n - 1, j]
						H[n - 1, j] = q * z + p * H[n, j]
						H[n, j] = q * H[n, j] - p * z

					for i in range(n + 1):
						z = H[i, n - 1]
						H[i, n - 1] = q * z + p * H[i, n]
						H[i, n] = q * H[i, n] - p * z

					for i in range(low, high + 1):
						z = V[i, n - 1]
						V[i, n - 1] = q * z + p * V[i, n]
						V[i, n] = q * V[i, n] - p * z

				else:
					d[n - 1] = x + p
					d[n] = x + p
					e[n - 1] = z
					e[n] = -z
				n -= 2
				iter = 0
			else:
				x = H[n, n]
				y = 0.0
				w = 0.0
				if (l < n):
					y = H[n - 1, n - 1]
					w = H[n, n - 1] * H[n - 1, n]

				if (iter == 10):
					exshift += x
					for i in range(low, n + 1):
						H[i, i] -= x
					s = abs(H[n, n - 1]) + abs(H[n - 1, n-2])
					x = y = 0.75 * s
					w = -0.4375 * s * s

				if (iter == 30):
					s = (y - x) / 2.0
					s = s * s + w
					if (s > 0):
						s = sqrt(s)
						if (y < x):
							s = -s
						s = x - w / ((y - x) / 2.0 + s)
						for i in range(low, n + 1):
							H[i, i] -= s
						exshift += s
						x = y = w = 0.964

				iter += 1

				m = n - 2
				while (m >= l):
					z = H[m, m]
					r = x - z
					s = y - z
					p = (r * s - w) / H[m + 1, m] + H[m, m + 1]
					q = H[m + 1, m + 1] - z - r - s
					r = H[m + 2, m + 1]
					s = abs(p) + abs(q) + abs(r)
					p /= s
					q /= s
					r /= s
					if (m == l):
						break
					if (abs(H[m, m - 1]) * (abs(q) + abs(r)) < eps * (abs(p) * (abs(H[m - 1, m - 1]) + abs(z) + abs(H[m + 1, m + 1])))):
							break
					m -= 1

				for i in range(m + 2, n + 1):
					H[i, i - 2] = 0.0
					if (i > m + 2):
						H[i, i - 3] = 0.0

				for k in range(m, n):
					notlast = (k != n - 1)
					if (k != m):
						p = H[k, k - 1]
						q = H[k + 1, k - 1]
						if notlast:
							r = H[k + 2, k - 1]
						else:
							r = 0.0
						x = abs(p) + abs(q) + abs(r)
						if (x != 0.0):
							p /= x
							q /= x
							r /= x
					if (x == 0.0):
						break
					s = sqrt(p * p + q * q + r * r)
					if (p < 0):
						s = -s
					if (s != 0):
						if (k != m):
							H[k, k - 1] = -s * x
						elif (l != m):
							H[k, k - 1] *= -1
						p += s
						x = p / s
						y = q / s
						z = r / s
						q /= p
						r /= p

						for j in range(k, nn):
							p = H[k, j] + q * H[k + 1, j]
							if (notlast):
								p += r * H[k + 2, j]
								H[k + 2, j] -= p * z
							H[k, j] -= p * x
							H[k + 1, j] -= p * y

						for i in range(min(n,k + 3) + 1):
							p = x * H[i, k] + y * H[i, k + 1]
							if (notlast):
								p += z * H[i, k + 2]
								H[i, k + 2] -= p * r
							H[i, k] -= p
							H[i, k + 1] -= p * q

						for i in range(low, high + 1):
							p = x * V[i, k] + y * V[i, k + 1]
							if (notlast):
								p += z * V[i, k + 2]
								V[i, k + 2] -= p * r
							V[i, k] -= p
							V[i, k + 1] -= p * q

		if (norm == 0.0):
			return

		_cdiv = self._cdiv
		for n in range(nn - 1, -1, -1):
			p = d[n]
			q = e[n]

			if (q == 0):
				l = n
				H[n, n] = 1.0
				for i in range(n - 1, -1, -1):
					w = H[i, i] - p
					r = 0.0
					for j in range(l, n + 1):
						r += H[i, j] * H[j, n]
					if (e[i] < 0.0):
						z = w
						s = r
					else:
						l = i
						if (e[i] == 0.0):
							if (w != 0.0):
								H[i, n] = -r / w
							else:
								H[i, n] = -r / (eps * norm)
						else:
							x = H[i, i + 1]
							y = H[i + 1, i]
							q = (d[i] - p) * (d[i] - p) + e[i]**2
							t = (x * s - z * r) / q
							H[i, n] = t
							if (abs(x) > abs(z)):
								H[i + 1, n] = (-r - w * t) / x
							else:
								H[i + 1, n] = (-s - y * t) / z

						t = abs(H[i, n])
						if ((eps * t) * t > 1):
							for j in range(i, n + 1):
								H[j, n] /= t
			elif (q < 0):
				l = n - 1

				if (abs(H[n, n - 1]) > abs(H[n - 1, n])):
					H[n - 1, n - 1] = q / H[n, n - 1]
					H[n - 1, n] = -(H[n, n] - p) / H[n, n - 1]
				else:
					cdivr, cdivi = _cdiv(0.0, -H[n - 1, n], H[n - 1, n - 1] - p, q)
					H[n - 1, n - 1] = cdivr
					H[n - 1, n] = cdivi
				H[n, n - 1] = 0.0
				H[n, n] = 1.0
				for i in range(n - 2, -1, -1):
					ra = 0.0
					sa = 0.0
					for j in range(l, n + 1):
						ra += H[i, j] * H[j, n - 1]
						sa += H[i, j] * H[j, n]
					w = H[i, i] - p

					if (e[i] < 0.0):
						z = w
						r = ra
						s = sa
					else:
						l = i
						if (e[i] == 0):
							cdivr, cdivi = _cdiv(-ra, -sa, w, q)
							H[i, n - 1] = cdivr
							H[i, n] = cdivi
						else:
							x = H[i, i + 1]
							y = H[i + 1, i]
							vr = (d[i] - p) * (d[i] - p) + e[i]**2 - q * q
							vi = (d[i] - p) * 2.0 * q
							if (vr == 0.0 and vi == 0.0):
								vr = eps * norm * (abs(w) + abs(q) + abs(x) + abs(y) + abs(z))
							cdivr, cdivi = _cdiv(x * r - z * ra + q * sa, x * s - z * sa - q * ra, vr, vi)
							H[i, n - 1] = cdivr
							H[i, n] = cdivi
							if (abs(x) > (abs(z) + abs(q))):
								H[i + 1, n - 1] = (-ra - w * H[i, n - 1] + q * H[i, n]) / x
								H[i + 1, n] = (-sa - w * H[i, n] - q * H[i, n - 1]) / x
							else:
								cdivr, cdivi = _cdiv(-r - y * H[i, n - 1], -s - y * H[i, n], z, q)
								H[i + 1, n - 1] = cdivr
								H[i + 1, n] = cdivi

						t = max(abs(H[i, n - 1]), abs(H[i, n]))
						if ((eps * t) * t > 1):
							for j in range(i, n + 1):
								H[j, n - 1] /= t
								H[j, n] /= t

		for i in range(nn):
			if (i < low or i > high):
				for j in range(i, nn):
					V[i, j] = H[i, j]

		for j in range(nn - 1, low - 1, -1):
			for i in range(low, high + 1):
				z = 0.0
				for k in range(low, min(j, high) + 1):
					z += V[i, k] * H[k, j]
				V[i, j] = z

		### Normalization
		for j in range(nn):
			sum = 0.0
			for i in range(nn):
				sum += V[i, j]**2
			scale = sqrt(sum)
			for i in range(nn):
				V[i, j] /= scale

		return d, e, V, H

	def _cdiv(self, xr, xi, yr, yi):
		"""This is based on EigenvalueDecomposition.java in JAMA.
		Complex scalar division.
		"""
		if (abs(yr) > abs(yi)):
			r = yi / yr
			d = yr + r * yi
			cdivr = (xr + r * xi) / d
			cdivi = (xi - r * xr) / d
		else:
			r = yr / yi
			d = yi + r * yr
			cdivr = (r * xr + xi) / d
			cdivi = (r * xi - xr) / d
		return cdivr, cdivi
