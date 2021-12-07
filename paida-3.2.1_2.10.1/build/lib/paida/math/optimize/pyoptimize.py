### NOTICE ###
# pyoptimize.py module by Koji KISHIMOTO (korry@users.sourceforge.net)
#
# This is pure python, and able to limit, constraint or fix parameters.

from paida.paida_core.PAbsorber import *
from math import sin, cos, tan, e, pi, asin, exp, log, sqrt
import random
try:
	import threading
except ImportError:
	import dummy_threading as threading

_normalNameSpace = {'exp': exp,
'sin': sin,
'cos': cos,
'tan': tan,
'log': log,
'e': e,
'pi': pi}

def _o2iConvert(lowerEdge, upperEdge, value):
	if (lowerEdge != None) and (upperEdge != None):
		return asin(2.0 * (value - lowerEdge) / (upperEdge - lowerEdge) - 1.0)
	elif (lowerEdge == None) and (upperEdge != None):
		return log(upperEdge - value)
	elif (lowerEdge != None) and (upperEdge == None):
		return log(value - lowerEdge)
	else:
		return value

def _o2i(evaluatorParameterSpace, limits, freeIndices, freeParameterNames):
	for i, (lowerEdge, upperEdge) in enumerate(limits):
		if i in freeIndices:
			parameterName = freeParameterNames[freeIndices.index(i)]
			evaluatorParameterSpace[parameterName] = _o2iConvert(lowerEdge, upperEdge, evaluatorParameterSpace[parameterName])

def _i2oConvert(lowerEdge, upperEdge, value):
	if (lowerEdge != None) and (upperEdge != None):
		return lowerEdge + (upperEdge - lowerEdge) * (sin(value) + 1.0) / 2.0
	elif (lowerEdge == None) and (upperEdge != None):
		return upperEdge - exp(value)
	elif (lowerEdge != None) and (upperEdge == None):
		return lowerEdge + exp(value)
	else:
		return value

def _i2o(evaluatorParameterSpace, limits, freeIndices, freeParameterNames):
	for i, (lowerEdge, upperEdge) in enumerate(limits):
		if i in freeIndices:
			parameterName = freeParameterNames[freeIndices.index(i)]
			evaluatorParameterSpace[parameterName] = _i2oConvert(lowerEdge, upperEdge, evaluatorParameterSpace[parameterName])

def _constraint(evaluatorParameterSpace, constraints):
	for constraint in constraints:
		### Jython2.1 doesn't understand exec(code, globals(), locals()) properly.
		#eval(constraint, _normalNameSpace, evaluatorParameterSpace)
		exec constraint in _normalNameSpace, evaluatorParameterSpace

def copyEvaluatorParameterSpace(evaluatorParameterSpace):
	newEvaluatorParameterSpace = evaluatorParameterSpace.copy()
	newEvaluatorParameterSpace['_parameterNameSpace_'] = newEvaluatorParameterSpace
	return newEvaluatorParameterSpace

def updateEvaluatorParameterSpace(evaluatorParameterSpaceFrom, evaluatorParameterSpaceTo):
	evaluatorParameterSpaceTo.update(evaluatorParameterSpaceFrom)
	evaluatorParameterSpaceTo['_parameterNameSpace_'] = evaluatorParameterSpaceTo

class _WrapFunction:
	def __init__(self, limits, constraints, freeIndices, freeParameterNames, evaluatorValue, evaluatorGradient, evaluatorHessian):
		self._limits = limits
		self._constraints = constraints
		self._freeIndices = freeIndices
		self._freeParameterNames = freeParameterNames
		self._evaluatorValue = evaluatorValue
		self._evaluatorGradient = evaluatorGradient
		self._evaluatorHessian = evaluatorHessian

	def evaluatorValue(self, evaluatorParameterSpace):
		_i2o(evaluatorParameterSpace, self._limits, self._freeIndices, self._freeParameterNames)
		_constraint(evaluatorParameterSpace, self._constraints)
		result = self._evaluatorValue(evaluatorParameterSpace)
		_o2i(evaluatorParameterSpace, self._limits, self._freeIndices, self._freeParameterNames)
		return result

	def evaluatorGradient(self, evaluatorParameterSpace, i):
		_i2o(evaluatorParameterSpace, self._limits, self._freeIndices, self._freeParameterNames)
		_constraint(evaluatorParameterSpace, self._constraints)
		result = self._evaluatorGradient(evaluatorParameterSpace, i)
		_o2i(evaluatorParameterSpace, self._limits, self._freeIndices, self._freeParameterNames)
		return result

	def evaluatorHessian(self, evaluatorParameterSpace, i, j):
		_i2o(evaluatorParameterSpace, self._limits, self._freeIndices, self._freeParameterNames)
		_constraint(evaluatorParameterSpace, self._constraints)
		result = self._evaluatorHessian(evaluatorParameterSpace, i, j)
		_o2i(evaluatorParameterSpace, self._limits, self._freeIndices, self._freeParameterNames)
		return result

