from paida.paida_core.PAbsorber import *
from paida.paida_core.IFitter import *
from paida.paida_core.IFitData import *
from paida.paida_core.PExceptions import *
from paida.paida_core.PUtilities import *

import types

class IFitFactory:

	def createFitData(self):
		return IFitData()
	
	def createFitter(self, data1 = None, data2 = None, data3 = None):
		if (data1 == None) and (data2 == None) and (data3 == None):
			method = 'Chi2'
			engine = 'SimplePAIDA'
			options = optionAnalyzer(None)
		elif (type(data1) in types.StringTypes) and (data2 == None) and (data3 == None):
			method = data1
			engine = 'SimplePAIDA'
			options = optionAnalyzer(None)
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and (data3 == None):
			method = data1
			engine = data2
			options = optionAnalyzer(None)
		elif (type(data1) in types.StringTypes) and (type(data2) in types.StringTypes) and (type(data3) in types.StringTypes):
			method = data1
			engine = data2
			options = optionAnalyzer(data3)
		else:
			raise IllegalArgumentException()

		### Method check.
		methods = ['LeastSquares', 'Chi2', 'CleverChi2', 'BinnedMaximumLikelihood', 'UnbinnedMaximumLikelihood']
		if not method in methods:
			raise IllegalArgumentException('The name does not correspond to a valid methods %s.' % methods)

		### Engine check.
		engines = ['SimplePAIDA', 'PAIDA']
		if not engine in engines:
			raise IllegalArgumentException('The name does not correspond to a valid engines %s.' % engines)

		### Create fitter.
		return IFitter(method, engine, options)
