from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import *
from paida.paida_core.ITitleStyle import *
from paida.paida_core.IBaseStyle import stringParameter, listedParameter, booleanParameter
from paida.paida_core.IPlotterRegion import *
from paida.paida_core.IConstants import *
import paida.paida_gui.PRoot as PRoot
import paida.paida_gui.PGuiSelector as PGuiSelector

import types
import time
import os

N = PRoot.N
NE = PRoot.NE
E = PRoot.E
SE = PRoot.SE
S = PRoot.S
SW = PRoot.SW
W = PRoot.W
NW = PRoot.NW
CENTER = PRoot.CENTER

class IPlotter:
	def __init__(self):
		self._serialNumber = 0
		self._regions = []
		self._allRegions = []
		self._currentRegionNumber = 0

		self._parameters = {}
		self._setType('viewHeight', stringParameter('210m'))
		self._setType('viewWidth', stringParameter('297m'))
		self._setType('height', stringParameter('210m'))
		self._setType('width', stringParameter('297m'))
		self._setType('landscape', booleanParameter(True))
		self._setType('swap', booleanParameter(False))
		self._setType('paper', listedParameter('A4', ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'Letter', 'Legal', 'Tabloid', 'Hagaki']))

		self.setTitleStyle(ITitleStyle())

		self._tabX = 0.01
		self._tabY = 0.01

		self._setGuiPlotter(PRoot.getRoot()._requestPlotter(self._parameterData('viewWidth'), self._parameterData('viewHeight'), self._parameterData('width'), self._parameterData('height')))

	def __del__(self):
		self._getGuiPlotter().terminate()
		self._setGuiPlotter(None)

	def _setGuiPlotter(self, guiPlotter):
		self._guiPlotter = guiPlotter

	def _getGuiPlotter(self):
		return self._guiPlotter

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

	def _setParameter(self, parameterName, options):
		if not parameterName in self.availableParameters():
			return False
		else:
			if options == None:
				self._getType(parameterName).reset()
				return True
			else:
				try:
					self._getType(parameterName).setValue(options)
					return True
				except _convertException:
					return False

	def setParameter(self, parameterName, options = None):
		oldLandScape = self._parameterData('landscape')
		oldSwap = self._parameterData('swap')

		if not self._setParameter(parameterName, options):
			return False

		if parameterName == 'swap':
			if self._parameterData('swap') != oldSwap:
				width = self._parameterData('width')
				height = self._parameterData('height')
				self._getGuiPlotter().setScrollRegion(0, 0, height, width)
				self._setParameter('width', height)
				self._setParameter('height', width)
				self.setParameter('viewWidth', height)
				self.setParameter('viewHeight', width)
				self._waitCanvasCommands()
				self._resizeAll()
		elif parameterName == 'paper':
			paper = self._parameterData('paper')
			if paper == 'A0':
				width, height = '841m', '1189m'
			elif paper == 'A1':
				width, height = '594m', '841m'
			elif paper == 'A2':
				width, height = '420m', '594m'
			elif paper == 'A3':
				width, height = '297m', '420m'
			elif paper == 'A4':
				width, height = '210m', '297m'
			elif paper == 'A5':
				width, height = '148m', '210m'
			elif paper == 'A6':
				width, height = '105m', '148m'
			elif paper == 'A7':
				width, height = '74m', '105m'
			elif paper == 'B0':
				width, height = '1030m', '1456m'
			elif paper == 'B1':
				width, height = '728m', '1030m'
			elif paper == 'B2':
				width, height = '515m', '728m'
			elif paper == 'B3':
				width, height = '364m', '515m'
			elif paper == 'B4':
				width, height = '257m', '364m'
			elif paper == 'B5':
				width, height = '182m', '257m'
			elif paper == 'B6':
				width, height = '128m', '182m'
			elif paper == 'B7':
				width, height = '91m', '128m'
			elif paper == 'Letter':
				width, height = '215.9m', '279.4m'
			elif paper == 'Legal':
				width, height = '215.9m', '355.6m'
			elif paper == 'Tabloid':
				width, height = '279.4m', '431.8m'
			elif paper == 'Hagaki':
				width, height = '100m', '148m'
			else:
				raise RuntimeException()
			if self._parameterData('landscape') == True:
				width, height = height, width
			if self._parameterData('swap') == True:
				width, height = height, width
			self._getGuiPlotter().setScrollRegion(0, 0, width, height)
			self._setParameter('width', width)
			self._setParameter('height', height)
			self.setParameter('viewWidth', width)
			self.setParameter('viewHeight', height)
			self._waitCanvasCommands()
			self._resizeAll()
		elif parameterName == 'landscape':
			landScape = self._parameterData('landscape')
			if landScape != oldLandScape:
				width = self._parameterData('width')
				height = self._parameterData('height')
				self._getGuiPlotter().setScrollRegion(0, 0, height, width)
				self._setParameter('width', height)
				self._setParameter('height', width)
				self.setParameter('viewWidth', height)
				self.setParameter('viewHeight', width)
				self._waitCanvasCommands()
				self._resizeAll()
		elif parameterName == 'viewWidth':
			self._getGuiPlotter().setViewWidth(self._parameterData('viewWidth'))
			self._waitCanvasCommands()
		elif parameterName == 'viewHeight':
			self._getGuiPlotter().setViewHeight(self._parameterData('viewHeight'))
			self._waitCanvasCommands()
		elif parameterName == 'width':
			self._setParameter('width', width)
			self._getGuiPlotter().setScrollRegion(0, 0, self._parameterData('width'), self._parameterData('height'))
			self._waitCanvasCommands()
			self._resizeAll()
		elif parameterName == 'height':
			self._setParameter('height', height)
			self._getGuiPlotter().setScrollRegion(0, 0, self._parameterData('width'), self._parameterData('height'))
			self._waitCanvasCommands()
			self._resizeAll()

		return True

	def _waitCanvasCommands(self):
		guiPlotter = self._getGuiPlotter()
		lock = guiPlotter.getLock()
		while 1:
			lock.acquire()
			if guiPlotter.getNCanvasCommands() == 0:
				lock.release()
				break
			else:
				lock.release()
				time.sleep(0.1)

	def _appendRegion(self, region):
		self._regions.append(region)
		
	def createRegion(self, x = None, y = None, w = None, h = None):
		try:
			if (x == None) and (y == None) and (w == None) and (h == None):
				x = self._tabX
				y = self._tabY
				w = 1.0 - 2 * x
				h = 1.0 - 2 * y
			elif (type(x) == types.FloatType) and (y == None) and (w == None) and (h == None):
				x = float(x)
				y = self._tabY
				w = 1.0 - x - self._tabX
				h = 1.0 - 2 * y
			elif (type(x) == types.FloatType) and (type(y) == types.FloatType) and (w == None) and (h == None):
				x = float(x)
				y = float(y)
				w = 1.0 - x - self._tabX
				h = 1.0 - y - self._tabY
			elif (type(x) == types.FloatType) and (type(y) == types.FloatType) and (type(w) == types.FloatType) and (h == None):
				x = float(x)
				y = float(y)
				w = float(w)
				h = 1.0 - y - self._tabY
			elif (type(x) == types.FloatType) and (type(y) == types.FloatType) and (type(w) == types.FloatType) and (type(h) == types.FloatType):
				x = float(x)
				y = float(y)
				w = float(w)
				h = float(h)
			else:
				raise IllegalArgumentException()
		except ValueError:
			raise IllegalArgumentException()

		### Create a region.
		self._allRegions.append(IPlotterRegion(self._getGuiPlotter(), self._serialNumber, x, y, x + w, y + h))
		self._serialNumber += 1
		return self._allRegions[-1]

	def createRegions(self, columns = None, rows = None, index = None):
		### Arguments check.
		if (columns == None) and (rows == None) and (index == None):
			columns = 1
			rows = 1
			index = 0
		elif (type(columns) == types.IntType) and (rows == None) and (index == None):
			rows = 1
			index = 0
		elif (type(columns) == types.IntType) and (type(rows) == types.IntType) and (index == None):
			index = 0
		elif (type(columns) == types.IntType) and (type(rows) == types.IntType) and (type(index) == types.IntType):
			pass
		else:
			raise IllegalArgumentException()
			
		### Create regions.
		width = (1.0 - (columns + 1) * self._tabX) / columns
		height = (1.0 - (rows + 1) * self._tabY) / rows
		for rowIndex in range(rows):
			for columnIndex in range(columns):
				positionX = self._tabX + columnIndex * (width + self._tabX)
				positionY = self._tabY + rowIndex * (height + self._tabY)
				self._appendRegion(self.createRegion(positionX, positionY, width, height))

		self.setCurrentRegionNumber(index)
		
	def currentRegion(self):
		return self.region(self.currentRegionNumber())

	def currentRegionNumber(self):
		return self._currentRegionNumber
		
	def numberOfRegions(self):
		return len(self._regions)

	def setCurrentRegionNumber(self, index):
		if 0 <= index < self.numberOfRegions():
			self._currentRegionNumber = index
		else:
			raise IllegalArgumentException()

	def next(self):
		self.setCurrentRegionNumber((self.currentRegionNumber() + 1) % self.numberOfRegions())
		return self.currentRegion()

	def region(self, index):
		if 0 <= index < self.numberOfRegions():
			return self._regions[index]
		else:
			raise IllegalArgumentException()

	def destroyRegions(self):
		for region in self._allRegions:
			region._destroyRegion()
		self._regions = []
		self._allRegions = []
		self._currentRegionNumber = 0

	def clearRegions(self):
		for region in self._allRegions:
			region.clear()

	def show(self):
		self._getGuiPlotter().setShow(True)

	def hide(self):
		self._getGuiPlotter().setShow(False)

	def refresh(self):
		self._getGuiPlotter().refresh()

	def _resizeAll(self):
		for region in self._allRegions:
			region.info()._setLegendVeto(True)
			region._refreshAll()
			region.info()._setLegendVeto(False)

	def interact(self):
		pass

	def writeToFile(self, fileName, fileType = None):
		engineName = PGuiSelector.getGuiEngineName()

		if engineName == 'batch':
			### Nothing to do.
			pass

		elif engineName == 'tkinter':
			if fileType != None:
				fileTypeUpper = fileType.upper()
				if (fileTypeUpper == 'PS') or (fileTypeUpper == 'POSTSCRIPT'):
					fileType = 'PostScript'
				elif (fileTypeUpper == 'EPS') or (fileTypeUpper == 'ENCAPSULATEDPOSTSCRIPT'):
					fileType = 'EncapsulatedPostScript'
				else:
					raise IllegalArgumentException('"%s" is not supported.' % fileType)
			else:
				### Guess file type from file name.
				if fileName.count('.') >= 1:
					ext = fileName.split('.')[-1]
					if ext.lower() == 'ps':
						fileType = 'PostScript'
					elif ext.lower() == 'eps':
						fileType = 'EncapsulatedPostScript'
					else:
						raise IllegalArgumentException('".%s" is not supported by tkinter GUI engine.' % ext)
				else:
					### Default is PostScript.
					fileType = 'PostScript'

			if fileType == 'EncapsulatedPostScript':
				self._getGuiPlotter().setPostscript(fileName, self._parameterData('landscape'))
			elif fileType == 'PostScript':
				try:
					if fileName in self._processedPostScripts:
						self._postScriptUpdate(fileName)
					else:
						self._processedPostScripts.append(fileName)
						self._postScriptCreate(fileName)
				except AttributeError:
					self._processedPostScripts = [fileName]
					self._postScriptCreate(fileName)

		elif engineName == 'swing':
			if fileType == None:
				if fileName.count('.') >= 1:
					fileType = fileName.split('.')[-1]
				else:
					raise IllegalArgumentException('No format type is specified.')
			formatNames = self._getGuiPlotter().getFormatNames()
			if not fileType in formatNames:
				raise IllegalArgumentException('"%s" format is not in %s supported by swing GUI engine.' % (fileType, formatNames))

			self._getGuiPlotter().setImageWrite(fileName, self._parameterData('landscape'), fileType)

		else:
			raise RuntimeError, 'Unknown GUI engine name "%s".' % engineName

	def _postScriptCreate(self, fileName):
		### Get postscript strings.
		bridge = []
		self._getGuiPlotter().setPostscriptStrings(self._parameterData('landscape'), bridge)
		postscriptStrings = bridge[0][0]

		### Comment part.
		psFile = file(fileName, 'w')
		psFile.write('%!PS-Adobe-3.0\n')
		psFile.write('%%Creator: PAIDA-' + IConstants.PAIDA_VERSION + '\n')
		psFile.write('%%Title: ' + self._getGuiPlotter().getTitle() + '\n')
		psFile.write('%%CreationDate: ' + time.ctime() + '\n')

		boundingString = '%%BoundingBox: '
		boundingIndex = postscriptStrings.index(boundingString)
		bounding = ''
		i = boundingIndex + len(boundingString)
		while postscriptStrings[i] != '\n':
			bounding += postscriptStrings[i]
			i += 1
		psFile.write('%%BoundingBox: ' + bounding + '\n')
		psFile.write('%%Pages: 1\n')
		psFile.write('%%EndComments\n')

		### The rest. Ensure ending with '%%Trailer\nend\n%%EOF\n'.
		startIndex = postscriptStrings.index('%%BeginProlog\n')
		try:
			endIndex = postscriptStrings.index('%%Trailer\nend\n%%EOF\n')
		except ValueError:
			### Maybe the way of creating PostScript file of Tcl/Tk is changed.
			raise RuntimeException('PAIDA encountered unknown type PostScript file. Please contact to the users mailing list.')
		psFile.write(postscriptStrings[startIndex:endIndex])
		psFile.write('%%Trailer\nend\n%%EOF\n')
		psFile.close()

	def _postScriptUpdate(self, fileName):
		### Check.
		if not os.path.exists(fileName):
			self._postScriptCreate(fileName)
			return

		### Preparation.
		psFile = file(fileName, 'r')
		psLines = psFile.readlines()
		psFile.close()
		psLines[2] = '%%Title: ' + self._getGuiPlotter().getTitle() + '\n'
		psLines[3] = '%%CreationDate: ' + time.ctime() + '\n'
		nPages = eval(psLines[5][9:-1]) + 1
		psLines[5] = '%%Pages: ' + ('%d' % nPages) + '\n'
		### Remove the last three lines '%%Trailer\nend\n%%EOF\n'.
		psLines.pop()
		psLines.pop()
		psLines.pop()

		### Commit.
		psFile = file(fileName, 'w')
		psFile.writelines(psLines)
		del psLines
		psFile.write('%%Page: ' + ('%d %d' % (nPages, nPages)) + '\n')

		### Get postscript strings.
		bridge = []
		self._getGuiPlotter().setPostscriptStrings(self._parameterData('landscape'), bridge)
		postscriptStrings = bridge[0][0]

		### Commit.
		startIndex = postscriptStrings.index('%%Page: 1 1\n') + len('%%Page: 1 1\n')
		endIndex = postscriptStrings.index('%%Trailer\nend\n%%EOF\n')
		psFile.write(postscriptStrings[startIndex:endIndex])
		psFile.write('%%Trailer\nend\n%%EOF\n')
		psFile.close()

	def _setWindowTitle(self, title):
		self._getGuiPlotter().setTitle(title)

	def setTitle(self, title):
		if type(title) in types.StringTypes:
			self._setWindowTitle(title)
			tags = ['globalTitle']
			guiPlotter = self._getGuiPlotter()
			guiPlotter.delete(tags)
			canvasWidth = guiPlotter.getScrollRegion()[2]
			guiPlotter.create_styledText(self.titleStyle().textStyle(), tags, canvasWidth / 2.0, 10.0, title, N)
		else:
			raise IllegalArgumentException()

	def titleStyle(self):
		return self._titleStyle

	def setTitleStyle(self, style):
		if isinstance(style, ITitleStyle):
			self._titleStyle = style
		else:
			raise IllegalArgumentException()