def _wrap(limits, constraints, freeIndices, freeParameterNames, evaluatorValue, evaluatorGradient, evaluatorHessian):
	if (limits != [[None, None]]*len(limits)) or (constraints != []):
		wrapper = _WrapFunction(limits, constraints, freeIndices, freeParameterNames, evaluatorValue, evaluatorGradient, evaluatorHessian)
		return wrapper.evaluatorValue, wrapper.evaluatorGradient, wrapper.evaluatorHessian
	else:
		return evaluatorValue, evaluatorGradient, evaluatorHessian

def line_search_BFGS(evaluatorValue, evaluatorParameterSpace, freeParameterNames, pk, gfk):
	originalSpace = copyEvaluatorParameterSpace(evaluatorParameterSpace)
	c1 = 1.220703125e-04
	alpha0 = 1.0
	phi0 = evaluatorValue(evaluatorParameterSpace)
	for i, parameterName in enumerate(freeParameterNames):
		evaluatorParameterSpace[parameterName] += pk[i]
	phi_a0 = evaluatorValue(evaluatorParameterSpace)
	derphi0 = 0.0
	for i, item in enumerate(pk):
		derphi0 += gfk[i] * item

	if (phi_a0 <= phi0 + c1 * derphi0):
		updateEvaluatorParameterSpace(originalSpace, evaluatorParameterSpace)
		return 1.0

	### Otherwise compute the minimizer of a quadratic interpolant:
	updateEvaluatorParameterSpace(originalSpace, evaluatorParameterSpace)
	alpha1 = -derphi0 / 2.0 / (phi_a0 - phi0 - derphi0)
	for i, parameterName in enumerate(freeParameterNames):
		evaluatorParameterSpace[parameterName] += alpha1 * pk[i]
	phi_a1 = evaluatorValue(evaluatorParameterSpace)

	if (phi_a1 <= phi0 + c1 * alpha1 * derphi0):
		updateEvaluatorParameterSpace(originalSpace, evaluatorParameterSpace)
		return alpha1

	### Otherwise loop with cubic interpolation until we find an alpha which satifies the first Wolfe condition.
	### (since we are backtracking, we will assume that the value of alpha is not too small and satisfies the second condition.)

	### we are assuming pk is a descent direction
	while 1:
		factor = alpha0 * alpha0 * alpha1 * alpha1 * (alpha1 - alpha0)
		a = 3.0 * (alpha0 * alpha0 * (phi_a1 - phi0 - derphi0 * alpha1) - alpha1 * alpha1 * (phi_a0 - phi0 - derphi0 * alpha0)) / factor
		gradient = (-alpha0 * alpha0 * alpha0 * (phi_a1 - phi0 - derphi0 * alpha1) + alpha1 * alpha1 * alpha1 * (phi_a0 - phi0 - derphi0 * alpha0)) / factor

		alpha2 = (-gradient + sqrt(abs(gradient * gradient - a * derphi0))) / a
		updateEvaluatorParameterSpace(originalSpace, evaluatorParameterSpace)
		for i, parameterName in enumerate(freeParameterNames):
			evaluatorParameterSpace[parameterName] += alpha2 * pk[i]
		phi_a2 = evaluatorValue(evaluatorParameterSpace)

		if (phi_a2 <= phi0 + c1 * alpha2 * derphi0):
			updateEvaluatorParameterSpace(originalSpace, evaluatorParameterSpace)
			return alpha2

		if (alpha1 - alpha2 > alpha1 / 2.0) or (1.0 - alpha2 / alpha1 < 0.96):
			alpha2 = alpha1 / 2.0

		alpha0 = alpha1
		alpha1 = alpha2
		phi_a0 = phi_a1
		phi_a1 = phi_a2

