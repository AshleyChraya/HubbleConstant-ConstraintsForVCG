from paida.paida_core.PAbsorber import *
from paida.paida_core.IFunctionCatalog import *
from paida.paida_core.IFunction import *
from paida.paida_core.PUtilities import _Shlex
from paida.paida_core.PExceptions import *

import os

class _EOFException(Exception):
	pass

class _ItemObject:
	_zeros = ['0.0', '-0.0', '(0.0)', '-(0.0)']

	def __init__(self, name0, name1):
		self._0 = name0
		self._1 = name1

	def __pos__(self):
		return _ItemObject(self._0, self._1)

	def __neg__(self):
		_0 = '-(%s)' % (self._0)
		_1 = '-(%s)' % (self._1)
		return _ItemObject(_0, _1)

	def __add__(self, other):
		_0 = '(%s + %s)' % (self._0, other._0)
		if self._1 in self._zeros:
			if other._1 in self._zeros:
				_1 = '0.0'
			else:
				_1 = '(%s)' % (other._1)
		else:
			if other._1 in self._zeros:
				_1 = '(%s)' % (self._1)
			else:
				_1 = '(%s + %s)' % (self._1, other._1)
		return _ItemObject(_0, _1)

	def __sub__(self, other):
		_0 = '(%s - %s)' % (self._0, other._0)
		if self._1 in self._zeros:
			if other._1 in self._zeros:
				_1 = '0.0'
			else:
				_1 = '-(%s)' % (other._1)
		else:
			if other._1 in self._zeros:
				_1 = '(%s)' % (self._1)
			else:
				_1 = '(%s - %s)' % (self._1, other._1)
		return _ItemObject(_0, _1)

	def __mul__(self, other):
		_0 = '(%s * %s)' % (self._0, other._0)
		if self._1 in self._zeros:
			if other._1 in self._zeros:
				_1 = '0.0'
			else:
				_1 = '(%s * %s)' % (self._0, other._1)
		else:
			if other._1 in self._zeros:
				_1 = '(%s * %s)' % (self._1, other._0)
			else:
				_1 = '(%s * %s + %s * %s)' % (self._1, other._0, self._0, other._1)
		return _ItemObject(_0, _1)

	def __div__(self, other):
		_0 = '(%s / %s)' % (self._0, other._0)
		if self._1 in self._zeros:
			if other._1 in self._zeros:
				_1 = '0.0'
			else:
				_1 = '(-(%s * %s) / (%s)**2)' % (self._0, other._1, other._0)
		else:
			if other._1 in self._zeros:
				_1 = '(%s / %s)' % (self._1, other._0)
			else:
				_1 = '(%s / %s - %s * %s / (%s)**2)' % (self._1, other._0, self._0, other._1, other._0)
		return _ItemObject(_0, _1)

	def __pow__(self, other):
		_0 = '(%(s0)s**%(o0)s)' % {'s0': self._0, 'o0': other._0}
		if self._1 in self._zeros:
			if other._1 in self._zeros:
				_1 = '0.0'
			else:
				_1 = '(%(s0)s**%(o0)s * log(%(s0)s) * %(o1)s)' % {'s0': self._0, 's1': self._1, 'o0': other._0, 'o1': other._1}
		else:
			if other._1 in self._zeros:
				_1 = '(%(o0)s * %(s0)s**(%(o0)s - 1) * %(s1)s)' % {'s0': self._0, 's1': self._1, 'o0': other._0, 'o1': other._1}
			else:
				_1 = '(%(s0)s**%(o0)s * log(%(s0)s) * %(o1)s + %(o0)s * %(s0)s**(%(o0)s - 1) * %(s1)s)' % {'s0': self._0, 's1': self._1, 'o0': other._0, 'o1': other._1}
		return _ItemObject(_0, _1)

