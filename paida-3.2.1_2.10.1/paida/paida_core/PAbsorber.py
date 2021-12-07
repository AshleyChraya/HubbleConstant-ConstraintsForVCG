### enumerate
try:
	_temp = enumerate
except NameError:
	def enumerate(data):
		result = []
		i = 0
		for item in data:
			result.append((i, item))
			i += 1
		return result

### True, False
try:
	_temp = True
	_temp = False
except NameError:
	True = 1
	False = 0

### bool
try:
	_temp = bool
except NameError:
	def bool(data):
		if data in [0, [], {}, (), '', None, False]:
			return False
		else:
			return True

### object
try:
	_temp = object
except NameError:
	class object:
		pass

### StringTypes
try:
	import types
	_temp = types.StringTypes
except AttributeError:
	types.StringTypes = (types.StringType, types.UnicodeType)

### file()
try:
	_temp = file
except NameError:
	file = open

### isinstance()
try:
	_temp = isinstance('', ())
except TypeError:
	import types
	_originalIsinstance = isinstance
	def isinstance(data0, data1):
		if data1.__class__.__name__ == types.TupleType.__name__:
			for item in data1:
				if _originalIsinstance(data0, item):
					return True
			else:
				return False
		else:
			return _originalIsinstance(data0, data1)

### sum()
try:
	_temp = sum
except NameError:
	import operator
	def sum(data, start = 0):
		return reduce(operator.add, data, start)

try:
	del _temp
except:
	pass