def fmin_ncg(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, freeParameterNames, limits, constraints, freeIndices, fixedIndices, display = False, averageDifference = 6.0554544523933479e-06, maxIteration = None):
	"""Modified Newton's method and uses a conjugate gradient algorithm to (approximately) invert the local Hessian.

	[Description]

	# This is based on Travis E. Oliphant's and Scipy's optimize.py modules
	# and modified by Koji KISHIMOTO.
	# ******NOTICE***************
	# optimize.py module by Travis E. Oliphant
	#
	# You may copy and use this module as you see fit with no
	# guarantee implied provided you keep this notice in all copies.
	# *****END NOTICE************

	Minimize the function by using the Newton-CG method.
	See Wright, and Nocedal 'Numerical Optimization', 1999, pg. 140.
	You can bound, constraint and/or fix variables.

	[Inputs]

	evaluatorValue
	   the IFunction's method to get value.

	evaluatorGradient
	   the IFunction's method to get gradient.

	evaluatorHessian
	   the IFunction's method to get hessian.

	evaluatorParameterSpace
	   the IFunction's parameter name space.
	
	freeParameterNames
	   parameter names neither constrained nor fixed.

	limits
	   list of sub-list [lowerEdge, upperEdge] for all parameters.
	   usage:
	      x = [1.0, 2.0]
	      limits = [[0.0, 3.0], [None, 5.0]]
	   [lowerEdge, upperEdge] : lowerEdge <= v <= upperEdge
	   [None, upperEdge]      : v <= upperEdge
	   [lowerEdge, None]      : lowerEdge <= v
	   [None, None]           : free

	constraints
	   list of parameter constraint expressions.
	   usage:
	      constant = 1.0
	      amplitude = 2.0
	      mean = 3.0
	      sigma = 4.0
	      constraints = ['constant = amplitude', 'mean = 3.0 * sigma']
	         in this case, parameters are finally set to:
	            constant = 2.0
	            amplitude = 2.0
	            mean = 12.0
	            sigma = 4.0
	   if constraints is set to [], all parameters are assumed to be unconstrained.

	freeIndices
	   list of free parameter indices.
	
	fixedIndices
	   list of fixed parameter indices.

	display
	   True to print convergence messages.

	averageDifference
	   convergence is assumed when the average relative error in the minimizer falls below this amount.
	   totalDefference = averageDifference * len(freeIndices)

	maxIteration
	   the maximum number of iterations to perform.

	[Outputs]

	   fval, hessian, warnflag, mesg

	   fval -- value of function at minimum
	   hessian -- hessian of function at minimum
	   warnflag -- Integer warning flag:
	      1 : 'Maximum number of iterations.'
	   mesg -- result message
	"""

	_o2i(evaluatorParameterSpace, limits, freeIndices, freeParameterNames)
	evaluatorValue, evaluatorGradient, evaluatorHessian = _wrap(limits, constraints, freeIndices, freeParameterNames, evaluatorValue, evaluatorGradient, evaluatorHessian)

	nFreeParameters = len(freeIndices)
	if maxIteration == None:
		maxIteration = nFreeParameters * 200
	totalDifference = nFreeParameters * averageDifference
	currentDifference = 2.0 * totalDifference
	nIterations = 0

	while 1:
		### Loop check.
		if (currentDifference <= totalDifference) or (nIterations >= maxIteration):
			break

		### Compute a search direction by applying the CG method.
		gradient = map(evaluatorGradient, [evaluatorParameterSpace] * nFreeParameters, freeIndices)
		maggrad = 0.0
		psupi = []
		dri0 = 0.0
		for item in gradient:
			maggrad += abs(item)
			psupi.append(-item)
			dri0 += item * item
		termcond = min([0.5, sqrt(maggrad)]) * maggrad
		xsupi = [0.0] * nFreeParameters
		ri = gradient[:]

		"""
		### Straightforward calculation.
		hessian = []
		for j, jIndex in enumerate(freeIndices):
			temp = []
			for k, kIndex in enumerate(freeIndices):
				temp.append(evaluatorHessian(evaluatorParameterSpace, jIndex, kIndex))
			hessian.append(temp)
		from paida.math.array.matrix import matrix
		inverseHessian = matrix(hessian, link = True).inverse()
		for j, jItem in enumerate(inverseHessian):
			for k, kItem in enumerate(gradient):
				xsupi[j] += -jItem[k] * kItem
		"""

		hessianRanges = []
		for j, jIndex in enumerate(freeIndices):
			tempRange = []
			for k, kIndex in enumerate(freeIndices[j + 1:]):
				tempRange.append((j, k + j + 1, evaluatorHessian(evaluatorParameterSpace, jIndex, kIndex)))
			hessianRanges.append((j, evaluatorHessian(evaluatorParameterSpace, jIndex, jIndex), tempRange))

		innerFlag = False
		while 1:
			### Loop check.
			termcond2 = 0.0
			for item in ri:
				termcond2 += abs(item)
			if termcond2 <= termcond:
				break

			Ap = [0.0] * nFreeParameters
			for (i, valueI, tempRange) in hessianRanges:
				Ap[i] += psupi[i] * valueI
				for (j, k, valueJK) in tempRange:
					Ap[j] += psupi[k] * valueJK
					Ap[k] += psupi[j] * valueJK

			### Check curvature.
			curv = 0.0
			for j, item in enumerate(Ap):
				curv += psupi[j] * item
			if curv == 0.0:
				break
			elif curv < 0.0:
				if innerFlag:
					break
				else:
					alphai = dri0 / curv
					for j, item in enumerate(psupi):
						xsupi[j] += alphai * item
					break
			alphai = dri0 / curv
			dri1 = 0.0
			for j, item in enumerate(ri):
				xsupi[j] += alphai * psupi[j]
				ri[j] += alphai * Ap[j]
				dri1 += item * item
			betai = dri1 / dri0
			for j, item in enumerate(psupi):
				psupi[j] = betai * item - ri[j]
			innerFlag = True
			dri0 = dri1

		### Search direction is solution to system.
		alphak = line_search_BFGS(evaluatorValue, evaluatorParameterSpace, freeParameterNames, xsupi, gradient)

		currentDifference = 0.0
		for j, parameterName in enumerate(freeParameterNames):
			value = alphak * xsupi[j]
			evaluatorParameterSpace[parameterName] += value
			currentDifference += abs(value)
		nIterations += 1

	fval = evaluatorValue(evaluatorParameterSpace)
	hessian = []
	for j in range(nFreeParameters):
		hessian.append([0.0] * nFreeParameters)
	for j, jIndex in enumerate(freeIndices):
		hessian[j][j] = evaluatorHessian(evaluatorParameterSpace, jIndex, jIndex)
		for k, kIndex in enumerate(freeIndices[j + 1:]):
			value = evaluatorHessian(evaluatorParameterSpace, jIndex, kIndex)
			hessian[j][k + j + 1] = value
			hessian[k + j + 1][j] = value

	_i2o(evaluatorParameterSpace, limits, freeIndices, freeParameterNames)

	if nIterations >= maxIteration:
		warnflag = 1
		mesg = "Maximum number of iterations has been exceeded."
		if display:
			print mesg
			print "\tCurrent function value: %f" % fval
			print "\tIterations: %d" % nIterations
	else:
		warnflag = 0
		mesg = "Optimization terminated successfully."
		if display:
			print mesg
			print "\tCurrent function value: %f" % fval
			print "\tIterations: %d" % nIterations

	return fval, hessian, warnflag, mesg

