from paida.paida_core.PAbsorber import *
from paida.paida_core.IFitParameterSettings import *
from paida.paida_core.PExceptions import *

class IFitResult:
	def __init__(self):
		### Always available.
		self._fittedParameterNames = None
		self._fitParameterSettings = None
		self._constraints = None
		self._ndf = None
		self._fitMethodName = None
		self._engineName = None
		self._isValid = None
		self._fitStatus = None
		self._dataDescription = None

		### Available only when the solution is found.
		self._fittedParameters = None
		self._fittedFunction = None
		self._quality = None
		self._covMatrixElement = None
		self._errors = None
		self._errorsPlus = None
		self._errorsMinus = None
	
	def isValid(self):
		return bool(self._isValid)
	
	def fitStatus(self):
		"""
		0: Successful.
		1: The solution is not found.
		2: The solution and parabolic error are found, but asymmetric error is invalid.
		3: The solution is found, but parabolic error is invalid.
		4: Unknown error has occured.
		"""

		return self._fitStatus

	def fittedFunction(self):
		return self._fittedFunction
	
	def quality(self):
		return self._quality
	
	def ndf(self):
		return self._ndf
	
	def covMatrixElement(self, i ,j):
		try:
			return self._covMatrixElement[i][j]
		except IndexError:
			l = len(self._covMatrixElement)
			if l == 0:
				m = 0
			else:
				m = len(self._covMatrixElement[0])
			raise IllegalArgumentException('Specified index (%s, %s) is not in range of (%s, %s).' % (i, j, l - 1, m - 1))
	
	def fitMethodName(self):
		return self._fitMethodName

	def engineName(self):
		return self._engineName

	def dataDescription(self):
		return self._dataDescription
	
	def constraints(self):
		return self._constraints[:]
	
	def fitParameterSettings(self, name):
		if not self._fitParameterSettings.has_key(name):
			self._fitParameterSettings[name] = IFitParameterSettings(name)
		return self._fitParameterSettings[name]

	def fittedParameters(self):
		return list(self._fittedParameters)
	
	def fittedParameterNames(self):
		return self._fittedParameterNames[:]

	def fittedParameter(self, name):
		return self.fittedParameters()[self.fittedParameterNames().index(name)]

	def errors(self):
		return list(self._errors)

	def errorsPlus(self):
		return list(self._errorsPlus)

	def errorsMinus(self):
		return list(self._errorsMinus)