class IFunctionFactory:
	_zeros = ['0.0', '-0.0', '(0.0)', '-(0.0)']

	def __init__(self, tree):
		self._tree = tree

		### Make a catalog.
		self._catalog = IFunctionCatalog()

		### Predefined gaussian.
		G = self.createFunctionFromScript('G',
		1,
		'amplitude * exp(-0.5 * ((x[0] - mean) / sigma)**2)',
		'amplitude,mean,sigma',
		'Gaussian',
		gradExpr = ','.join(['exp(-0.5 * ((x[0] - mean) / sigma)**2)',
			'amplitude * exp(-0.5 * ((x[0] - mean) / sigma)**2) * (x[0] - mean) / sigma**2',
			'amplitude * exp(-0.5 * ((x[0] - mean) / sigma)**2) * (x[0] - mean)**2 / sigma**3']),
		grad2Expr = ','.join(['0.0',
			'exp(-0.5 * ((x[0] - mean) / sigma)**2) * (x[0] - mean) / sigma**2',
			'exp(-0.5 * ((x[0] - mean) / sigma)**2) * (x[0] - mean)**2 / sigma**3',
			'exp(-0.5 * ((x[0] - mean) / sigma)**2) * (x[0] - mean) / sigma**2',
			'amplitude * exp(-0.5 * ((x[0] - mean) / sigma)**2) * (((x[0] - mean) / sigma)**2 - 1.0) / sigma**2',
			'amplitude * exp(-0.5 * ((x[0] - mean) / sigma)**2) * ((x[0] - mean)**3 / sigma**5 - 2.0 * (x[0] - mean) / sigma**3)',
			'exp(-0.5 * ((x[0] - mean) / sigma)**2) * (x[0] - mean)**2 / sigma**3',
			'amplitude * exp(-0.5 * ((x[0] - mean) / sigma)**2) * ((x[0] - mean)**3 / sigma**5 - 2.0 * (x[0] - mean) / sigma**3)',
			'amplitude * exp(-0.5 * ((x[0] - mean) / sigma)**2) * ((x[0] - mean)**4 / sigma**6 - 3.0 * (x[0] - mean)**2 / sigma**4)']),
		inner = True)
		if self._catalog.add('G', G) == False:
			### Catalogging failed.
			raise RuntimeException()

		### Predefined double gaussian.
		GG = self.createFunctionFromScript('GG',
		1,
		'amplitude0 * exp(-0.5 * ((x[0] - mean0) / sigma0)**2) + amplitude1 * exp(-0.5 * ((x[0] - mean1) / sigma1)**2)',
		'amplitude0,mean0,sigma0,amplitude1,mean1,sigma1',
		'Double Gaussian',
		gradExpr = ','.join(['exp(-0.5 * ((x[0] - mean0) / sigma0)**2)',
			'amplitude0 * exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * (x[0] - mean0) / sigma0**2',
			'amplitude0 * exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * (x[0] - mean0)**2 / sigma0**3',
			'exp(-0.5 * ((x[0] - mean1) / sigma1)**2)',
			'amplitude1 * exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * (x[0] - mean1) / sigma1**2',
			'amplitude1 * exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * (x[0] - mean1)**2 / sigma1**3']),
		grad2Expr = ','.join(['0.0',
			'exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * (x[0] - mean0) / sigma0**2',
			'exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * (x[0] - mean0)**2 / sigma0**3',
			'0.0',
			'0.0',
			'0.0',
			'exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * (x[0] - mean0) / sigma0**2',
			'amplitude0 * exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * (((x[0] - mean0) / sigma0)**2 - 1.0) / sigma0**2',
			'amplitude0 * exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * ((x[0] - mean0)**3 / sigma0**5 - 2.0 * (x[0] - mean0) / sigma0**3)',
			'0.0',
			'0.0',
			'0.0',
			'exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * (x[0] - mean0)**2 / sigma0**3',
			'amplitude0 * exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * ((x[0] - mean0)**3 / sigma0**5 - 2.0 * (x[0] - mean0) / sigma0**3)',
			'amplitude0 * exp(-0.5 * ((x[0] - mean0) / sigma0)**2) * ((x[0] - mean0)**4 / sigma0**6 - 3.0 * (x[0] - mean0)**2 / sigma0**4)',
			'0.0',
			'0.0',
			'0.0',
			'0.0',
			'0.0',
			'0.0',
			'0.0',
			'exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * (x[0] - mean1) / sigma1**2',
			'exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * (x[0] - mean1)**2 / sigma1**3',
			'0.0',
			'0.0',
			'0.0',
			'exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * (x[0] - mean1) / sigma1**2',
			'amplitude1 * exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * (((x[0] - mean1) / sigma1)**2 - 1.0) / sigma1**2',
			'amplitude1 * exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * ((x[0] - mean1)**3 / sigma1**5 - 2.0 * (x[0] - mean1) / sigma1**3)',
			'0.0',
			'0.0',
			'0.0',
			'exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * (x[0] - mean1)**2 / sigma1**3',
			'amplitude1 * exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * ((x[0] - mean1)**3 / sigma1**5 - 2.0 * (x[0] - mean1) / sigma1**3)',
			'amplitude1 * exp(-0.5 * ((x[0] - mean1) / sigma1)**2) * ((x[0] - mean1)**4 / sigma1**6 - 3.0 * (x[0] - mean1)**2 / sigma1**4)']),
		inner = True)
		if self._catalog.add('GG', GG) == False:
			### Catalogging failed.
			raise RuntimeException()

		### Predefined exponential.
		E = self.createFunctionFromScript('E',
		1,
		'amplitude * exp(exponent * x[0])', 'amplitude,exponent',
		'Exponential',
		gradExpr = ','.join(['exp(exponent * x[0])',
			'amplitude * exp(exponent * x[0]) * x[0]']),
		grad2Expr = ','.join(['0.0',
			'exp(exponent * x[0]) * x[0]',
			'exp(exponent * x[0]) * x[0]',
			'amplitude * exp(exponent * x[0]) * x[0]**2']),
		inner = True)
		if self._catalog.add('E', E) == False:
			### Catalogging failed.
			raise RuntimeException()

		### Predefined double exponential.
		EE = self.createFunctionFromScript('EE',
		1,
		'amplitude0 * exp(exponent0 * x[0]) + amplitude1 * exp(exponent1 * x[0])',
		'amplitude0,exponent0,amplitude1,exponent1',
		'Double Exponential',
		gradExpr = ','.join(['exp(exponent0 * x[0])',
			'amplitude0 * exp(exponent0 * x[0]) * x[0]',
			'exp(exponent1 * x[0])',
			'amplitude1 * exp(exponent1 * x[0]) * x[0]']),
		grad2Expr = ','.join(['0.0',
			'exp(exponent0 * x[0]) * x[0]',
			'0.0',
			'0.0',
			'exp(exponent0 * x[0]) * x[0]',
			'amplitude0 * exp(exponent0 * x[0]) * x[0]**2',
			'0.0',
			'0.0',
			'0.0',
			'0.0',
			'0.0',
			'exp(exponent1 * x[0]) * x[0]',
			'0.0',
			'0.0',
			'exp(exponent1 * x[0]) * x[0]',
			'amplitude1 * exp(exponent1 * x[0]) * x[0]**2']),
		inner = True)
		if self._catalog.add('EE', EE) == False:
			### Catalogging failed.
			raise RuntimeException()

		### Polynomial will be created on demand by calling self._createPolynomial().
		### Any degree of polynomial will be accepted!

	def _createPolynomial(self, degree, parameterNamePrefix, inner):
		name = 'P%d' % degree
		parameters = 'p0'
		expression = 'p0'
		gradExpr = '1.0'
		grad2Expr = '0.0'
		for i in range(degree):
			ip1 = i + 1
			parameters += ',p%d' % ip1
			expression += ' + p%d * x[0]**%d' % (ip1, ip1)
			gradExpr += ',x[0]**%d' % ip1
		grad2Expr += ',0.0' * ((degree + 1)**2 - 1)
		function = self.createFunctionFromScript(name, 1, expression, parameters, 'Polynomial%d' % degree, gradExpr = gradExpr, grad2Expr = grad2Expr, parameterNamePrefix = parameterNamePrefix, inner = True)

		if inner == False:
			if self._catalog.add(name, function) == False:
				### Catalogging failed.
				raise RuntimeException()
		return function

	def _sin(self, data):
		if data._0 in self._zeros:
			_0 = '0.0'
			_1 = '0.0'
		elif data._1 in self._zeros:
			_0 = 'sin(%s)' % (data._0)
			_1 = '0.0'
		elif data._2 in self._zeros:
			_0 = 'sin(%s)' % (data._0)
			_1 = '(cos(%s) * %s)' % (data._0, data._1)
		else:
			_0 = 'sin(%s)' % (data._0)
			_1 = '(cos(%s) * %s)' % (data._0, data._1)
		return _ItemObject(_0, _1)

	def _cos(self, data):
		if data._0 in self._zeros:
			_0 = '1.0'
			_1 = '0.0'
		elif data._1 in self._zeros:
			_0 = 'cos(%s)' % (data._0)
			_1 = '0.0'
		elif data._2 in self._zeros:
			_0 = 'cos(%s)' % (data._0)
			_1 = '(-sin(%s) * %s)' % (data._0, data._1)
		else:
			_0 = 'cos(%s)' % (data._0)
			_1 = '(-sin(%s) * %s)' % (data._0, data._1)
		return _ItemObject(_0, _1)

	def _tan(self, data):
		if data._0 in self._zeros:
			_0 = '0.0'
			_1 = '0.0'
		elif data._1 in self._zeros:
			_0 = 'tan(%s)' % (data._0)
			_1 = '0.0'
		elif data._1 in self._zeros:
			_0 = 'tan(%s)' % (data._0)
			_1 = '(%s / cos(%s)**2)' % (data._1, data._0)
		else:
			_0 = 'tan(%s)' % (data._0)
			_1 = '(%s / cos(%s)**2)' % (data._1, data._0)
		return _ItemObject(_0, _1)

	def _exp(self, data):
		if data._0 in self._zeros:
			_0 = '1.0'
			_1 = '0.0'
		elif data._1 in self._zeros:
			_0 = 'exp(%s)' % (data._0)
			_1 = '0.0'
		elif data._1 in self._zeros:
			_0 = 'exp(%s)' % (data._0)
			_1 = '(exp(%s) * %s)' % (data._0, data._1)
		else:
			_0 = 'exp(%s)' % (data._0)
			_1 = '(exp(%s) * %s)' % (data._0, data._1)
		return _ItemObject(_0, _1)

	def _log(self, data):
		if data._0 in self._zeros:
			raise ValueError, 'Called log(0.0).'
		elif data._1 in self._zeros:
			_0 = 'log(%s)' % (data._0)
			_1 = '0.0'
		elif data._1 in self._zeros:
			_0 = 'log(%s)' % (data._0)
			_1 = '(%s / %s)' % (data._1, data._0)
		else:
			_0 = 'log(%s)' % (data._0)
			_1 = '(%s / %s)' % (data._1, data._0)
		return _ItemObject(_0, _1)

	def _x(self, _index):
		_0 = 'x[%d]' % _index
		_1 = '0.0'
		return _ItemObject(_0, _1)

	def _getParameterNamesByName(self, expression):
		parser = _Shlex(expression)
		parameterNames = []
		dimension = 0
		catalogedNameList = self._catalog.list()
		try:
			while 1:
				item = parser.get_token()
				if item == parser.eof:
					raise _EOFException()

				if item in [' ', '\t', '\r\n', '\r', '\n', '(', ')', '{', '}', '[', ']', '+', '-', '*', '/', '<', '>', '%', '&', ',', '.', '=', '|', '!', ':', ';']:
					continue
				elif item in ['sin', 'cos', 'tan', 'exp', 'log']:
					continue
				else:
					try:
						### Integer?
						int(item)
						continue
					except ValueError:
						try:
							### Float?
							float(item)
							continue
						except ValueError:
							if item in catalogedNameList:
								codeletString = self._catalog._getCodeletString(item)
								innerFunction = self._createCopy(codeletString, item, parameterNamePrefix = item, inner = True)
							elif (item[0] == 'P') and item[1:].isdigit():
								innerFunction = self._createPolynomial(int(item[1:]), item, True)
							else:
								continue
							for functionParameterName in innerFunction.parameterNames():
								if not functionParameterName in parameterNames:
									parameterNames.append(functionParameterName)
							dimension = max(dimension, innerFunction.dimension())
		except _EOFException:
			return parameterNames, dimension

	def _getDerivative0Expression(self, expression, parameterNamePrefix, parameterNames):
		parser = _Shlex(expression)
		innerNameSpace = {}
		innerExpression = ''
		catalogedNameList = self._catalog.list()
		unknownItemFlag = False
		try:
			while 1:
				item = parser.get_token()
				if item == parser.eof:
					raise _EOFException()

				if parameterNamePrefix == None:
					innerPrefix = item
				else:
					innerPrefix = '%s_%s' % (parameterNamePrefix, item)

				if item in catalogedNameList:
					codeletString = self._catalog._getCodeletString(item)
					innerFunction = self._createCopy(codeletString, item, parameterNamePrefix = innerPrefix, inner = True)
					innerNameSpace[innerPrefix] = innerFunction
					innerExpression += '(%s)' % innerFunction._deriv0
				elif (item[0] == 'P') and item[1:].isdigit():
					innerFunction = self._createPolynomial(int(item[1:]), innerPrefix, True)
					innerNameSpace[innerPrefix] = innerFunction
					innerExpression += '(%s)' % innerFunction._deriv0
				elif item == 'x':
					innerExpression += item
				elif item in [' ', '\t', '\r\n', '\r', '\n', '(', ')', '{', '}', '[', ']', '+', '-', '*', '/', '<', '>', '%', '&', ',', '.', '=', '|', '!', ':', ';']:
					innerExpression += item
				elif item in ['sin', 'cos', 'tan', 'exp', 'log']:
					innerExpression += item
				else:
					try:
						### Integer?
						int(item)
						innerExpression += item
					except ValueError:
						try:
							### Float?
							float(item)
							innerExpression += item
						except ValueError:
							if item in parameterNames:
								innerExpression += innerPrefix
							else:
								unknownItemFlag = True
								innerExpression += item
		except _EOFException:
			return innerExpression, innerNameSpace, unknownItemFlag

	def _getDerivative1Expression(self, expression, innerNameSpace, parameterNamePrefix, parameterNames, parameterName):
		parser = _Shlex(expression)
		evalNameSpace = {}
		eval2NameSpace = {}
		evalExpression = ''
		functionNameList = innerNameSpace.keys()
		try:
			while 1:
				item = parser.get_token()
				if item == parser.eof:
					raise _EOFException()

				if item == 'x':
					evalExpression += item
					while 1:
						item = parser.get_token()
						if item == parser.eof:
							raise _EOFException()
						elif item == '[':
							evalExpression += '('
						elif item == ']':
							evalExpression += ')'
							break
						else:
							evalExpression += item
				elif item in [' ', '\t', '\r\n', '\r', '\n', '(', ')', '{', '}', '[', ']', '+', '-', '*', '/', '<', '>', '%', '&', ',', '.', '=', '|', '!', ':', ';']:
					evalExpression += item
				elif item in ['sin', 'cos', 'tan', 'exp', 'log']:
					evalExpression += item
				else:
					try:
						### Integer?
						int(item)
						name = 'Int%s' % item
						_0 = item
						_1 = '0.0'
						evalExpression += name
						evalNameSpace[name] = _ItemObject(_0, _1)
						eval2NameSpace[name] = _ItemObject(_0, _1)
					except ValueError:
						try:
							### Float?
							float(item)
							name = 'Float%s' % (item.replace('.', '_'))
							_0 = item
							_1 = '0.0'
							evalExpression += name
							evalNameSpace[name] = _ItemObject(_0, _1)
							eval2NameSpace[name] = _ItemObject(_0, _1)
						except ValueError:
							if parameterNamePrefix == None:
								name = item
							else:
								name = '%s_%s' % (parameterNamePrefix, item)
							if name in functionNameList:
								innerFunction = innerNameSpace[name]
								functionParameterNames = innerFunction.parameterNames()
								if parameterName in functionParameterNames:
									parameterIndex = functionParameterNames.index(parameterName)
									_0 = '(%s)' % innerFunction._deriv0
									_12 = '%s._getDeriv1(_parameterNameSpace_, %d)' % (name, parameterIndex)
									if innerFunction._deriv1 == None:
										_1 = _12
									else:
										_1 = '(%s)' % innerFunction._deriv1[parameterIndex]
								else:
									_0 = '(%s)' % innerFunction._deriv0
									_1 = '0.0'
									_12 = '0.0'
								evalExpression += name
								evalNameSpace[name] = _ItemObject(_0, _1)
								eval2NameSpace[name] = _ItemObject(_0, _12)
							elif item in parameterNames:
								if item == parameterName:
									_0 = name
									_1 = '1.0'
								else:
									_0 = name
									_1 = '0.0'
								evalExpression += name
								evalNameSpace[name] = _ItemObject(_0, _1)
								eval2NameSpace[name] = _ItemObject(_0, _1)
							else:
								evalExpression += item
		except _EOFException:
			fNameSpace = {'x':self._x, 'sin':self._sin, 'cos':self._cos, 'tan':self._tan, 'exp':self._exp, 'log':self._log}
			evalNameSpace.update(fNameSpace)
			eval2NameSpace.update(fNameSpace)
			result = eval(evalExpression, evalNameSpace, {})
			result2 = eval(evalExpression, eval2NameSpace, {})
			return result._1, result2._1

	def _getDerivative2Expression(self, expression, innerNameSpace, parameterNames, parameterName):
		parser = _Shlex(expression)
		evalNameSpace = {}
		evalExpression = ''
		functionNameList = innerNameSpace.keys()
		try:
			while 1:
				item = parser.get_token()
				if item == parser.eof:
					raise _EOFException()

				if item == 'x':
					evalExpression += item
					while 1:
						item = parser.get_token()
						if item == parser.eof:
							raise _EOFException()
						elif item == '[':
							evalExpression += '('
						elif item == ']':
							evalExpression += ')'
							break
						else:
							evalExpression += item
				elif item in [' ', '\t', '\r\n', '\r', '\n', '(', ')', '{', '}', '[', ']', '+', '-', '*', '/', '<', '>', '%', '&', ',', '.', '=', '|', '!', ':', ';']:
					evalExpression += item
				elif item in ['sin', 'cos', 'tan', 'exp', 'log']:
					evalExpression += item
				else:
					try:
						### Integer?
						int(item)
						name = 'Int%s' % item
						_0 = item
						_1 = '0.0'
						evalExpression += name
						evalNameSpace[name] = _ItemObject(_0, _1)
					except ValueError:
						try:
							### Float?
							float(item)
							name = 'Float%s' % (item.replace('.', '_'))
							_0 = item
							_1 = '0.0'
							evalExpression += name
							evalNameSpace[name] = _ItemObject(_0, _1)
						except ValueError:
							if item in functionNameList:
								item2 = parser.get_token()
								if item2 != '.':
									raise RuntimeError, 'Expected "." but "%s".' % (item2)
								item2 = parser.get_token()
								if item2 != '_getDeriv1':
									raise RuntimeError, 'Expected "_getDeriv1" but "%s".' % (item2)
								item2 = parser.get_token()
								if item2 != '(':
									raise RuntimeError, 'Expected "(" but "%s".' % (item2)
								item2 = parser.get_token()
								if item2 != '_parameterNameSpace_':
									raise RuntimeError, 'Expected "_parameterNameSpace_" but "%s".' % (item2)
								item2 = parser.get_token()
								if item2 != ',':
									raise RuntimeError, 'Expected "," but "%s".' % (item2)
								item2 = parser.get_token()
								if item2 != ' ':
									raise RuntimeError, 'Expected " " but "%s".' % (item2)

								deriv1Index = int(parser.get_token())

								item2 = parser.get_token()
								if item2 != ')':
									raise RuntimeError, 'Expected ")" but "%s".' % (item2)

								innerFunction = innerNameSpace[item]
								if innerFunction._deriv1 == None:
									_0 = '%s._getDeriv1(_parameterNameSpace_, %d)' % (item, deriv1Index)
								else:
									_0 = '(%s)' % innerFunction._deriv1[deriv1Index]
								functionParameterNames = innerFunction.parameterNames()
								if parameterName in functionParameterNames:
									deriv2Index = functionParameterNames.index(parameterName)
									if innerFunction._deriv2 == None:
										_1 = '%s._getDeriv2(_parameterNameSpace_, %d, %d)' % (item, deriv1Index, deriv2Index)
									else:
										_1 = '(%s)' % innerFunction._deriv2[deriv1Index][deriv2Index]
								else:
									_1 = '0.0'
								evalExpression += item
								evalNameSpace[item] = _ItemObject(_0, _1)
							elif item in parameterNames:
								if item == parameterName:
									_0 = item
									_1 = '1.0'
								else:
									_0 = item
									_1 = '0.0'
								evalExpression += item
								evalNameSpace[item] = _ItemObject(_0, _1)
							else:
								evalExpression += item
		except _EOFException:
			evalNameSpace['x'] = self._x
			evalNameSpace['sin'] = self._sin
			evalNameSpace['cos'] = self._cos
			evalNameSpace['tan'] = self._tan
			evalNameSpace['exp'] = self._exp
			evalNameSpace['log'] = self._log
			result = eval(evalExpression, evalNameSpace, {})
			return result._1

	def createFunctionByName(self, path, expression, parameterNamePrefix = None, inner = False):
		parameterNames, dimension = self._getParameterNamesByName(expression)
		if parameterNames == None:
			raise ValueError, 'The expression contains unknown function name.'
		newParameterNames = []
		for parameterName in parameterNames:
			if parameterNamePrefix == None:
				newParameterNames.append(parameterName)
			else:
				newParameterNames.append('%s_%s' % (parameterNamePrefix, parameterName))

		name = os.path.basename(path)
		deriv0, innerNameSpace, unknownItemFlag = self._getDerivative0Expression(expression, parameterNamePrefix, parameterNames)
		if unknownItemFlag:
			deriv1 = None
			deriv2 = None
		else:
			deriv1 = []
			deriv2 = []
			for parameterName in newParameterNames:
				expression1, expression2 = self._getDerivative1Expression(expression, innerNameSpace, parameterNamePrefix, newParameterNames, parameterName)
				deriv1.append(expression1)
				deriv2i = []
				for parameterName2 in newParameterNames:
					deriv2i.append(self._getDerivative2Expression(expression2, innerNameSpace, newParameterNames, parameterName2))
				deriv2.append(deriv2i)

		gradExpr = None
		grad2Expr = None
		newFunction = IFunction('catalog', self, name, dimension, expression, deriv0, deriv1, deriv2, gradExpr, grad2Expr, newParameterNames, innerNameSpace, expression)

		if inner == False:
			if self._catalog.add(name, newFunction) == False:
				### Catalogging failed.
				raise RuntimeError, 'Catalogging "%s" function failed.' % name
			self._tree._mkObject(path, newFunction)
		return newFunction

	def createFunctionFromScript(self, path, dimension, expression, parameterNames, description, gradExpr = None, grad2Expr = None, parameterNamePrefix = None, inner = False):
		_parameterNames = []
		newParameterNames = []
		for _parameterName in parameterNames.split(','):
			_parameterNames.append(_parameterName.strip())
			if parameterNamePrefix == None:
				newParameterNames.append(_parameterName)
			else:
				newParameterNames.append('%s_%s' % (parameterNamePrefix, _parameterName))

		name = os.path.basename(path)
		deriv0, innerNameSpace, unknownItemFlag = self._getDerivative0Expression(expression, parameterNamePrefix, _parameterNames)
		if unknownItemFlag:
			deriv1 = None
			deriv2 = None
		else:
			if grad2Expr == None:
				deriv1 = []
				deriv2 = []
				for parameterName in _parameterNames:
					expression1, expression2 = self._getDerivative1Expression(expression, innerNameSpace, parameterNamePrefix, _parameterNames, parameterName)
					deriv1.append(expression1)
					deriv2i = []
					for parameterName2 in newParameterNames:
						deriv2i.append(self._getDerivative2Expression(expression2, innerNameSpace, newParameterNames, parameterName2))
					deriv2.append(deriv2i)

		if gradExpr != None:
			deriv1 = []
			for item in gradExpr.split(','):
				deriv1.append(self._getDerivative0Expression(item, parameterNamePrefix, _parameterNames)[0])
		if grad2Expr != None:
			deriv2 = []
			nParameters = len(newParameterNames)
			tempExpr = grad2Expr.split(',')
			for i in range(nParameters):
				temp = []
				for item in tempExpr[i * nParameters:(i + 1) * nParameters]:
					temp.append(self._getDerivative0Expression(item, parameterNamePrefix, _parameterNames)[0])
				deriv2.append(temp)

		newFunction = IFunction('verbatim', self, name, dimension, expression, deriv0, deriv1, deriv2, gradExpr, grad2Expr, newParameterNames, innerNameSpace, description)

		if inner == False:
			if self._catalog.add(name, newFunction) == False:
				### Catalogging failed.
				raise RuntimeError, 'Catalogging "%s" function failed.' % name
			self._tree._mkObject(path, newFunction)
		return newFunction

	def cloneFunction(self, f, inner = False):
		codelet = f.codeletString()
		name = 'clone_%s' % f._name
		return self._createCopy(codelet, name, parameterNamePrefix = None, inner = inner)

	def _createCopy(self, codelet, name, parameterNamePrefix = None, inner = False):
		codeletList = codelet.split(':')
		if len(codeletList) == 2:
			### codelet:typename - no location specified (using 'catalogue').
			codeletList.append('catalog')
		typeName = codeletList[2]
		if typeName == 'verbatim':
			### Check if PAIDA can understand or not.
			if not len(codeletList) in [7, 8, 9]:
				RuntimeException('PAIDA can not understand the codelet "%s".' % codelet)
			description = codeletList[1].strip()
			dimension = eval(codeletList[4].strip())
			expression = codeletList[5].strip()
			parameterNames = codeletList[6].strip()
			if len(codeletList) == 7:
				gradExpr = None
				grad2Expr = None
			else:
				gradExpr = codeletList[7].strip()
				if gradExpr == 'null':
					gradExpr = None
				if len(codeletList) == 9:
					grad2Expr = codeletList[8].strip()
					if grad2Expr == 'null':
						grad2Expr = None
				else:
					grad2Expr = None
			newFunction = self.createFunctionFromScript(name, dimension, expression, parameterNames, description, gradExpr = gradExpr, grad2Expr = grad2Expr, parameterNamePrefix = parameterNamePrefix, inner = inner)
		elif typeName in ['catalog', 'catalogue']:
			model = codeletList[1].strip()
			newFunction = self.createFunctionByName(name, model, parameterNamePrefix = parameterNamePrefix, inner = inner)
		elif typeName == 'file':
			RuntimeException('Currently PAIDA can not understand filed functions. codelet = "%s"' % codelet)
		else:
			RuntimeException('Unknown typename "%s" in "%s".' % (typeName, codelet))
		return newFunction

	def catalog(self):
		return self._catalog