class _Evaluator:
	def __init__(self, evaluatorParameterSpace, freeParameterNames, freeIndices, evaluatorGradient):
		self._evaluatorParameterSpace = evaluatorParameterSpace
		self._freeParameterNames = freeParameterNames
		self._freeIndices = freeIndices
		self._evaluatorGradient = evaluatorGradient

	def set(self, individual):
		evaluatorParameterSpace = self._evaluatorParameterSpace
		for i, parameterName in enumerate(self._freeParameterNames):
			evaluatorParameterSpace[parameterName] = individual[i]

	def evaluate(self):
		evaluatorParameterSpace = self._evaluatorParameterSpace
		difference = 0.0
		for i in self._freeIndices:
			difference += self._evaluatorGradient(evaluatorParameterSpace, i)
		return difference

def geneticAlgorithm(evaluatorValue, evaluatorGradient, evaluatorHessian, evaluatorParameterSpace, freeParameterNames, limits, constraints, freeIndices, fixedIndices, ndf, display = False, averageDifference = 6.0554544523933479e-06, maxIteration = None):
	"""Genetic algorithm for global optimization.

	ndf
	   number of degrees of freedom

	See "fmin_ncg()" for explanations of other parameters.
	"""

	### Number of individuals
	nIndividuals = 300
	### Number of islands
	nIslands = 10
	### Dimenstion
	dimension = len(freeIndices)
	### Number of Crossover
	nCrossovers = 200 / nIslands
	### Loop limit
	if maxIteration == None:
		maximumGeneration = dimension * 2000
	else:
		maximumGeneration = maxIteration
	### Expand ratio
	expandRatio = 1.2
	### Migration interval
	migrationInterval = 5
	### Migration rate
	migrationRate = 0.5
	### Initial rate
	initialRate = 0.1

	### Initialization
	totalDifference = dimension * averageDifference
	_o2i(evaluatorParameterSpace, limits, freeIndices, freeParameterNames)
	generator = random.Random()
	population = nIndividuals / nIslands
	nMigrators = int(population * migrationRate)
	nInitials = int(population * initialRate)

	migrationService = _MigrationService(generator)
	for i in range(nIslands):
		threadEvaluatorParameterSpace = copyEvaluatorParameterSpace(evaluatorParameterSpace)
		evaluatorValue, evaluatorGradient, evaluatorHessian = _wrap(limits, constraints, freeIndices, freeParameterNames, evaluatorValue, evaluatorGradient, evaluatorHessian)
		evaluator = _Evaluator(threadEvaluatorParameterSpace, freeParameterNames, freeIndices, evaluatorGradient)
		island = _Island()
		island.set(migrationService,
			freeIndices,
			freeParameterNames,
			threadEvaluatorParameterSpace,
			evaluator,
			evaluatorValue,
			evaluatorHessian,
			generator,
			population,
			nInitials,
			nCrossovers,
			expandRatio,
			migrationInterval,
			nMigrators,
			totalDifference,
			maximumGeneration,
			display,
			ndf)

		result = island.getResult()
		if result != None:
			### Got answer.
			fval, hessian, warnflag, mesg = result
			_i2o(threadEvaluatorParameterSpace, limits, freeIndices, freeParameterNames)
			updateEvaluatorParameterSpace(threadEvaluatorParameterSpace, evaluatorParameterSpace)
			return fval, hessian, warnflag, mesg
		else:
			migrationService.addIsland(island)

	for island in migrationService.getIslands():
		island.start()

	while 1:
		condition = migrationService.getCondition()
		condition.acquire()
		condition.wait()
		for island in migrationService.getIslands()[:]:
			if not island.isAlive():
				### Terminated.
				migrationService.removeIsland(island)
				### Got solution?
				lock = island.getLock()
				lock.acquire()
				result = island.getResult()
				lock.release()
				if result != None:
					### Yes.
					for island2 in migrationService.getIslands():
						island2.terminate()
					fval, hessian, warnflag, mesg = result
					if display:
						print mesg
					threadEvaluatorParameterSpace = island.getEvaluatorParameterSpace()
					_i2o(threadEvaluatorParameterSpace, limits, freeIndices, freeParameterNames)
					updateEvaluatorParameterSpace(threadEvaluatorParameterSpace, evaluatorParameterSpace)
					condition.release()
					return fval, hessian, warnflag, mesg
				elif len(migrationService.getIslands()) == 0:
					### All failed.
					evaluator.set(best)
					fval = evaluationMinimum
					hessian = []
					for j in range(dimension):
						hessian.append([0.0] * dimension)
					for j, jIndex in enumerate(freeIndices):
						hessian[j][j] = evaluatorHessian(evaluatorParameterSpace, jIndex, jIndex)
						for k, kIndex in enumerate(freeIndices[j + 1:]):
							value = evaluatorHessian(evaluatorParameterSpace, jIndex, kIndex)
							hessian[j][k + j + 1] = value
							hessian[k + j + 1][j] = value
					warnflag = 1
					mesg = "Maximum number of iterations has been exceeded."
					if display:
						print mesg
					threadEvaluatorParameterSpace = island.getEvaluatorParameterSpace()
					_i2o(threadEvaluatorParameterSpace, limits, freeIndices, freeParameterNames)
					updateEvaluatorParameterSpace(threadEvaluatorParameterSpace, evaluatorParameterSpace)
					condition.release()
					return fval, hessian, warnflag, mesg
		condition.release()

