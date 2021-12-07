from paida.paida_core.PAbsorber import *
from paida.paida_core.IConstants import *
from paida.paida_core.PExceptions import *
from paida.paida_core.PUtilities import *
from paida.paida_core.ITree import *

import types
import os

_initialXml = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE aida SYSTEM "http://aida.freehep.org/schemas/3.2.1/aida.dtd">
<aida version="%s">
	<implementation package="PAIDA" version="%s"/>
</aida>""" % (IConstants.AIDA_VERSION, IConstants.PAIDA_VERSION)

class ITreeFactory:
	""" The creator of trees """
	def create(self, storeName='', storeType='xml', readOnly=False, createNew=True, options=None):
		""" Creates a new tree and associates it with a store. The store is assumed to be read/write. The store will be created if it does not exist.
		Parameters:
			storeName - The name of the store, if empty (""), the tree is created in memory and therefore will not be associated with a file.
			storeType - Implementation specific string, may control store type
			readOnly - If true the store is opened readonly, an exception if it does not exist
			createNew - If false the file must exist, if true the file will be created
			options - Other options, currently are not specified 
		Throws:
			IOException - if the store already exists 
			IllegalArgumentException
		"""

		storeTypes = ['xml']
		storeType = storeType.lower()
		options = optionAnalyzer(options)
		# type-checking the arguments
		if not (type(storeName) in types.StringTypes and type(storeType) in types.StringTypes and readOnly in [True, False] and createNew in [True, False]):
			raise IllegalArgumentException('Illegal arguments.')

		# if no storename is given, we need new defaults.
		# read-only mode and don't create a new file
		if not storeName:
			readOnly = True
			createNew = False
			storeName = None

		if storeType not in storeTypes:
			raise IllegalArgumentException('Store type "%s" is not in %s.' % (storeType, storeTypes))
		if readOnly:
			if storeName and (not os.path.exists(storeName)):
				raise IOException('%s does not exist.' % storeName)
		else:
			if createNew:
				storeFile = open(storeName, 'w')
				storeFile.write(_initialXml)
				storeFile.close()
			elif not os.path.exists(storeName):
				raise IOException('%s does not exist.' % storeName)
		return ITree(storeName, storeType, readOnly, options)
