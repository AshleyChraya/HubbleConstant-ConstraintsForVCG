from paida.paida_core.PAbsorber import *
from paida.paida_core.IHistogram1D import *
from paida.paida_core.IHistogram2D import *
from paida.paida_core.IHistogram3D import *
from paida.paida_core.ICloud1D import *
from paida.paida_core.ICloud2D import *
from paida.paida_core.ICloud3D import *
from paida.paida_core.IProfile1D import *
from paida.paida_core.IProfile2D import *
from paida.paida_core.IDataPointSet import *
from paida.paida_core.IFitParameterSettings import *
from paida.paida_core.IFitData import *
from paida.paida_core.IFitResult import *
from paida.paida_core.IFunctionFactory import *
from paida.paida_core.IFunction import *
from paida.paida_core.IRangeSet import *
from paida.paida_core.PExceptions import *
from paida.math.optimize.pyoptimize import fmin_ncg, geneticAlgorithm
from paida.math.array.matrix import matrix
from paida.math.pylapack.dgesv import dgesv

from math import fabs, sqrt, sin, exp, log, fmod, pi
import types

def copyEvaluatorParameterSpace(evaluatorParameterSpace):
	newEvaluatorParameterSpace = evaluatorParameterSpace.copy()
	newEvaluatorParameterSpace['_parameterNameSpace_'] = newEvaluatorParameterSpace
	return newEvaluatorParameterSpace

def updateEvaluatorParameterSpace(evaluatorParameterSpaceFrom, evaluatorParameterSpaceTo):
	evaluatorParameterSpaceTo.update(evaluatorParameterSpaceFrom)
	evaluatorParameterSpaceTo['_parameterNameSpace_'] = evaluatorParameterSpaceTo

class _EOFException(Exception):
	pass

