from paida.paida_core.PAbsorber import *
from paida.paida_core.IAnnotation import *

import math

class IFunction:
	_eps2 = 1.4901161193847656e-08
	_eps3 = 6.0554544523933479e-06
	_eps4 = 0.0001220703125

	def __init__(self, typeName, parentFactory, name, dimension, expression, deriv0, deriv1, deriv2, gradExpr, grad2Expr, parameterNames, innerNameSpace, description):
		self._annotation = IAnnotation()
		self._annotation.addItem('Title', description, True)

		self._parentFactory = parentFactory
		self._name = name
		self._dimension = dimension
		self._expression = expression
		self._gradExpr = gradExpr
		self._grad2Expr = grad2Expr
		self._parameterNames = parameterNames

		### Derivatives.
		self._deriv0 = deriv0
		self._deriv1 = deriv1
		self._deriv2 = deriv2

		self._innerParameterNameSpace = {}
		for i, parameterName in enumerate(parameterNames):
			self._innerParameterNameSpace[parameterName] = i + 1.0
		self._innerParameterNameSpace['_parameterNameSpace_'] = self._innerParameterNameSpace
		_xs = []
		for i in range(dimension):
			_xs.append(i + 1.0)
		self._innerParameterNameSpace['x'] = _xs

		self._innerNameSpace = innerNameSpace
		self._innerNameSpace['sin'] = math.sin
		self._innerNameSpace['cos'] = math.cos
		self._innerNameSpace['tan'] = math.tan
		self._innerNameSpace['exp'] = math.exp
		self._innerNameSpace['log'] = math.log
		self._innerNameSpace['pi'] = math.pi
		self._innerNameSpace['e'] = math.e
		self._compiledDeriv0 = compile(deriv0, 'IFunction.py', 'eval')
		if deriv1 == None:
			self._compiledDeriv1 = None
			self._getDeriv1 = self._getDeriv1From0
			self._getDeriv1Base = self._getDeriv1From0Base
		else:
			self._compiledDeriv1 = []
			for deriv1Item in deriv1:
				self._compiledDeriv1.append(compile(deriv1Item, 'IFunction.py', 'eval'))
			self._getDeriv1 = self._getDeriv1From1
			self._getDeriv1Base = self._getDeriv1From1Base
		if deriv2 == None:
			self._compiledDeriv2 = None
			self._getDeriv2 = self._getDeriv2From0
			self._getDeriv2Base = self._getDeriv2From0Base
		else:
			self._compiledDeriv2 = []
			for deriv2Items in deriv2:
				_compiledDeriv2i = []
				for deriv2Item in deriv2Items:
					_compiledDeriv2i.append(compile(deriv2Item, 'IFunction.py', 'eval'))
				self._compiledDeriv2.append(_compiledDeriv2i)
			self._getDeriv2 = self._getDeriv2From2
			self._getDeriv2Base = self._getDeriv2From2Base

		### Codelet.
		codeletList = ['codelet']
		if typeName == 'verbatim':
			codeletList.append(description)
			codeletList.append(typeName)
			codeletList.append('py')
			codeletList.append('%d' % dimension)
			codeletList.append(expression)
			codeletList.append(','.join(parameterNames))
			if gradExpr == None:
				codeletList.append('null')
			else:
				codeletList.append(gradExpr)
			if grad2Expr == None:
				#codeletList.append('null')
				pass
			else:
				codeletList.append(grad2Expr)
		elif typeName == 'catalog':
			codeletList.append(expression)
			codeletList.append('catalog')
		else:
			raise ValueError, 'Unknown typeName "%s".' % typeName
		self._codeletString = ':'.join(codeletList)

	def _getParentFactory(self):
		return self._parentFactory

	def _roundResult(self, result):
		return result
		if abs(result) < self._eps2:
			return 0.0
		else:
			return result

	def _getDeriv0Base(self, parameterNameSpace):
		return eval(self._compiledDeriv0, self._innerNameSpace, parameterNameSpace)

	def _getDeriv0(self, parameterNameSpace):
		return self._roundResult(self._getDeriv0Base(parameterNameSpace))

	def _getDeriv1From1Base(self, parameterNameSpace, parameterIndex):
		return eval(self._compiledDeriv1[parameterIndex], self._innerNameSpace, parameterNameSpace)

	def _getDeriv1From1(self, parameterNameSpace, parameterIndex):
		return self._roundResult(self._getDeriv1From1Base(parameterNameSpace, parameterIndex))

	def _getDeriv2From2Base(self, parameterNameSpace, parameterIndex1, parameterIndex2):
		return eval(self._compiledDeriv2[parameterIndex1][parameterIndex2], self._innerNameSpace, parameterNameSpace)

	def _getDeriv2From2(self, parameterNameSpace, parameterIndex1, parameterIndex2):
		return self._roundResult(self._getDeriv2From2Base(parameterNameSpace, parameterIndex1, parameterIndex2))

	def _getDeriv1From0Base(self, parameterNameSpace, parameterIndex):
		eps2 = self._eps2
		parameterName = self._parameterNames[parameterIndex]
		compiledDeriv0 = self._compiledDeriv0
		innerNameSpace = self._innerNameSpace
		current = parameterNameSpace[parameterName]

		parameterNameSpace[parameterName] += eps2
		fp = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
		parameterNameSpace[parameterName] = current - eps2
		fm = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
		result = (fp - fm) / 2.0 / eps2
		parameterNameSpace[parameterName] = current
		return result

	def _getDeriv1From0BaseConstrained(self, parameterNameSpace, parameterIndex, constraints):
		eps2 = self._eps2
		parameterName = self._parameterNames[parameterIndex]
		compiledDeriv0 = self._compiledDeriv0
		innerNameSpace = self._innerNameSpace
		currents = parameterNameSpace.copy()

		parameterNameSpace[parameterName] += eps2
		for constraint in constraints:
			### Jython2.1 doesn't understand exec(code, globals(), locals()) properly.
			#eval(constraint, _normalNameSpace, parameterNameSpace)
			exec constraint in innerNameSpace, parameterNameSpace
		fp = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
		parameterNameSpace.update(currents)
		parameterNameSpace[parameterName] -= eps2
		for constraint in constraints:
			exec constraint in innerNameSpace, parameterNameSpace
		fm = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
		result = (fp - fm) / 2.0 / eps2
		parameterNameSpace.update(currents)
		return result

	def _getDeriv1From0(self, parameterNameSpace, parameterIndex):
		return self._roundResult(self._getDeriv1From0Base(parameterNameSpace, parameterIndex))

	def _getDeriv2From0Base(self, parameterNameSpace, parameterIndex1, parameterIndex2):
		eps = self._eps3
		parameterName1 = self._parameterNames[parameterIndex1]
		parameterName2 = self._parameterNames[parameterIndex2]
		compiledDeriv0 = self._compiledDeriv0
		innerNameSpace = self._innerNameSpace
		current1 = parameterNameSpace[parameterName1]
		current2 = parameterNameSpace[parameterName2]

		if parameterIndex1 == parameterIndex2:
			fc = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace[parameterName1] += eps
			fp = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace[parameterName1] = current1 - eps
			fm = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			result = (fp + fm - 2.0 * fc) / eps**2
		else:
			parameterNameSpace[parameterName1] = current1 + eps
			parameterNameSpace[parameterName2] = current2 + eps
			fpp = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace[parameterName1] = current1 - eps
			parameterNameSpace[parameterName2] = current2 - eps
			fmm = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace[parameterName1] = current1 + eps
			parameterNameSpace[parameterName2] = current2 - eps
			fpm = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace[parameterName1] = current1 - eps
			parameterNameSpace[parameterName2] = current2 + eps
			fmp = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			result = (fpp + fmm - fpm - fmp) / eps**2 / 4.0

		parameterNameSpace[parameterName1] = current1
		parameterNameSpace[parameterName2] = current2
		return result

	def _getDeriv2From0BaseConstrained(self, parameterNameSpace, parameterIndex1, parameterIndex2, constraints):
		eps = self._eps3
		parameterName1 = self._parameterNames[parameterIndex1]
		parameterName2 = self._parameterNames[parameterIndex2]
		compiledDeriv0 = self._compiledDeriv0
		innerNameSpace = self._innerNameSpace
		currents = parameterNameSpace.copy()

		if parameterIndex1 == parameterIndex2:
			for constraint in constraints:
				exec constraint in innerNameSpace, parameterNameSpace
			fc = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace.update(currents)
			parameterNameSpace[parameterName1] += eps
			for constraint in constraints:
				exec constraint in innerNameSpace, parameterNameSpace
			fp = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace.update(currents)
			parameterNameSpace[parameterName1] -= eps
			for constraint in constraints:
				exec constraint in innerNameSpace, parameterNameSpace
			fm = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			result = (fp + fm - 2.0 * fc) / eps**2
		else:
			parameterNameSpace[parameterName1] += eps
			parameterNameSpace[parameterName2] += eps
			for constraint in constraints:
				exec constraint in innerNameSpace, parameterNameSpace
			fpp = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace.update(currents)
			parameterNameSpace[parameterName1] -= eps
			parameterNameSpace[parameterName2] -= eps
			for constraint in constraints:
				exec constraint in innerNameSpace, parameterNameSpace
			fmm = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace.update(currents)
			parameterNameSpace[parameterName1] += eps
			parameterNameSpace[parameterName2] -= eps
			for constraint in constraints:
				exec constraint in innerNameSpace, parameterNameSpace
			fpm = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			parameterNameSpace.update(currents)
			parameterNameSpace[parameterName1] -= eps
			parameterNameSpace[parameterName2] += eps
			for constraint in constraints:
				exec constraint in innerNameSpace, parameterNameSpace
			fmp = eval(compiledDeriv0, innerNameSpace, parameterNameSpace)
			result = (fpp + fmm - fpm - fmp) / eps**2 / 4.0

		parameterNameSpace.update(currents)
		return result

	def _getDeriv2From0(self, parameterNameSpace, parameterIndex1, parameterIndex2):
		return self._roundResult(self._getDeriv2From0Base(parameterNameSpace, parameterIndex1, parameterIndex2))

	def _setX(self, x):
		self._innerParameterNameSpace['x'] = x

	def value(self, x):
		self._setX(x)
		return self._getDeriv0(self._innerParameterNameSpace)

	def gradient(self, x):
		self._setX(x)
		result = []
		for i in range(self.numberOfParameters()):
			result.append(self._getDeriv1(self._innerParameterNameSpace, i))
		return result

	def _hessian(self, x):
		self._setX(x)
		result = []
		for i in range(self.numberOfParameters()):
			resulti = []
			for j in range(self.numberOfParameters()):
				resulti.append(self._getDeriv2(self._innerParameterNameSpace, i, j))
			result.append(resulti)
		return result

	def dimension(self):
		return self._dimension

	def isEqual(self, function):
		if self.codeletString() == function.codeletString():
			return True
		else:
			return False

	def providesGradient(self):
		if self._gradExpr == None:
			return False
		else:
			return True

	def variableName(self, i):
		return 'x[%s]' % i

	def variableNames(self):
		names = []
		for i in range(self._dimension):
			names.append(self.variableName(i))
		return names

	def setParameters(self, parameterValues):
		parameterNames = self._parameterNames
		parameterNameSpace = self._innerParameterNameSpace
		for i, parameterValue in enumerate(parameterValues):
			parameterNameSpace[parameterNames[i]] = parameterValue

	def setParameter(self, parameterName, parameterValue):
		self._innerParameterNameSpace[parameterName] = parameterValue

	def parameters(self):
		result = []
		parameterNameSpace = self._innerParameterNameSpace
		for parameterName in self._parameterNames:
			result.append(parameterNameSpace[parameterName])
		return result

	def parameter(self, parameterName):
		return self._innerParameterNameSpace[parameterName]

	def numberOfParameters(self):
		return len(self._parameterNames)

	def parameterNames(self):
		return self._parameterNames[:]

	def indexOfParameter(self, parameterName):
		return self._parameterNames.index(parameterName)

	def annotation(self):
		return self._annotation

	def codeletString(self):
		return self._codeletString
