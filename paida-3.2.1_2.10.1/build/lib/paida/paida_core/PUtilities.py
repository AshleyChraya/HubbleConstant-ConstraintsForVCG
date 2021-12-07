from paida.paida_core.PAbsorber import *

def optionAnalyzer(options):
	### Return options as dictionary.
	if options == None:
		return {}
	if options == '':
		return {}
	globalNameSpace = {}
	globalNameSpace['true'] = True
	globalNameSpace['false'] = False
	globalNameSpace['TRUE'] = True
	globalNameSpace['FALSE'] = False
	globalNameSpace['yes'] = True
	globalNameSpace['no'] = False
	globalNameSpace['YES'] = True
	globalNameSpace['NO'] = False
	globalNameSpace['Yes'] = True
	globalNameSpace['No'] = False
	options = options.replace(';', ',')
	items = options.split(',')
	result = {}
	for item in items:
		expressions = item.split('=')
		left = expressions[0].strip()
		if len(expressions) == 1:
			result[left] = None
		else:
			right = expressions[1].strip()
			try:
				result[left] = float(right)
			except ValueError:
				try:
					result[left] = int(right)
				except ValueError:
					try:
						result[left] = globalNameSpace[right]
					except KeyError:
						result[left] = right
	return result

def optionConstructor(options):
	if options in [{}, None, '']:
		return ''
	result = ''
	for key in options.keys():
		if options[key] == None:
			result += '%s,' % key
		elif options[key] == True:
			result += '%s=true,' % key
		elif options[key] == False:
			result += '%s=false,' % key
		else:
			result += '%s=%s,' % (key, options[key])
	return result[:-1]

class _Shlex(object):
	eof = None

	def __init__(self, data, omitQuotes = True, omitSpaces = False):
		if data in ['', None]:
			self.tokens = []
		else:
			self.tokens = []
			whitespace = ' \t\r\n'
			splitChars = '(){}[]+-*/<>%&,.=|!:;'
			quotes = ["'", '"']
			charList = list(data)
			charList.reverse()
			while 1:
				try:
					char = charList.pop()
				except IndexError:
					break
				else:
					if char in quotes:
						if omitQuotes:
							word = ''
						else:
							word = char
						quote = char
						while 1:
							try:
								char = charList.pop()
							except IndexError:
								self.tokens.append(word)
								break
							else:
								if char == quote:
									if omitQuotes:
										self.tokens.append(word)
										break
									else:
										self.tokens.append(word + char)
										break
								else:
									word += char
					elif char in whitespace:
						if not omitSpaces:
							self.tokens.append(char)
						continue
					elif char in splitChars:
						if char == '.':
							try:
								char = charList.pop()
							except IndexError:
								self.tokens.append(char)
							else:
								if char.isdigit():
									self.tokens.append('0.' + char)
								else:
									self.tokens.append('.')
									self.tokens.append(char)
						else:
							self.tokens.append(char)
						continue
					else:
						word = char
						while 1:
							try:
								char = charList.pop()
							except IndexError:
								self.tokens.append(word)
								break
							else:
								if char in whitespace:
									self.tokens.append(word)
									if not omitSpaces:
										self.tokens.append(char)
									break
								elif char in splitChars:
									if char == '.':
										if word.isdigit():
											word += char
										else:
											self.tokens.append(word)
											self.tokens.append(char)
											break
									else:
										self.tokens.append(word)
										self.tokens.append(char)
										break
								else:
									word += char
		self.tokens.reverse()

	def get_token(self):
		try:
			return self.tokens.pop()
		except IndexError:
			return None

def cExpressionConverter(cExpression, replaces = {}):
	result = ''
	parser = _Shlex(cExpression, omitQuotes = False)
	while 1:
			token = parser.get_token()
			if token == parser.eof:
				break
			elif replaces.has_key(token):
				result += replaces[token]
			### &&
			elif token == '&':
				token = parser.get_token()
				if token == '&':
					result += ' and '
				elif token == parser.eof:
					result += '&'
					break
				else:
					result += '&' + token
			### ||
			elif token == '|':
				token = parser.get_token()
				if token == '|':
					result += ' or '
				elif token == parser.eof:
					result += '|'
					break
				else:
					result += '|' + token
			### !
			elif token == '!':
				token = parser.get_token()
				if token == '=':
					result += '!='
				elif token == parser.eof:
					result += '!'
					break
				else:
					result += ' not ' + token
			### Others.
			else:
				result += token
	return result
