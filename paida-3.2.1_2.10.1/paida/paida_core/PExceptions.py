from paida.paida_core.PAbsorber import *
display = True

class BaseException:
	def __init__(self, message = None):
		self.message = message
		if display == True:
			self.notify()

	def notify(self):
		message = self.getMessage()
		if message == None:
			message = '(No exception message)'
		print ' #########################'
		print ' #   Exception Message   #'
		print ' #########################'
		print ' ' + self.__class__.__name__
		print ' ========================='
		print ' ' + message
		print ' #########################'
		print ''
		
	def getMessage(self):
		return self.message

class IllegalArgumentException(BaseException):
	pass

class AlreadyConvertedException(BaseException):
	pass

class OutOfStorageException(BaseException):
	pass

class RuntimeException(BaseException):
	pass

class NotImplementedException(BaseException):
	pass

class ClassCastException(BaseException):
	pass

class IOException(BaseException):
	pass
