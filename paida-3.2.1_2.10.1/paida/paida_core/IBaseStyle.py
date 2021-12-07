from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import *

import types

class _convertException:
	def __init__(self, message=None):
		if message != None:
			print message

class baseParameter:
	def __init__(self, default):
		self.default = self.convert(default)
		self.reset()

	def reset(self):
		self.value = self.default
		self.setCustomized(False)

	def setCustomized(self, boolean):
		self._customized = boolean

	def getCustomized(self):
		return self._customized

	def setValue(self, value, customize = True):
		self.value = self.convert(value)
		if customize:
			self.setCustomized(True)

	def getValue(self):
		return self.value

	def getValueString(self):
		return str(self.getValue())

class listParameter(baseParameter):
	def __init__(self, default):
		baseParameter.__init__(self, default)

	def convert(self, dataString):
		if isinstance(dataString, types.StringTypes):
			return list(eval(dataString))
		elif isinstance(dataString, types.ListType):
			return dataString
		elif isinstance(dataString, types.TupleType):
			return list(dataString)
		else:
			raise _convertException('The parameter was not converted to list type.')

	def availableOptions(self):
		return ['<list type>']

class listedParameter(baseParameter):
	def __init__(self, default, optionList):
		self.optionList = optionList
		baseParameter.__init__(self, default)

	def convert(self, dataString):
		if dataString in self.optionList:
			return dataString
		else:
			raise _convertException('"%s" is not in %s.' % (dataString, self.optionList))

	def availableOptions(self):
		return self.optionList

class stringParameter(baseParameter):
	def __init__(self, default):
		baseParameter.__init__(self, default)

	def convert(self, dataString):
		try:
			return '%s' % dataString
		except:
			raise _convertException('The parameter was not converted to string type.')

	def availableOptions(self):
		return ['<string type>']

class intParameter(baseParameter):
	def __init__(self, default):
		baseParameter.__init__(self, default)

	def convert(self, dataString):
		try:
			return int(dataString)
		except:
			raise _convertException('"%s" was not converted to int type.' % dataString)

	def availableOptions(self):
		return ['<int type>']

class floatParameter(baseParameter):
	def __init__(self, default):
		baseParameter.__init__(self, default)

	def convert(self, dataString):
		try:
			return float(dataString)
		except:
			raise _convertException('"%s" was not converted to float type.' % dataString)

	def availableOptions(self):
		return ['<float type>']

class booleanParameter(baseParameter):
	def __init__(self, default):
		baseParameter.__init__(self, default)

	def convert(self, dataString):
		if dataString in ['True', 'true', True]:
			return True
		elif dataString in ['False', 'false', False]:
			return False
		else:
			raise _convertException('"%s" is not bool type.' % dataString)

	def availableOptions(self):
		return ['true', 'false', 'True', 'False']

class colorParameter(baseParameter):
	def __init__(self, default):
		baseParameter.__init__(self, default)

	def convert(self, dataString):
		colorChars = dataString.lower()
		if colorChars == '':
			return colorChars
		elif (dataString[0] == '#') and (len(dataString) in [4, 7, 10, 13]):
			for colorChar in colorChars[1:]:
				if not colorChar in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
					raise _convertException('"%s" is invalid color string.' % dataString)
			return colorChars
		elif colorChars in ['white', 'black', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow']:
			return colorChars
		else:
			raise _convertException('"%s" is invalid color string.' % dataString)

	def availableOptions(self):
		return ['<#rgb>', '<#rrggbb>', '<#rrrgggbbb>', '<#rrrrggggbbbb>', 'white', 'black', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow', '']

class intRangeParameter(intParameter):
	def __init__(self, default, lower, upper):
		self.lower = lower
		self.upper = upper
		intParameter.__init__(self, default)

	def convert(self, dataString):
		data = intParameter.convert(self, dataString)
		if self.lower <= data <= self.upper:
			return data
		else:
			raise _convertException('"%s" is not between %i and %i.' % (dataString, self.lower, self.upper))

	def availableOptions(self):
		return ['<%i <= int type <= %i>' % (self.lower, self.upper)]

class floatRangeParameter(floatParameter):
	def __init__(self, default, lower, upper):
		self.lower = lower
		self.upper = upper
		floatParameter.__init__(self, default)

	def convert(self, dataString):
		data = floatParameter.convert(self, dataString)
		if self.lower <= data <= self.upper:
			return data
		else:
			raise _convertException('"%s" is not between %f and %f.' % (dataString, self.lower, self.upper))

	def availableOptions(self):
		return ['<%i <= float type <= %i>' % (self.lower, self.upper)]

class styleParameter(baseParameter):
	def __init__(self, default, styleName):
		self.defaultClass = default
		self.styleName = styleName
		baseParameter.__init__(self, default())

	def convert(self, dataString):
		if dataString.__class__.__name__ == self.styleName:
			return dataString
		else:
			raise _convertException('The parameter is not %s.' % self.styleName)

	def availableOptions(self):
		return ['<%s>' % self.styleName]

	def reset(self):
		self.default = self.convert(self.defaultClass())
		self.value = self.default

class fontParameter(baseParameter):
	def __init__(self):
		baseParameter.__init__(self, defaultFont)

	def convert(self, dataString):
		if dataString in fontList:
			return dataString
		else:
			raise _convertException('"%s" is not in %s.' % (dataString, fontList))

	def availableOptions(self):
		return fontList[:]

class IBaseStyle:

	def __init__(self):
		self._parameters = {}

	def _setType(self, parameterName, typeData):
		self._parameters[parameterName] = typeData

	def _getType(self, parameterName):
		return self._parameters[parameterName]

	def availableParameters(self):
		names = self._parameters.keys()
		names.sort()
		return names

	def availableParameterOptions(self, parameterName):
		availables = self.availableParameters()
		if parameterName in availables:
			return self._getType(parameterName).availableOptions()
		else:
			raise IllegalArgumentException('Parameter %s is not in %s.' % (parameterName, availables))

	def parameterValue(self, parameterName):
		availables = self.availableParameters()
		if parameterName in availables:
			return self._getType(parameterName).getValueString()
		else:
			raise IllegalArgumentException('Parameter %s is not in %s.' % (parameterName, availables))

	def _parameterData(self, parameterName):
		return self._getType(parameterName).getValue()

	def reset(self):
		for parameterName in self.availableParameters():
			self._getType(parameterName).reset()

	def setParameter(self, parameterName, options = None, customize = True):
		if not parameterName in self.availableParameters():
			return False
		else:
			if options == None:
				self._getType(parameterName).reset()
			else:
				try:
					self._getType(parameterName).setValue(options, customize)
				except _convertException:
					return False
			return True

	def _setCustomized(self, parameterName, boolean):
		self._getType(parameterName).setCustomized(boolean)

	def _getCustomized(self, parameterName):
		return self._getType(parameterName).getCustomized()


import paida.paida_gui.PRoot
if not locals().has_key('fontList'):
	fontList, defaultFont = paida.paida_gui.PRoot.getFontList(['Courier', 'courier'])