class _MigrationService:
	def __init__(self, generator):
		self._islands = []
		self._generator = generator
		self._condition = threading.Condition()

	def addIsland(self, island):
		self._islands.append(island)

	def removeIsland(self, island):
		self._islands.remove(island)

	def getIslands(self):
		return self._islands

	def selectIsland(self):
		return self._generator.choice(self._islands)

	def getCondition(self):
		return self._condition

class _Island(threading.Thread):
	def set(self,
			migrationService,
			freeIndices,
			freeParameterNames,
			evaluatorParameterSpace,
			evaluator,
			evaluatorValue,
			evaluatorHessian,
			generator,
			population,
			nInitials,
			nCrossovers,
			expandRatio,
			migrationInterval,
			nMigrators,
			totalDifference,
			maximumGeneration,
			display,
			ndf):

		self._migrationService = migrationService
		self._freeIndices = freeIndices
		self._freeParameterNames = freeParameterNames
		self._evaluatorParameterSpace = evaluatorParameterSpace
		self._evaluator = evaluator
		self._evaluatorValue = evaluatorValue
		self._evaluatorHessian = evaluatorHessian
		self._generator = generator
		self._population = population
		self._nCrossovers = nCrossovers
		self._expandRatio = expandRatio
		self._migrationInterval = migrationInterval
		self._nMigrators = nMigrators
		self._totalDifference = totalDifference
		self._maximumGeneration = maximumGeneration
		self._display = display
		self._ndf = ndf

		evaluationMaximum = ndf * 10.0
		self._evaluationMaximum = evaluationMaximum

		islanders = []
		for i in range(nInitials):
			individual = []
			for parameterName in freeParameterNames:
				individual.append(evaluatorParameterSpace[parameterName])
			islanders.append(individual)
		for i in range(population - nInitials):
			individual = []
			for parameterName in freeParameterNames:
				value = evaluatorParameterSpace[parameterName] * 10**((generator.random() - 0.5) * 6)
				if generator.choice([True, False]):
					individual.append(value)
				else:
					individual.append(-value)
			islanders.append(individual)
		self._islanders = islanders

		### Evaluation
		best = []
		for parameterName in freeParameterNames:
			best.append(evaluatorParameterSpace[parameterName])
		evaluationMinimum = evaluatorValue(evaluatorParameterSpace)
		for individual in islanders:
			evaluator.set(individual)
			value = evaluatorValue(evaluatorParameterSpace)
			if value < evaluationMinimum:
				best = individual
				evaluationMinimum = value

		result = None
		if evaluationMinimum < evaluationMaximum:
			evaluator.set(best)
			if abs(evaluator.evaluate()) < totalDifference:
				fval = evaluationMinimum
				hessian = []
				for i in range(dimension):
					hessian.append([0.0] * dimension)
				for i, iIndex in enumerate(freeIndices):
					hessian[i][i] = evaluatorHessian(evaluatorParameterSpace, iIndex, iIndex)
					for j, jIndex in enumerate(freeIndices[i + 1:]):
						value = evaluatorHessian(evaluatorParameterSpace, iIndex, jIndex)
						hessian[i][j + i + 1] = value
						hessian[j + i + 1][i] = value
				warnflag = 0
				mesg = "Optimization terminated successfully."
				result = (fval, hessian, warnflag, mesg)
		self.setResult(result)

		self._terminate = False
		migrators = []
		for i in range(nMigrators):
			migrators.append(generator.choice(islanders))
		self.setMigrators(migrators)
		self._lock = threading.Lock()

	def setResult(self, result):
		self._result = result

	def getResult(self):
		return self._result

	def getEvaluatorParameterSpace(self):
		return self._evaluatorParameterSpace

	def run(self):
		migrationService = self._migrationService
		freeIndices = self._freeIndices
		freeParameterNames = self._freeParameterNames
		evaluatorParameterSpace = self._evaluatorParameterSpace
		evaluator = self._evaluator
		evaluatorValue = self._evaluatorValue
		evaluatorHessian = self._evaluatorHessian
		generator = self._generator
		population = self._population
		nCrossovers = self._nCrossovers
		expandRatio = self._expandRatio
		migrationInterval = self._migrationInterval
		nMigrators = self._nMigrators
		totalDifference = self._totalDifference
		maximumGeneration = self._maximumGeneration
		islanders = self._islanders
		display = self._display
		ndf = self._ndf
		evaluationMaximum = self._evaluationMaximum

		generation = 0
		dimension = len(freeIndices)
		nRanks = 2.0 * nCrossovers

		while (generation != maximumGeneration) and (not self._terminate):
			### Selection for reproduction
			parent0 = generator.choice(islanders)
			parent1 = generator.choice(islanders)

			### Crossover
			children = []
			for i in range(nCrossovers):
				child0 = []
				child1 = []
				for j in range(dimension):
					length = abs(parent0[j] - parent1[j]) * expandRatio
					sigma = length / 4.0
					child0.append(generator.normalvariate(parent0[j], sigma))
					child1.append(generator.normalvariate(parent1[j], sigma))
				children.append(child0)
				children.append(child1)

			### Selection for survival
			evaluator.set(parent0)
			evaluationParent0 = evaluatorValue(evaluatorParameterSpace)
			evaluator.set(parent1)
			evaluationParent1 = evaluatorValue(evaluatorParameterSpace)
			if evaluationParent0 < evaluationParent1:
				best = parent0
				evaluationMinimum = evaluationParent0
			else:
				best = parent1
				evaluationMinimum = evaluationParent1
			evaluationChildren = []
			for child in children:
				evaluator.set(child)
				evaluationChild = evaluatorValue(evaluatorParameterSpace)
				if evaluationChild <= evaluationMinimum:
					best = child
					evaluationMinimum = evaluationChild
				evaluationChildren.append(evaluationChild)

			if evaluationMinimum < evaluationMaximum:
				evaluator.set(best)
				if abs(evaluator.evaluate()) < totalDifference:
					fval = evaluationMinimum
					hessian = []
					for j in range(dimension):
						hessian.append([0.0] * dimension)
					for j, jIndex in enumerate(freeIndices):
						hessian[j][j] = evaluatorHessian(evaluatorParameterSpace, jIndex, jIndex)
						for k, kIndex in enumerate(freeIndices[j + 1:]):
							value = evaluatorHessian(evaluatorParameterSpace, jIndex, kIndex)
							hessian[j][k + j + 1] = value
							hessian[k + j + 1][j] = value
					warnflag = 0
					mesg = "Optimization terminated successfully."
					result = (fval, hessian, warnflag, mesg)
					lock = self.getLock()
					lock.acquire()
					self.setResult(result)
					lock.release()
					condition = migrationService.getCondition()
					condition.acquire()
					condition.notifyAll()
					condition.release()
					return

			if best == parent0:
				children.append(parent1)
				evaluationChildren.append(evaluationParent1)
			elif best == parent1:
				children.append(parent0)
				evaluationChildren.append(evaluationParent0)
			else:
				children.remove(best)
				children.append(parent0)
				children.append(parent1)
				evaluationChildren.remove(evaluationMinimum)
				evaluationChildren.append(evaluationParent0)
				evaluationChildren.append(evaluationParent1)
			sorted = evaluationChildren[:]
			sorted.sort()
			while 1:
				lucky = generator.choice(children)
				luckyIndex = children.index(lucky)
				rank = sorted.index(evaluationChildren[luckyIndex])
				if generator.random() / 3.0 > rank / nRanks:
					break
			islanders[islanders.index(parent0)] = best
			islanders[islanders.index(parent1)] = lucky

			### Migration
			generation += 1
			if generation % migrationInterval == 0:
				migratorIndices = []
				migrators = []
				for i in range(nMigrators):
					migratorIndex = generator.randrange(population)
					migratorIndices.append(migratorIndex)
					migrators.append(islanders[migratorIndex])

				### Special migrator
				migrators[-1] = best

				self.setMigrators(migrators)

				migrators = migrationService.selectIsland().getMigrators()
				for i, migratorIndex in enumerate(migratorIndices):
					islanders[migratorIndex] = migrators[i]

			if display:
				print self, generation
				print best, evaluationMinimum / ndf

		condition = migrationService.getCondition()
		condition.acquire()
		condition.notifyAll()
		condition.release()

	def setMigrators(self, migrators):
		self._migrators = migrators

	def getMigrators(self):
		return self._migrators

	def getLock(self):
		return self._lock

	def terminate(self):
		self._terminate = True
