from paida.paida_core.PAbsorber import *
import optparse
import os

def getGuiEngineName():
	return _guiEngineName

def setGuiEngineName(guiEngineName):
	if guiEngineName == 'firefox':
		pass
	elif guiEngineName == 'matplotlib':
		pass
	elif guiEngineName == 'tkinter':
		try:
			import Tkinter
		except ImportError:
			print 'PAIDA: "tkinter" GUI engine is unavailable.'
			print 'PAIDA: "batch" GUI engine is selected.'
			guiEngineName = 'batch'
	elif guiEngineName == 'swing':
		pass
	elif guiEngineName == 'batch':
		pass
	else:
		print 'PAIDA: "%s" GUI engine was not found.' % guiEngineName
		print 'PAIDA: "batch" GUI engine is selected.'
		guiEngineName = 'batch'
	global _guiEngineName
	_guiEngineName = guiEngineName

### Check GUI option.
from paida.paida_core.IConstants import IConstants
parser = optparse.OptionParser(
	version = "PAIDA %d.%d.%d (supports AIDA %d.%d.%d)" % 
	(IConstants.PAIDA_VERSION_MAJOR,
	 IConstants.PAIDA_VERSION_MINOR,
	 IConstants.PAIDA_VERSION_BUGFIX,
	 IConstants.AIDA_VERSION_MAJOR,
	 IConstants.AIDA_VERSION_MINOR,
	 IConstants.AIDA_VERSION_BUGFIX))
parser.add_option('--gui', dest = 'gui', default = 'default', help = 'specify GUI engine')
def parser_error(dummy):
	pass
def parser_exit():
	### This enables other applications to handle "-h" option later.
	pass
parser.error = parser_error
parser.exit = parser_exit
(options, args) = parser.parse_args()
if options.gui == 'default':
	if os.name == 'java':
		setGuiEngineName('swing')
	else:
		setGuiEngineName('tkinter')
else:
	setGuiEngineName(options.gui)