class IFitter:
	_eps2 = 1.4901161193847656e-08
	_engineNames = ['SimplePAIDA', 'PAIDA', 'SimpleGA', 'GA']

	def __init__(self, method, engine, option = {}):
		self.resetConstraints()
		self.resetParameterSettings()
		self.setEngine(engine)
		self.setFitMethod(method)
		self._option = option

	def setUseFunctionGradient(self, boolean):
		raise NotImplementedError

	def useFunctionGradient(self):
		return False

	def setEngine(self, engineName):
		engineNames = self._engineNames
		if not engineName in engineNames:
			raise TypeError('%s is not in %s.' % (engineName, engineNames))
		else:
			self._engineName = engineName

	def engineName(self):
		return self._engineName

	def setFitMethod(self, name):
		methods = ['LeastSquares', 'Chi2', 'CleverChi2', 'BinnedMaximumLikelihood', 'UnbinnedMaximumLikelihood']
		if not name in methods:
			raise TypeError('%s is not in %s.' % (name, methods))

		if name == 'LeastSquares':
			self._fitMethod = 'LeastSquares'
		elif name == 'Chi2':
			self._fitMethod = 'Chi2'
		elif name == 'CleverChi2':
			self._fitMethod = 'CleverChi2'
		elif name == 'BinnedMaximumLikelihood':
			self._fitMethod = 'BinnedMaximumLikelihood'
		elif name == 'UnbinnedMaximumLikelihood':
			self._fitMethod = 'UnbinnedMaximumLikelihood'
		else:
			raise RuntimeError()

	def fitMethodName(self):
		return self._fitMethod

	def fitParameterSettings(self, name):
		if not self._fitParameterSettings.has_key(name):
			self._fitParameterSettings[name] = IFitParameterSettings(name)
		return self._fitParameterSettings[name]

	def listParameterSettings(self):
		return self._fitParameterSettings.keys()

	def resetParameterSettings(self):
		self._fitParameterSettings = {}

	def setConstraint(self, expression):
		if expression in self.constraints():
			raise TypeError('"%s" exists already.' % expression)
		else:
			self._constraints.append(expression)
			self._compiledConstraints.append(compile(expression, 'IFitter.py', 'exec'))

	def constraints(self):
		return self._constraints[:]

	def _getCompiledConstraints(self):
		return self._compiledConstraints

	def _hasConstraints(self):
		return bool(len(self._constraints))

	def resetConstraints(self):
		self._constraints = []
		self._compiledConstraints = []

	def _checkFitType(self, fitData):
		### Check.
		fitMethod = self.fitMethodName()
		if fitData._binned == True:
			### IHistograms, IProfiles and IDataPointSet only.
			if fitMethod in ['LeastSquares', 'Chi2', 'CleverChi2', 'BinnedMaximumLikelihood']:
				pass
			elif fitMethod in ['UnbinnedMaximumLikelihood']:
				raise TypeError('Binned data are unable to be fitted by "%s" method.' % fitMethod)
			else:
				raise RuntimeError()
		else:
			### IClouds and ITuple only.
			if fitMethod in ['LeastSquares', 'Chi2', 'CleverChi2', 'BinnedMaximumLikelihood']:
				raise TypeError('Unbinned data are unable to be fitted by "%s" method.' % fitMethod)
			elif fitMethod in ['UnbinnedMaximumLikelihood']:
				pass
			else:
				raise RuntimeError()

	def fit(self, data1, data2, data3 = None):
		if isinstance(data1, IFitData) and isinstance(data2, IFunction) and (data3 == None):
			fitData = data1
			self._checkFitType(fitData)
			_function = data2
			guessed = False
		elif isinstance(data1, IFitData) and isinstance(data2, types.StringTypes) and (data3 == None):
			fitData = data1
			self._checkFitType(fitData)
			_functionFactory = IFunctionFactory(None)
			_function = _functionFactory.createFunctionByName(data2, data2, inner = True)
			guessed = False
		elif isinstance(data1, IFitData) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			fitData = data1
			self._checkFitType(fitData)
			_functionFactory = IFunctionFactory(None)
			_function = _functionFactory.createFunctionByName(data2, data2, inner = True)
			_function.setParameters(data3)
			guessed = True

		elif isinstance(data1, IHistogram1D) and isinstance(data2, IFunction) and (data3 == None):
			fitData = IFitData()
			fitData.create1DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, IProfile1D) and isinstance(data2, IFunction) and (data3 == None):
			fitData = IFitData()
			fitData.create1DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, ICloud1D) and isinstance(data2, IFunction) and (data3 == None):
			fitData = IFitData()
			fitData.create1DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, IHistogram2D) and isinstance(data2, IFunction) and (data3 == None):
			fitData = IFitData()
			fitData.create2DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, IProfile2D) and isinstance(data2, IFunction) and (data3 == None):
			fitData = IFitData()
			fitData.create2DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, ICloud2D) and isinstance(data2, IFunction) and (data3 == None):
			fitData = IFitData()
			fitData.create2DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, IHistogram3D) and isinstance(data2, IFunction) and (data3 == None):
			fitData = IFitData()
			fitData.create3DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, ICloud3D) and isinstance(data2, IFunction) and (data3 == None):
			fitData = IFitData()
			fitData.create3DConnection(data1)
			return self.fit(fitData, data2)

		elif isinstance(data1, IHistogram1D) and isinstance(data2, types.StringTypes) and (data3 == None):
			fitData = IFitData()
			fitData.create1DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, IProfile1D) and isinstance(data2, types.StringTypes) and (data3 == None):
			fitData = IFitData()
			fitData.create1DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, ICloud1D) and isinstance(data2, types.StringTypes) and (data3 == None):
			fitData = IFitData()
			fitData.create1DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, IHistogram2D) and isinstance(data2, types.StringTypes) and (data3 == None):
			fitData = IFitData()
			fitData.create2DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, IProfile2D) and isinstance(data2, types.StringTypes) and (data3 == None):
			fitData = IFitData()
			fitData.create2DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, ICloud2D) and isinstance(data2, types.StringTypes) and (data3 == None):
			fitData = IFitData()
			fitData.create2DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, IHistogram3D) and isinstance(data2, types.StringTypes) and (data3 == None):
			fitData = IFitData()
			fitData.create3DConnection(data1)
			return self.fit(fitData, data2)
		elif isinstance(data1, ICloud3D) and isinstance(data2, types.StringTypes) and (data3 == None):
			fitData = IFitData()
			fitData.create3DConnection(data1)
			return self.fit(fitData, data2)

		elif isinstance(data1, IHistogram1D) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			fitData = IFitData()
			fitData.create1DConnection(data1)
			return self.fit(fitData, data2, data3)
		elif isinstance(data1, IProfile1D) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			fitData = IFitData()
			fitData.create1DConnection(data1)
			return self.fit(fitData, data2, data3)
		elif isinstance(data1, ICloud1D) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			fitData = IFitData()
			fitData.create1DConnection(data1)
			return self.fit(fitData, data2, data3)
		elif isinstance(data1, IHistogram2D) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			fitData = IFitData()
			fitData.create2DConnection(data1)
			return self.fit(fitData, data2, data3)
		elif isinstance(data1, IProfile2D) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			fitData = IFitData()
			fitData.create2DConnection(data1)
			return self.fit(fitData, data2, data3)
		elif isinstance(data1, ICloud2D) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			fitData = IFitData()
			fitData.create2DConnection(data1)
			return self.fit(fitData, data2, data3)
		elif isinstance(data1, IHistogram3D) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			fitData = IFitData()
			fitData.create3DConnection(data1)
			return self.fit(fitData, data2, data3)
		elif isinstance(data1, ICloud3D) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			fitData = IFitData()
			fitData.create3DConnection(data1)
			return self.fit(fitData, data2, data3)

		elif isinstance(data1, IDataPointSet) and isinstance(data2, IFunction) and (data3 == None):
			indices = range(data1.dimension())
			fitData = IFitData()
			fitData.createConnection(data1, indices[:-1], indices[-1])
			return self.fit(fitData, data2)
		elif isinstance(data1, IDataPointSet) and isinstance(data2, types.StringTypes) and (data3 == None):
			indices = range(data1.dimension())
			fitData = IFitData()
			fitData.createConnection(data1, indices[:-1], indices[-1])
			return self.fit(fitData, data2)
		elif isinstance(data1, IDataPointSet) and isinstance(data2, types.StringTypes) and hasattr(data3, '__iter__'):
			indices = range(data1.dimension())
			fitData = IFitData()
			fitData.createConnection(data1, indices[:-1], indices[-1])
			return self.fit(fitData, data2, data3)

		else:
			raise TypeError('Invalid arguments.')

		inRangeData = self._getInRangeData(fitData)
		self._inRangeData = inRangeData
		self._function = _function

		### Save original parameters.
		originalParameters = _function.parameters()

		### Auto parameter adjustment.
		if (guessed == False) and (fitData._binned == True):
			codelet = _function.codeletString()
			if codelet.startswith('codelet:G:'):
				### Gaussian
				sum = 0.0
				weight = 0.0
				square = 0.0
				for binData in inRangeData:
					x = binData[0][0]
					y = binData[1]
					sum += x * y
					weight += y
					square += x**2 * y
				mean = sum / weight
				sigma = sqrt(square / weight - mean * mean)
				amplitude = weight / (sqrt(2.0 * pi) * sigma)
				_function.setParameters([amplitude, mean, sigma])
			elif codelet.startswith('codelet:E:'):
				### Exponential
				x1 = None
				x2 = None
				for binData in inRangeData:
					if binData[1] != 0.0:
						x1 = binData[0][0]
						y1 = binData[1]
						break
				for i in range(len(inRangeData)):
					binData = inRangeData[-(i + 1)]
					if binData[1] != 0.0:
						x2 = binData[0][0]
						y2 = binData[1]
						break
				if (x1 != None) and (x2 != None):
					slope = log(y1 - y2) / (x1 - x2)
					amplitude = y1 / exp(slope * x1)
					_function.setParameters([amplitude, slope])
			else:
				### No change
				pass

		### Initialization.
		freeParameterNames, limits, constraints, freeIndices, fixedIndices = self._fitInitialization(_function, self._fitParameterSettings)
		engineName = self.engineName()
		fitMethodName = self.fitMethodName()
		parameterNames = _function.parameterNames()

		### Overwrite function methods if any constraint.
		if constraints != []:
			originalDeriv1 = _function._getDeriv1
			originalDeriv1Base = _function._getDeriv1Base
			originalDeriv2 = _function._getDeriv2
			originalDeriv2Base = _function._getDeriv2Base
			_function._getDeriv1 = _function._getDeriv1From0
			_function._getDeriv1Base = _function._getDeriv1From0Base
			_function._getDeriv2 = _function._getDeriv2From0
			_function._getDeriv2Base = _function._getDeriv2From0Base

		### Create IFitResult instance.
		fitResult = IFitResult()
		fitResult._fittedParameterNames = parameterNames[:]
		fitResult._fitParameterSettings = self._fitParameterSettings.copy()
		fitResult._constraints = self.constraints()
		fitResult._engineName = engineName
		fitResult._fitMethodName = fitMethodName

		evaluatorParameterSpace = _function._innerParameterNameSpace
		evaluatorValue, evaluatorGradient, evaluatorHessian = self._getEvaluator(engineName, fitMethodName)
		ndf = len(inRangeData) - len(freeIndices)
		if engineName in self._engineNames:
			if fitMethodName == 'LeastSquares':
				up = 1.0
			elif fitMethodName == 'Chi2':
				up = 1.0
			elif fitMethodName == 'CleverChi2':
				up = 1.0
			elif fitMethodName == 'BinnedMaximumLikelihood':
				up = 0.5
			elif fitMethodName == 'UnbinnedMaximumLikelihood':
				up = 0.5
			else:
				raise RuntimeError()

			### Verbose mode?
			if self._option.has_key('verbose'):
				if self._option['verbose'] == True:
					verbose = True
				else:
					verbose = False
			else:
				verbose = False

			### Get the solutions.
			if engineName in ['SimplePAIDA', 'PAIDA']:
				minimum, hessian, warnflag, mesg = fmin_ncg(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, freeParameterNames, limits, constraints, freeIndices, fixedIndices, display = verbose)
			elif engineName in ['SimpleGA', 'GA']:
				minimum, hessian, warnflag, mesg = geneticAlgorithm(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, freeParameterNames, limits, constraints, freeIndices, fixedIndices, ndf, display = verbose)
			else:
				raise RuntimeError, 'Unknown engine name:', engineName
			resultValues = _function.parameters()

			### Is valid?
			if warnflag == 0:
				### Yes.
				fitResult._isValid = True
				fitResult._fittedParameters = resultValues
				fitResult._dataDescription = mesg
				fitResult._fitStatus = 0
				fitResult._fittedFunction = _function._getParentFactory().cloneFunction(_function, inner = True)
				fitResult._fittedFunction.annotation().setValue('Title', 'fitted_%s' % _function.annotation().value('Title'))
				fitResult._fittedFunction.setParameters(resultValues)
				fitResult._ndf = ndf
				fitResult._quality = minimum / fitResult._ndf

				if fitMethodName == 'LeastSquares':
					### PAIDA is not able to calculate errors in this case.
					fitResult._covMatrixElement = None
					fitResult._errors = None
					fitResult._errorsPlus = None
					fitResult._errorsMinus = None
				else:
					### Get parabolic errors.
					errorMatrix = self._getErrorMatrix(hessian)
					if errorMatrix == None:
						### Invalid result.
						fitResult._dataDescription = 'The solution is found, but parabolic error is invalid.'
						fitResult._fitStatus = 2
					else:
						fitResult._covMatrixElement = errorMatrix
						fitResult._errors = []
						parabolicErrors = []
						freeIndex = 0
						for i in range(len(parameterNames)):
							if i in freeIndices:
								error = sqrt(errorMatrix[freeIndex][freeIndex])
								fitResult._errors.append(error)
								parabolicErrors.append(error)
								freeIndex += 1
							else:
								fitResult._errors.append(0.0)
								parabolicErrors.append(0.0)

						### Simple engine?
						if engineName in ['SimplePAIDA', 'SimpleGA']:
							### Asymmetric errors are not calculated.
							fitResult._errorsPlus = [None] * len(parabolicErrors)
							fitResult._errorsMinus = [None] * len(parabolicErrors)
						else:
							### Get asymmetric errors.
							asymmetricErrors = self._getAsymmetricError(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, parameterNames, freeParameterNames, limits, constraints, freeIndices, fixedIndices, minimum, up, parabolicErrors)
							if asymmetricErrors == None:
								### Invalid result.
								fitResult._dataDescription = 'The solution and parabolic error are found, but asymmetric error is invalid.'
								fitResult._fitStatus = 1
								fitResult._errorsPlus = [None] * len(parabolicErrors)
								fitResult._errorsMinus = [None] * len(parabolicErrors)
							else:
								fitResult._errorsPlus = []
								fitResult._errorsMinus = []
								for asymmetricError in asymmetricErrors:
									fitResult._errorsMinus.append(asymmetricError[0])
									fitResult._errorsPlus.append(asymmetricError[1])

			else:
				### No, invalid.
				fitResult._isValid = False
				fitResult._dataDescription = mesg
				fitResult._fitStatus = -1

		else:
			raise RuntimeError()

		### Overwrite back function methods if any constraint.
		if constraints != []:
			_function._getDeriv1 = originalDeriv1
			_function._getDeriv1Base = originalDeriv1Base
			_function._getDeriv2 = originalDeriv2
			_function._getDeriv2Base = originalDeriv2Base

		### Return to original states.
		_function.setParameters(originalParameters)

		return fitResult

	def _getInRangeData(self, fitData):
		### Fitting range initialization with associated error check.
		inRangeData = []
		dimension = fitData.dimension()
		centers = fitData._connection[0]
		weights = fitData._connection[1]
		errorsP = fitData._connection[2]
		errorsM = fitData._connection[3]

		fitMethodName = self.fitMethodName()
		for i, center in enumerate(centers):
			### Range check.
			for axisNumber in range(dimension):
				if not fitData.range(axisNumber).isInRange(center[axisNumber]):
					### Out of range.
					break
			else:
				### Check fit method.
				if fitMethodName == 'Chi2':
					weight = weights[i]

					errorP = errorsP[i]
					if errorP == None:
						if weight > 0.0:
							errorP = weight
						else:
							### Exclude.
							continue
					else:
						if errorP == 0.0:
							if weight > 0.0:
								errorP = weight
							else:
								### Exclude.
								continue

					errorM = errorsM[i]
					if errorM == None:
						if weight > 0.0:
							errorM = weight
						else:
							### Exclude.
							continue
					else:
						if errorM == 0.0:
							if weight > 0.0:
								errorM = weight
							else:
								### Exclude.
								continue
					inRangeData.append([center, weight, errorP, errorM])

				elif fitMethodName == 'CleverChi2':
					if weights[i] != 0.0:
						inRangeData.append([center, weights[i]])
				elif fitMethodName == 'LeastSquares':
					inRangeData.append([center, weights[i]])
				elif fitMethodName == 'BinnedMaximumLikelihood':
					inRangeData.append([center, weights[i]])
				elif fitMethodName == 'UnbinnedMaximumLikelihood':
					inRangeData.append([center])
				else:
					raise RuntimeError()
		return inRangeData

	def _fitInitialization(self, function, fitParameterSettings):
		constraintNames = []
		compiledConstraints = self._getCompiledConstraints()
		for constraint in self.constraints():
			constraintNames.append(constraint.split('=')[0].strip())

		freeParameterNames = []
		freeIndices = []
		fixedIndices = []
		limits = []
		for parameterIndex, parameterName in enumerate(function.parameterNames()):
			parameterValue = function.parameter(parameterName)
			### This parameter has any setting?
			if fitParameterSettings.has_key(parameterName):
				setting = fitParameterSettings[parameterName]
				### This parameter is fixed or bound?
				if setting.isFixed():
					###Fixed parameter.
					fixedIndices.append(parameterIndex)
					limits.append([None, None])
				elif setting.isBound():
					### Bound parameter.
					lower = setting.lowerBound()
					upper = setting.upperBound()
					### Check if parameter is between bounds.
					if not (lower < parameterValue < upper):
						raise TypeError('%s=%f is not between %f and %f' % (parameterName, parameterValue, lower, upper))
					### Parameter conversion.
					if (lower != IRangeSet._NINF) and (upper != IRangeSet._PINF):
						limits.append([lower, upper])
					elif (lower == IRangeSet._NINF) and (upper != IRangeSet._PINF):
						limits.append([None, upper])
					elif (lower != IRangeSet._NINF) and (upper == IRangeSet._PINF):
						limits.append([lower, None])
					else:
						raise RuntimeError('Must be isBound() == False in this case.')

					### Under constraint?
					if not parameterName in constraintNames:
						### No.
						freeIndices.append(parameterIndex)
						freeParameterNames.append(parameterName)
				else:
					### Unbound parameter.
					limits.append([None, None])

					### Under constraint?
					if not parameterName in constraintNames:
						### No.
						freeIndices.append(parameterIndex)
						freeParameterNames.append(parameterName)
			else:
				### Unbound parameter.
				limits.append([None, None])

				### Under constraint?
				if not parameterName in constraintNames:
					### No.
					freeIndices.append(parameterIndex)
					freeParameterNames.append(parameterName)

		return freeParameterNames, limits, compiledConstraints, freeIndices, fixedIndices

	def _roundResult(self, result):
		if abs(result) < self._eps2:
			return 0.0
		else:
			return result

	def _leastSquaresValue(self, parameterNameSpace):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			sum += (getDeriv0Base(parameterNameSpace) - binData[1])**2
		return self._roundResult(sum)

	def _leastSquaresValueConstrained(self, parameterNameSpace):
		return self._leastSquaresValue(parameterNameSpace)

	def _chi2Value(self, parameterNameSpace):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			difference = getDeriv0Base(parameterNameSpace) - binData[1]
			if difference > 0.0:
				sum += difference**2 / binData[2]
			else:
				sum += difference**2 / binData[3]
		return self._roundResult(sum)

	def _chi2ValueConstrained(self, parameterNameSpace):
		return self._chi2Value(parameterNameSpace)

	def _cleverChi2Value(self, parameterNameSpace):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			fValue = getDeriv0Base(parameterNameSpace)
			sum += (fValue - binData[1])**2 / fabs(fValue)
		return self._roundResult(sum)

	def _cleverChi2ValueConstrained(self, parameterNameSpace):
		return self._cleverChi2Value(parameterNameSpace)

	def _binnedMaximumLikelihoodValue(self, parameterNameSpace):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			fValue = getDeriv0Base(parameterNameSpace)
			sum += (fValue - binData[1] * log(fValue))
		return self._roundResult(sum)

	def _binnedMaximumLikelihoodValueConstrained(self, parameterNameSpace):
		return self._binnedMaximumLikelihoodValue(parameterNameSpace)

	def _unbinnedMaximumLikelihoodValue(self, parameterNameSpace):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			sum -= log(getDeriv0Base(parameterNameSpace))
		return self._roundResult(sum)

	def _unbinnedMaximumLikelihoodValueConstrained(self, parameterNameSpace):
		return self._unbinnedMaximumLikelihoodValue(parameterNameSpace)

	def _leastSquaresGradient(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			sum += 2.0 * (getDeriv0Base(parameterNameSpace) - binData[1]) * getDeriv1Base(parameterNameSpace, i)
		return self._roundResult(sum)

	def _leastSquaresGradientConstrained(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			sum += 2.0 * (getDeriv0Base(parameterNameSpace) - binData[1]) * getDeriv1Base(parameterNameSpace, i, constraints)
		return self._roundResult(sum)

	def _chi2Gradient(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			difference = getDeriv0Base(parameterNameSpace) - binData[1]
			if difference > 0.0:
				sum += 2.0 * difference / binData[2] * getDeriv1Base(parameterNameSpace, i)
			else:
				sum += 2.0 * difference / binData[3] * getDeriv1Base(parameterNameSpace, i)
		return self._roundResult(sum)

	def _chi2GradientConstrained(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			difference = getDeriv0Base(parameterNameSpace) - binData[1]
			if difference > 0.0:
				sum += 2.0 * difference / binData[2] * getDeriv1Base(parameterNameSpace, i, constraints)
			else:
				sum += 2.0 * difference / binData[3] * getDeriv1Base(parameterNameSpace, i, constraints)
		return self._roundResult(sum)

	def _cleverChi2Gradient(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += 2.0 * (data - binData[1]) / fabs(data) * getDeriv1Base(parameterNameSpace, i)
		return self._roundResult(sum)

	def _cleverChi2GradientConstrained(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += 2.0 * (data - binData[1]) / fabs(data) * getDeriv1Base(parameterNameSpace, i, constraints)
		return self._roundResult(sum)

	def _binnedMaximumLikelihoodGradient(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += getDeriv1Base(parameterNameSpace, i) * (1.0 - binData[1] / data)
		return self._roundResult(sum)

	def _binnedMaximumLikelihoodGradientConstrained(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += getDeriv1Base(parameterNameSpace, i, constraints) * (1.0 - binData[1] / data)
		return self._roundResult(sum)

	def _unbinnedMaximumLikelihoodGradient(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum -= getDeriv1Base(parameterNameSpace, i) / data
		return self._roundResult(sum)

	def _unbinnedMaximumLikelihoodGradientConstrained(self, parameterNameSpace, i):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum -= getDeriv1Base(parameterNameSpace, i, constraints) / data
		return self._roundResult(sum)

	def _leastSquaresHessian(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		getDeriv2Base = function._getDeriv2Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			sum += 2.0 * (getDeriv1Base(parameterNameSpace, i) * getDeriv1Base(parameterNameSpace, j) + (getDeriv0Base(parameterNameSpace) - binData[1]) * getDeriv2Base(parameterNameSpace, i, j))
		return self._roundResult(sum)

	def _leastSquaresHessianConstrained(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		getDeriv2Base = function._getDeriv2From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			sum += 2.0 * (getDeriv1Base(parameterNameSpace, i, constraints) * getDeriv1Base(parameterNameSpace, j, constraints) + (getDeriv0Base(parameterNameSpace) - binData[1]) * getDeriv2Base(parameterNameSpace, i, j, constraints))
		return self._roundResult(sum)

	def _chi2Hessian(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		getDeriv2Base = function._getDeriv2Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			difference = getDeriv0Base(parameterNameSpace) - binData[1]
			if difference > 0.0:
				sum += 2.0 * (getDeriv1Base(parameterNameSpace, i) * getDeriv1Base(parameterNameSpace, j) + difference * getDeriv2Base(parameterNameSpace, i, j)) / binData[2]
			else:
				sum += 2.0 * (getDeriv1Base(parameterNameSpace, i) * getDeriv1Base(parameterNameSpace, j) + difference * getDeriv2Base(parameterNameSpace, i, j)) / binData[3]
		return self._roundResult(sum)

	def _chi2HessianConstrained(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		getDeriv2Base = function._getDeriv2From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			difference = getDeriv0Base(parameterNameSpace) - binData[1]
			if difference > 0.0:
				sum += 2.0 * (getDeriv1Base(parameterNameSpace, i, constraints) * getDeriv1Base(parameterNameSpace, j, constraints) + difference * getDeriv2Base(parameterNameSpace, i, j, constraints)) / binData[2]
			else:
				sum += 2.0 * (getDeriv1Base(parameterNameSpace, i, constraints) * getDeriv1Base(parameterNameSpace, j, constraints) + difference * getDeriv2Base(parameterNameSpace, i, j, constraints)) / binData[3]
		return self._roundResult(sum)

	def _cleverChi2Hessian(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		getDeriv2Base = function._getDeriv2Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += 2.0 * (getDeriv1Base(parameterNameSpace, i) * getDeriv1Base(parameterNameSpace, j) + (data - binData[1]) * getDeriv2Base(parameterNameSpace, i, j)) / fabs(data)
		return self._roundResult(sum)

	def _cleverChi2HessianConstrained(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		getDeriv2Base = function._getDeriv2From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += 2.0 * (getDeriv1Base(parameterNameSpace, i, constraints) * getDeriv1Base(parameterNameSpace, j, constraints) + (data - binData[1]) * getDeriv2Base(parameterNameSpace, i, j, constraints)) / fabs(data)
		return self._roundResult(sum)

	def _binnedMaximumLikelihoodHessian(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		getDeriv2Base = function._getDeriv2Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += getDeriv2Base(parameterNameSpace, i, j) * (1.0 - binData[1] / data) + getDeriv1Base(parameterNameSpace, i) * getDeriv1Base(parameterNameSpace, j) * binData[1] / data**2
		return self._roundResult(sum)

	def _binnedMaximumLikelihoodHessianConstrained(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		getDeriv2Base = function._getDeriv2From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += getDeriv2Base(parameterNameSpace, i, j, constraints) * (1.0 - binData[1] / data) + getDeriv1Base(parameterNameSpace, i, constraints) * getDeriv1Base(parameterNameSpace, j, constraints) * binData[1] / data**2
		return self._roundResult(sum)

	def _unbinnedMaximumLikelihoodHessian(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1Base
		getDeriv2Base = function._getDeriv2Base
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += getDeriv1Base(parameterNameSpace, i) * getDeriv1Base(parameterNameSpace, j) / data**2 - getDeriv2Base(parameterNameSpace, i, j) / data
		return self._roundResult(sum)

	def _unbinnedMaximumLikelihoodHessianConstrained(self, parameterNameSpace, i, j):
		function = self._function
		getDeriv0Base = function._getDeriv0Base
		getDeriv1Base = function._getDeriv1From0BaseConstrained
		getDeriv2Base = function._getDeriv2From0BaseConstrained
		constraints = self._getCompiledConstraints()
		sum = 0.0
		for binData in self._inRangeData:
			parameterNameSpace['x'] = binData[0]
			data = getDeriv0Base(parameterNameSpace)
			sum += getDeriv1Base(parameterNameSpace, i, constraints) * getDeriv1Base(parameterNameSpace, j, constraints) / data**2 - getDeriv2Base(parameterNameSpace, i, j, constraints) / data
		return self._roundResult(sum)

	def _getErrorMatrix(self, sums2):
		fitMethodName = self.fitMethodName()
		if fitMethodName == 'LeastSquares':
			up = 2.0
		elif fitMethodName == 'Chi2':
			up = 2.0
		elif fitMethodName == 'CleverChi2':
			up = 2.0
		elif fitMethodName == 'BinnedMaximumLikelihood':
			up = 1.0
		elif fitMethodName == 'UnbinnedMaximumLikelihood':
			up = 1.0
		else:
			raise RuntimeError()

		### Create the error matrix.
		Nf = len(sums2)
		if Nf == 1:
			errorMatrix = [[up / sums2[0][0]]]
		else:
			a = matrix(sums2, link = True)
			try:
				errorMatrix = (a.inverse() * up).toList()
			except:
				return None

		### Check and return.
		for i in range(Nf):
			if errorMatrix[i][i] < 0.0:
				return None
		return errorMatrix

	def _getAsymmetricError(self, evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, parameterNames, freeParameterNames, limits, constraints, freeIndices, fixedIndices, minimum, up, parabolicErrors):
		currentSpace = copyEvaluatorParameterSpace(evaluatorParameterSpace)
		errors = []
		for i, parameterName in enumerate(parameterNames):
			if i in freeIndices:
				valuei = currentSpace[parameterName]
				evaluatorParameterSpace[parameterName] = valuei - parabolicErrors[i]
				### Get the solutions.
				value1, warnflag1, mesg2 = self._asymmetricErrorSearch(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, parameterNames, freeParameterNames, limits, constraints, freeIndices, fixedIndices, minimum + up, i, parameterName)
				if warnflag1 != 0:
					return None

				evaluatorParameterSpace[parameterName] = valuei + parabolicErrors[i]
				### Get the solutions.
				value2, warnflag2, mesg2 = self._asymmetricErrorSearch(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, parameterNames, freeParameterNames, limits, constraints, freeIndices, fixedIndices, minimum + up, i, parameterName)
				if warnflag2 != 0:
					return None

				#if value1 == value2:
				#	return None
				errorMinus = valuei - min(value1, value2)
				errorPlus = max(value1, value2) - valuei
				errors.append([errorMinus, errorPlus])
			else:
				errors.append([0.0, 0.0])
		updateEvaluatorParameterSpace(currentSpace, evaluatorParameterSpace)
		return errors

	def _asymmetricErrorSearch(self, evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, parameterNames, freeParameterNames, limits, constraints, freeIndices, fixedIndices, targetValue, i, parameterName, heightErrorLimit = None, maxIter = None):
		N = len(freeParameterNames)
		if heightErrorLimit == None:
			heightErrorLimit = self._eps2
		if maxIter == None:
			maxIter = N * 200

		if freeIndices == [i]:
			single = True
		else:
			freeParameterNames2 = freeParameterNames[:]
			freeParameterNames2.remove(parameterNames[i])
			freeIndices2 = freeIndices[:]
			freeIndices2.remove(i)
			fixedIndices2 = fixedIndices[:]
			fixedIndices2.append(i)
			single = False

		currentSpace = copyEvaluatorParameterSpace(evaluatorParameterSpace)
		currentIter = 0
		while 1:
			currentIter += 1
			if currentIter > maxIter:
				warnflag = 1
				mesg = 'Warning: Maximum number of iterations has been exceeded.'
				break
			if single:
				localMinimum = evaluatorValue(evaluatorParameterSpace)
			else:
				localMinimum, hessian, warnflag, mesg = fmin_ncg(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, freeParameterNames2, limits, constraints, freeIndices2, fixedIndices2, display = False)
				if warnflag != 0:
					warnflag = 2
					mesg = 'Optimization failed.'
					break
			heightError = targetValue - localMinimum
			if fabs(heightError) < heightErrorLimit:
				warnflag = 0
				mesg = 'Optimization terminated successfully.'
				break
			evaluatorParameterSpace[parameterName] += heightError / evaluatorGradient(evaluatorParameterSpace, i)

		result = evaluatorParameterSpace[parameterName]
		updateEvaluatorParameterSpace(currentSpace, evaluatorParameterSpace)
		return result, warnflag, mesg

	def _getEvaluator(self, engineName, fitMethodName):
		if engineName in self._engineNames:
			if self._hasConstraints():
				if fitMethodName == 'LeastSquares':
					evaluatorValue = self._leastSquaresValueConstrained
					evaluatorGradient = self._leastSquaresGradientConstrained
					evaluatorHessian = self._leastSquaresHessianConstrained
				elif fitMethodName == 'Chi2':
					evaluatorValue = self._chi2ValueConstrained
					evaluatorGradient = self._chi2GradientConstrained
					evaluatorHessian = self._chi2HessianConstrained
				elif fitMethodName == 'CleverChi2':
					evaluatorValue = self._cleverChi2ValueConstrained
					evaluatorGradient = self._cleverChi2GradientConstrained
					evaluatorHessian = self._cleverChi2HessianConstrained
				elif fitMethodName == 'BinnedMaximumLikelihood':
					evaluatorValue = self._binnedMaximumLikelihoodValueConstrained
					evaluatorGradient = self._binnedMaximumLikelihoodGradientConstrained
					evaluatorHessian = self._binnedMaximumLikelihoodHessianConstrained
				elif fitMethodName == 'UnbinnedMaximumLikelihood':
					evaluatorValue = self._unbinnedMaximumLikelihoodValueConstrained
					evaluatorGradient = self._unbinnedMaximumLikelihoodGradientConstrained
					evaluatorHessian = self._unbinnedMaximumLikelihoodHessianConstrained
				else:
					raise RuntimeError()
			else:
				if fitMethodName == 'LeastSquares':
					evaluatorValue = self._leastSquaresValue
					evaluatorGradient = self._leastSquaresGradient
					evaluatorHessian = self._leastSquaresHessian
				elif fitMethodName == 'Chi2':
					evaluatorValue = self._chi2Value
					evaluatorGradient = self._chi2Gradient
					evaluatorHessian = self._chi2Hessian
				elif fitMethodName == 'CleverChi2':
					evaluatorValue = self._cleverChi2Value
					evaluatorGradient = self._cleverChi2Gradient
					evaluatorHessian = self._cleverChi2Hessian
				elif fitMethodName == 'BinnedMaximumLikelihood':
					evaluatorValue = self._binnedMaximumLikelihoodValue
					evaluatorGradient = self._binnedMaximumLikelihoodGradient
					evaluatorHessian = self._binnedMaximumLikelihoodHessian
				elif fitMethodName == 'UnbinnedMaximumLikelihood':
					evaluatorValue = self._unbinnedMaximumLikelihoodValue
					evaluatorGradient = self._unbinnedMaximumLikelihoodGradient
					evaluatorHessian = self._unbinnedMaximumLikelihoodHessian
				else:
					raise RuntimeError()
		else:
			raise RuntimeError()

		return evaluatorValue, evaluatorGradient, evaluatorHessian

	def createScan1D(self, fitData, function, parameterName, npts, pmin, pmax):
		originals = function.parameters()
		currentFunction = self._function
		currentRangeData = self._inRangeData
		dataPointSet = IDataPointSet('scan1D', 'scan1D', 2)
		inRangeData = self._getInRangeData(fitData)
		evaluatorParameterSpace = function._innerParameterNameSpace
		evaluatorValue, evaluatorGradient, evaluatorHessian = self._getEvaluator(self.engineName(), self.fitMethodName())

		self._function = function
		self._inRangeData = inRangeData
		for step in range(npts):
			value = pmin + (pmax - pmin) * (step + 0.5) / npts
			function.setParameter(parameterName, value)
			dataPoint = dataPointSet.addPoint()
			dataPoint.coordinate(0).setValue(value)
			dataPoint.coordinate(1).setValue(evaluatorValue(evaluatorParameterSpace))

		function.setParameters(originals)
		self._function = currentFunction
		self._inRangeData = currentRangeData
		return dataPointSet

	def createContour(self, fitData, fitResult, parameterName1, parameterName2, npts, up):
		function = fitResult.fittedFunction()
		originals = fitResult.fittedParameters()
		parameterNames = function.parameterNames()
		currentFunction = self._function
		currentRangeData = self._inRangeData
		inRangeData = self._getInRangeData(fitData)
		evaluatorParameterSpace = function._innerParameterNameSpace
		evaluatorValue, evaluatorGradient, evaluatorHessian = self._getEvaluator(fitResult.engineName(), fitResult.fitMethodName())

		self._function = function
		self._inRangeData = inRangeData
		minimum = evaluatorValue(evaluatorParameterSpace)
		parameterErrorsAll = fitResult.errors()
		wasFixed = {}
		fitParameterSettings = {}
		parabolicErrors = []
		for i, name in enumerate(parameterNames):
			fitParameterSetting = fitResult.fitParameterSettings(name)
			wasFixed[name] = fitParameterSetting.isFixed()
			if name == parameterName1:
				fitParameterSetting.setFixed(False)
				parabolicErrors.append(parameterErrorsAll[i] * up)
			elif name == parameterName2:
				fitParameterSetting.setFixed(True)
				parabolicErrors.append(parameterErrorsAll[i] * up)
			else:
				fitParameterSetting.setFixed(True)
				parabolicErrors.append(0.0)
			fitParameterSettings[name] = fitParameterSetting
		freeParameterNames, limits, constraints, freeIndices, fixedIndices = self._fitInitialization(function, fitParameterSettings)
		asymmetricErrors = self._getAsymmetricError(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, parameterNames, freeParameterNames, limits, constraints, freeIndices, fixedIndices, minimum, up, parabolicErrors)
		parameter1Index = parameterNames.index(parameterName1)
		parameter2Index = parameterNames.index(parameterName2)
		parameter1Value = evaluatorParameterSpace[parameterName1]
		parameter2Value = evaluatorParameterSpace[parameterName2]
		min1 = parameter1Value - asymmetricErrors[parameter1Index][0]
		max1 = parameter1Value + asymmetricErrors[parameter1Index][1]

		dataPointSet = IDataPointSet('contour', 'contour', 2)
		length1 = max1 - min1
		nptsm1 = npts - 1
		freeIndices.append(parameter2Index)
		freeIndices.remove(parameter1Index)
		fixedIndices.append(parameter1Index)
		fixedIndices.remove(parameter2Index)
		for step1 in range(npts):
			value1 = min1 + length1 * step1 / nptsm1
			evaluatorParameterSpace[parameterName1] = value1
			asymmetricErrors2 = self._getAsymmetricError(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, parameterNames, freeParameterNames, limits, constraints, freeIndices, fixedIndices, minimum, up, parabolicErrors)
			parameter2Minus = parameter2Value - asymmetricErrors2[parameter2Index][0]
			parameter2Plus = parameter2Value + asymmetricErrors2[parameter2Index][1]
			if parameter2Minus == parameter2Plus:
				dataPoint = dataPointSet.addPoint()
				dataPoint.coordinate(0).setValue(value1)
				dataPoint.coordinate(1).setValue(parameter2Minus)
			else:
				dataPoint = dataPointSet.addPoint()
				dataPoint.coordinate(0).setValue(value1)
				dataPoint.coordinate(1).setValue(parameter2Minus)
				dataPoint = dataPointSet.addPoint()
				dataPoint.coordinate(0).setValue(value1)
				dataPoint.coordinate(1).setValue(parameter2Plus)

		function.setParameters(originals)
		self._function = currentFunction
		self._inRangeData = currentRangeData
		for name in parameterNames:
			fitResult.fitParameterSettings(name).setFixed(wasFixed[name])

		return dataPointSet
