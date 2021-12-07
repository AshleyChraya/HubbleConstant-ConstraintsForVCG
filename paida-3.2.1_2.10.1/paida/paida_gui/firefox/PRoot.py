from paida.paida_core.PAbsorber import *
from paida.paida_core.IFillStyle import *
from paida.paida_core.ILineStyle import *
from paida.paida_core.ITextStyle import *
from paida.paida_gui.firefox.paida_library import paida_library
from paida.paida_gui.firefox.top_html import top_html
from paida.paida_gui.firefox.tree_xml import tree_xml
from paida.paida_gui.firefox.plotter_xml import plotter_xml
import BaseHTTPServer
import code

try:
	import threading
except ImportError:
	import dummy_threading as threading
import time
import math

N = 'N'
NE = 'NE'
E = 'E'
SE = 'SE'
S = 'S'
SW = 'SW'
W = 'W'
NW = 'NW'
CENTER = 'CENTER'

def createRoot():
	global _guiRoot
	_guiRoot = _Root()
	_guiRoot.setDaemon(True)

def startRoot():
	global _guiRoot
	_guiRoot.start()

def getRoot():
	global _guiRoot
	return _guiRoot

def getFontList(_defaultCandidates):
	### Fix me!
	return _defaultCandidates, _defaultCandidates[0]

class SvgFont:
	def __init__(self, textStyle):
		self.configure(textStyle)

	def configure(self, textStyle):
		self._family = textStyle.font()
		self._size = textStyle.fontSize()
		if textStyle.isBold():
			self._weight = 'bold'
		else:
			self._weight = 'normal'
		if textStyle.isItalic():
			self._slant = 'italic'
		else:
			self._slant = 'roman'
		if textStyle.isUnderlined():
			self._Underline = 1
		else:
			self._Underline = 0

	def family(self):
		return self._family

	def measure(self, data):
		return self._size * len(data) / 2.0

	def size(self):
		return self._size

	def metrics(self, part):
		if part == 'linespace':
			return self._size * 0.8
		elif part == 'ascent':
			return self._size * 0.2
		elif part == 'height':
			return self._size
		else:
			raise RuntimeError

class PAIDAHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def __init__(self, *args1, **args2):
		#self.runner = code.InteractiveInterpreter(local)
		BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args1, **args2)

	def log_message(self, format, *args):
		pass
		#BaseHTTPServer.BaseHTTPRequestHandler.log_message(self, format, *args)

	def getCode(self):
		return urllib.unquote(cgi.parse_qs(self.path[2:])['command'][0])

	def do_GET(self):
		self.send_response(200)
		if self.path.endswith('.xml'):
			self.send_header("Content-Type", "text/xml")
		else:
			self.send_header("Content-Type", "text/html")
		self.send_header('Connection', 'close')
		self.end_headers()

		if self.path.startswith('/plotter?'):
			root = getRoot()
			plotters = root._getPlotters()
			if plotters == []:
				self.wfile.write('')
			else:
				result = ''
				plotter = plotters[0]
				plotter.getLock().acquire()
				for command in plotter._canvasCommands:
					command[0](*command[1], **command[2])
				else:
					plotter._canvasCommands = []

				for command in plotter._commands:
					for item in command:
						result += item[0] + '=' + item[1] + '&'
					result += '#'
				self.wfile.write(result)
				plotter._commands = []
				plotter.getLock().release()
		elif self.path.startswith('/tree?'):
			root = getRoot()
			trees = root._getTrees()
			if trees == []:
				self.wfile.write('')
			else:
				result = ''
				tree = trees[0]
				tree.getLock().acquire()
				for command in tree._canvasCommands:
					command[0](*command[1], **command[2])
				else:
					tree._canvasCommands = []

				for command in tree._commands:
					for item in command:
						result += item[0] + '=' + item[1] + '&'
					result += '#'
				self.wfile.write(result)
				tree._commands = []
				tree.getLock().release()
		elif self.path in ['/', '/top.html']:
			self.wfile.write(top_html)
		elif self.path == '/paida_library.js':
			self.wfile.write(paida_library)
		elif self.path == '/tree.xml':
			self.wfile.write(tree_xml)
		elif self.path == '/plotter.xml':
			self.wfile.write(plotter_xml)
		else:
			systemWrite = sys.stdout
			sys.stdout = self.wfile
			self.runner.runsource(self.getCode())
			sys.stdout = systemWrite

class _Root(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._setRootCondition(threading.Condition())

	def run(self):
		rootCondition = self._getRootCondition()
		rootCondition.acquire()

		httpd = BaseHTTPServer.HTTPServer(('', 8080), PAIDAHandler)
		#httpd.serve_forever()

		self._trees = []
		self._plotters = []
		self._requestedTrees = []
		self._requestedPlotters = []
		self._setQuitLoop(False)

		self._setLock(threading.RLock())
		self._setTreeCondition(threading.Condition())
		self._setPlotterCondition(threading.Condition())

		rootCondition.notifyAll()
		rootCondition.release()

		lock = self._getLock()
		while 1:
			if self._getQuitLoop():
				rootCondition = self._getRootCondition()
				rootCondition.acquire()
				### Wait other threads.
				lock.acquire()
				lock.release()
				rootCondition.notifyAll()
				rootCondition.release()
				break
			if lock.acquire(blocking = 0):
				self._check()
				lock.release()
			httpd.handle_request()
			time.sleep(0.1)

	def _setLock(self, lock):
		self._lock = lock

	def _getLock(self):
		return  self._lock

	def _setRootCondition(self, Condition):
		self._rootCondition = Condition

	def _getRootCondition(self):
		return self._rootCondition

	def _setTreeCondition(self, Condition):
		self._treeCondition = Condition

	def _getTreeCondition(self):
		return self._treeCondition

	def _setPlotterCondition(self, Condition):
		self._plotterCondition = Condition

	def _getPlotterCondition(self):
		return self._plotterCondition

	def _setQuitLoop(self, boolean):
		self._quitLoop = boolean

	def _getQuitLoop(self):
		return self._quitLoop

	def _appendTree(self, tree):
		self._trees.append(tree)

	def _getTrees(self):
		return self._trees

	def _removeTree(self, tree):
		self._getTrees().remove(tree)

	def _appendPlotter(self, plotter):
		self._plotters.append(plotter)

	def _getPlotters(self):
		return self._plotters

	def _removePlotter(self, plotter):
		self._getPlotters().remove(plotter)

	def _requestTree(self):
		treeCondition = self._getTreeCondition()
		treeCondition.acquire()
		bridge = []
		self._requestedTrees.append(bridge)
		treeCondition.wait()
		treeCondition.release()
		return bridge[0][0]

	def _requestPlotter(self, viewWidth, viewHeight, width, height):
		plotterCondition = self._getPlotterCondition()
		plotterCondition.acquire()
		bridge = []
		self._requestedPlotters.append((bridge, viewWidth, viewHeight, width, height))
		plotterCondition.wait()
		plotterCondition.release()
		return bridge[0][0]

	def _check(self):
		self._updateTrees()
		self._updatePlotters()

	def _updateTrees(self):
		if self._requestedTrees:
			treeCondition = self._getTreeCondition()
			treeCondition.acquire()
			for bridge in self._requestedTrees:
				_tree = _Tree(self._getLock())
				bridge.append([_tree])
				self._appendTree(_tree)
				_tree.update()
			self._requestedTrees = []
			treeCondition.notifyAll()
			treeCondition.release()
			return

	def _updatePlotters(self):
		if self._requestedPlotters:
			plotterCondition = self._getPlotterCondition()
			plotterCondition.acquire()
			for (bridge, viewWidth, viewHeight, width, height) in self._requestedPlotters:
				_plotter = _Plotter(self._getLock(), viewWidth, viewHeight, width, height)
				bridge.append([_plotter])
				self._appendPlotter(_plotter)
				_plotter.update()
			self._requestedPlotters = []
			plotterCondition.notifyAll()
			plotterCondition.release()
			return

class _Base:
	def __init__(self, lock):
		self._canvasCommands = []
		self._sizeCommands = []
		self.setLock(lock)

		self._setFontCondition(threading.Condition())
		textStyle = ITextStyle()
		textStyle.setBold(False)
		textStyle.setUnderlined(False)
		self._fontMeasurement = self._createSvgFont(textStyle)

		self.setShow(True)
		self.setTitle('')

	def _sizeChanged(self, event):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_sizeChanged, [event], {}])
		self.getLock().release()

	def canvas_sizeChanged(self, event):
		### Fix me!
		pass

	def _setFontCondition(self, condition):
		self._fontCondition = condition

	def _getFontCondition(self):
		return self._fontCondition

	def getNCanvasCommands(self):
		return len(self._canvasCommands)

	def setLock(self, lock):
		self._lock = lock

	def getLock(self):
		return  self._lock

	def canvas_title(self, title):
		### Fix me!
		self._title = title

	def canvas_show(self, boolean):
		### Fix me!
		self._show = boolean

	def canvas_terminate(self):
		### Fix me!
		pass

	def setTitle(self, title):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_title, [title], {}])
		self.getLock().release()

	def getTitle(self):
		return self._title

	def setShow(self, boolean):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_show, [boolean], {}])
		self.getLock().release()

	def getShow(self):
		return self._show

	def _createSvgFont(self, textStyle):
		return SvgFont(textStyle)

	def _configureSvgFont(self, font, textStyle):
		font.configure(textStyle)
		return font

	def _getFontTuple(self, textStyle):
		### Fix me!
		fontFamily = textStyle.font()
		fontSize = str(int(textStyle.fontSize()))
		options = ''
		if textStyle.isBold():
			options += 'bold'
		else:
			options += 'normal'
		if textStyle.isItalic():
			options += ' italic'
		else:
			options += ' roman'
		if textStyle.isUnderlined():
			options += ' underline'
		else:
			pass
		return (fontFamily, fontSize, options)

	def _getFontMeasurements(self, textDataList, bridge):
		fontCondition = self._getFontCondition()
		fontCondition.acquire()
		self._canvasCommands.append([self.canvas_fontMeasurements, [textDataList, bridge], {}])
		fontCondition.wait()
		fontCondition.release()

	def canvas_fontMeasurements(self, textDataList, bridge):
		### Fix me!
		fontCondition = self._getFontCondition()
		fontCondition.acquire()
		result = []
		fontMeasurement = self._fontMeasurement
		for textStyle, text in textDataList:
			fontMeasurement = self._configureSvgFont(fontMeasurement, textStyle)
			result.append([fontMeasurement.measure(text), fontMeasurement.metrics('linespace')])
		bridge.append(result)
		fontCondition.notifyAll()
		fontCondition.release()

	def update(self):
		### Fix me!
		pass

class _Tree(_Base):
	_folderIconString = 'R0lGODlhDgAPAIIAAA4ODkhz///U1ABV/46r/wAAAAAAAAAAACH5BAEAAAIALAAAAAAOAA8AAAhX\nAAUIHAgAwMCDBAEECFAQoYCCCyMyNChQocSLBiFelFgQAAGNHAEMKEigpMaCA1KSLGlSZEqVHll+\nfPlyJUuXNG2apKnyoUycPSvGxNkQYceRFB0KdRgQADs=\n'
	_fileIconString = 'R0lGODlhCgAKAIIAACVX/7HH/9Tj/2uP/////wAAAAAAAAAAACH5BAEAAAQALAAAAAAKAAoAAAg0\nAAkIHEiQAICDCAkiRDhAgMCFBwcEcAgRgESKEC8azDhR4ICPIDsSEBCgpEmHAgWoXEkgIAA7\n'

	def __init__(self, lock):
		_Base.__init__(self, lock)

		self._commands = []

		self._folderImage = None
		self._folderImageW = 16
		self._folderImageH = 16
		self._fileImage = None
		self._fileImageW = 16
		self._fileImageH = 16

		textStyle = ITextStyle()
		textStyle.setBold(False)
		textStyle.setUnderlined(False)
		self._fontNormal = self._createSvgFont(textStyle)
		textStyle.setBold(True)
		textStyle.setUnderlined(True)
		self._fontSelected = self._createSvgFont(textStyle)

	def terminate(self):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_terminate, [], {}])
		self.getLock().release()

	def canvas_terminate(self):
		getRoot()._removeTree(self)

		_Base.canvas_terminate(self)

		self._folderImage = None
		self._fileImage = None
		self._fontNormal = None
		self._fontSelected = None

	def redrawTree(self, block, itree):
		if self.getLock().acquire(block):
			canvasCommands = self._canvasCommands
			command = [self.canvas_redrawTree, [itree], {}]
			try:
				while 1:
					canvasCommands.remove(command)
			except ValueError:
				pass
			canvasCommands.append(command)
			self.getLock().release()

	def canvas_redrawTree(self, itree):
		pwd = itree._getPwd()
		self.redrawTreeWalker(itree, pwd, '/', 10, 10)

	def redrawTreeWalker(self, itree, pwd, directoryPath, x, y):
		spaceX = 16
		spaceY = 4
		stringSpaceX = 4
		fileX = x + self._fileImageW + stringSpaceX
		fontNormal = self._fontNormal
		fileImage = self._fileImage
		tags = ['allItems']
		objects = itree._listObjects(directoryPath)
		for object in objects:
			if object._instance:
				command = []
				command.append(['_name_', 'circle'])
				command.append(['cx', str(x)])
				command.append(['cy', str(y)])
				command.append(['r', '4'])
				command.append(['fill', 'blue'])
				command.append(['stroke', 'blue'])
				command.append(['stroke-width', '1'])
				self._commands.append(command)
				command = []
				command.append(['_text_', object.name()])
				command.append(['x', str(x + 8)])
				command.append(['y', str(y + fontNormal.metrics('linespace') / 2.0)])
				command.append(['font-size', str(fontNormal.size())])
				command.append(['font-family', fontNormal.family()])
				self._commands.append(command)
				y += spaceY + self._fileImageH
			else:
				### Subdirectory.
				command = []
				command.append(['_name_', 'rect'])
				command.append(['x', str(x)])
				command.append(['y', str(y)])
				command.append(['width', '24'])
				command.append(['height', '16'])
				command.append(['fill', 'red'])
				command.append(['stroke', 'red'])
				command.append(['stroke-width', '1'])
				self._commands.append(command)
				command = []
				command.append(['_text_', object.name()])
				command.append(['x', str(x + 8)])
				command.append(['y', str(y + fontNormal.metrics('linespace') / 2.0)])
				command.append(['font-size', str(fontNormal.size())])
				command.append(['font-family', fontNormal.family()])
				self._commands.append(command)
				y += spaceY + self._folderImageH
				self.redrawTreeWalker(itree, pwd, '%s/%s' % (directoryPath, object.name()), x + spaceX, y)

class _Plotter(_Base):
	def __init__(self, lock, viewWidth, viewHeight, width, height):
		### Fix me!
		self._commands = []

		_Base.__init__(self, lock)
		#canvas.configure(bg='white')
		self.setImageIOCondition(threading.Condition())

		self._legendsFont = self._createSvgFont(ITextStyle())
		self._statisticsFont = self._createSvgFont(ITextStyle())
		self._textsFont = self._createSvgFont(ITextStyle())
		self._canvasFont = self._createSvgFont(ITextStyle())
		self._canvasExponentBaseFont = self._createSvgFont(ITextStyle())
		self._canvasExponentIndexFont = self._createSvgFont(ITextStyle())

		#self.setViewWidth(canvas.winfo_pixels(viewWidth))
		#self.setViewHeight(canvas.winfo_pixels(viewHeight))
		#self.setScrollRegion(0, 0, canvas.winfo_pixels(width), canvas.winfo_pixels(height))

	def _requestRegion(self, serialNumber, allTags, x0, y0, x1, y1):
		### Nothing to do for Firefox GUI.
		pass

	def _convertToPixel(self, length):
		dpi = 72.0
		inch = 2.54
		last = length[-1]
		if last == 'c':
			return eval(length[:-1]) / inch * dpi
		elif last == 'i':
			return eval(length[:-1]) * dpi
		elif last == 'm':
			return eval(length[:-1]) / inch * dpi / 10.0
		elif last == 'p':
			return eval(length[:-1])
		else:
			return eval(length)

	def _convertToPixelX(self, length):
		return self._convertToPixel(length)

	def _convertToPixelY(self, length):
		return self._convertToPixel(length)

	def setImageIOCondition(self, condition):
		self._imageIOCondition = condition

	def getImageIOCondition(self):
		return self._imageIOCondition

	def setScrollRegion(self, *args):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_scrollRegion, args, {}])
		self.getLock().release()

	def getScrollRegion(self):
		### Fix me!
		return (600, 400, 600, 400)

	def setViewWidth(self, viewWidth):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_viewWidth, [viewWidth], {}])
		self.getLock().release()

	def getViewWidth(self):
		return self._viewWidth

	def setViewHeight(self, viewHeight):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_viewHeight, [viewHeight], {}])
		self.getLock().release()

	def getViewHeight(self):
		return self._viewHeight

	def refresh(self):
		pass

	def delete(self, *args):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_delete, args, {}])
		self.getLock().release()

	def create_styledText(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledText, args1, args2])
		self.getLock().release()

	def create_styledExponent(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledExponent, args1, args2])
		self.getLock().release()

	def create_styledOval(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledOval, args1, args2])
		self.getLock().release()

	def create_styledRectangle(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledRectangle, args1, args2])
		self.getLock().release()

	def create_styledLine(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledLine, args1, args2])
		self.getLock().release()

	def create_styledPolygon(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledPolygon, args1, args2])
		self.getLock().release()

	def create_styledMarker(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledMarker, args1, args2])
		self.getLock().release()

	def create_styledTextsBox(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledTextsBox, args1, args2])
		self.getLock().release()

	def create_styledLegendsBox(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledLegendsBox, args1, args2])
		self.getLock().release()

	def create_styledStatisticsBox(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_create_styledStatisticsBox, args1, args2])
		self.getLock().release()

	def setPostscript(self, fileName, landscape):
		imageIOCondition = self.getImageIOCondition()
		imageIOCondition.acquire()
		self._canvasCommands.append([self.canvas_postscript, [fileName, landscape], {}])
		imageIOCondition.wait()
		imageIOCondition.release()

	def setPostscriptStrings(self, landscape, bridge):
		imageIOCondition = self.getImageIOCondition()
		imageIOCondition.acquire()
		self._canvasCommands.append([self.canvas_postscriptStrings, [landscape, bridge], {}])
		imageIOCondition.wait()
		imageIOCondition.release()

	def terminate(self):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_terminate, [], {}])
		self.getLock().release()

	def canvas_terminate(self):
		getRoot()._removePlotter(self)

		_Base.canvas_terminate(self)

		self._legendsFont = None
		self._statisticsFont = None
		self._textsFont = None
		self._canvasFont = None
		self._canvasExponentBaseFont = None
		self._canvasExponentIndexFont = None

	def canvas_scrollRegion(self, x0, y0, x1, y1):
		### Fix me!
		pass

	def canvas_viewWidth(self, viewWidth):
		### Fix me!
		pass

	def canvas_viewHeight(self, viewHeight):
		### Fix me!
		pass

	def canvas_create_styledLegendsBox(self, infoStyle, region, layout, legends, tags):
		self.canvas_delete(tags)
		textStyle = infoStyle.textStyle()
		fontData = self._configureSvgFont(self._legendsFont, textStyle)
		fontWidth = fontData.measure('W')
		fontHeight = fontData.metrics('linespace')
		fontHalf = fontData.metrics('ascent') / 2.0

		longestDescription = 0
		for [style, description] in legends:
			longestDescription = max(longestDescription, fontData.measure(description))
		longestStyle = fontWidth

		xLower, xUpper = region._getAxisRangeX()
		yLower, yUpper = region._getAxisRangeY()
		regionLengthX = region._getRegionLengthX()
		regionLengthY = region._getRegionLengthY()
		tabX = max(5, int(0.014 * regionLengthX)) + 1
		tabY = max(5, int(0.014 * regionLengthY)) + 1
		spacerX = max(2, fontWidth / 2)
		spacerY = max(2, fontHeight / 4)
		boxOffsetX = self._convertToPixelX(layout._parameterData('legendsBoxOffsetX'))
		boxOffsetY = self._convertToPixelY(layout._parameterData('legendsBoxOffsetY'))
		boxAnchor = layout._parameterData('legendsBoxAnchor')
		if boxAnchor == 'N':
			boxX = (xLower + xUpper) / 2.0 - (longestStyle + spacerX + longestDescription) / 2.0 - tabX + boxOffsetX
			boxY = yLower + boxOffsetY
		elif boxAnchor == 'NE':
			boxX = xUpper - longestStyle - spacerX - longestDescription - tabX * 2 + boxOffsetX
			boxY = yLower + boxOffsetY
		elif boxAnchor == 'E':
			boxX = xUpper - longestStyle - spacerX - longestDescription - tabX * 2 + boxOffsetX
			boxY = (yLower + yUpper) / 2.0 - (len(legends) * (fontHeight + spacerY) - spacerY) / 2.0 - tabY + boxOffsetY
		elif boxAnchor == 'SE':
			boxX = xUpper - longestStyle - spacerX - longestDescription - tabX * 2 + boxOffsetX
			boxY = yUpper - (len(legends) * (fontHeight + spacerY) - spacerY) - tabY * 2 + boxOffsetY
		elif boxAnchor == 'S':
			boxX = (xLower + xUpper) / 2.0 - (longestStyle + spacerX + longestDescription) / 2.0 - tabX + boxOffsetX
			boxY = yUpper - (len(legends) * (fontHeight + spacerY) - spacerY) - tabY * 2 + boxOffsetY
		elif boxAnchor == 'SW':
			boxX = xLower + boxOffsetX
			boxY = yUpper - (len(legends) * (fontHeight + spacerY) - spacerY) - tabY * 2 + boxOffsetY
		elif boxAnchor == 'W':
			boxX = xLower + boxOffsetX
			boxY = (yLower + yUpper) / 2.0 - (len(legends) * (fontHeight + spacerY) - spacerY) / 2.0 - tabY + boxOffsetY
		elif boxAnchor == 'NW':
			boxX = xLower + boxOffsetX
			boxY = yLower + boxOffsetY
		else:
			raise RuntimeException()
		styleX = boxX + tabX
		descriptionX = styleX + longestStyle + spacerX
		lineY = boxY + tabY

		boxWidth = tabX * 2 + longestStyle + spacerX + longestDescription
		boxHeight = len(legends) * (fontHeight + spacerY) - spacerY + tabY * 2
		fillStyle = infoStyle._parameterData('fillStyle')
		lineStyle = infoStyle._parameterData('lineStyle')
		self.canvas_create_styledRectangle(lineStyle, fillStyle, tags, boxX, boxY, boxX + boxWidth, boxY + boxHeight)
		for [style, description] in legends:
			style = style._createCopy()
			if style.__class__.__name__ == 'IFillStyle':
				originalColor = lineStyle.color()
				lineStyle.setColor(style.color())
				self.canvas_create_styledRectangle(lineStyle, style, tags, styleX, lineY, styleX + fontWidth, lineY + fontHeight)
				lineStyle.setColor(originalColor)
			elif style.__class__.__name__ == 'ILineStyle':
				self.canvas_create_styledLine(style, tags, styleX, lineY + fontHalf, styleX + fontWidth, lineY + fontHalf)
			elif style.__class__.__name__ == 'IMarkerStyle':
				originalSize = style._parameterData('size')
				style.setParameter('size', fontWidth)
				self.canvas_create_styledMarker(style, tags, styleX + fontWidth / 2.0, lineY + fontHalf)
				style.setParameter('size', originalSize)
			else:
				raise RuntimeException()
			self.canvas_create_styledText(textStyle, tags, descriptionX, lineY, description, NW)
			lineY += fontHeight + spacerY

	def canvas_create_styledStatisticsBox(self, infoStyle, region, layout, statisticsData, tags):
		self.canvas_delete(tags)
		textStyle = infoStyle.textStyle()
		fontData = self._configureSvgFont(self._statisticsFont, textStyle)
		fontWidth = fontData.measure('W')
		fontHeight = fontData.metrics('linespace')

		longestName = 0
		longestData = 0
		for [name, data] in statisticsData:
			longestName = max(longestName, fontData.measure(name))
			longestData = max(longestData, fontData.measure(data))

		xLower, xUpper = region._getAxisRangeX()
		yLower, yUpper = region._getAxisRangeY()
		regionLengthX = region._getRegionLengthX()
		regionLengthY = region._getRegionLengthY()
		tabX = max(5, int(0.014 * regionLengthX)) + 1
		tabY = max(5, int(0.014 * regionLengthY)) + 1
		spacerX = max(2, fontWidth / 2)
		spacerY = max(2, fontHeight / 4)
		boxOffsetX = self._convertToPixelX(layout._parameterData('statisticsBoxOffsetX'))
		boxOffsetY = self._convertToPixelY(layout._parameterData('statisticsBoxOffsetY'))
		boxAnchor = layout._parameterData('statisticsBoxAnchor')
		if boxAnchor == 'N':
			boxX = (xLower + xUpper) / 2.0 - (longestName + spacerX + longestData) / 2.0 - tabX + boxOffsetX
			boxY = yLower + boxOffsetY
		elif boxAnchor == 'NE':
			boxX = xUpper - longestName - spacerX - longestData - tabX * 2 + boxOffsetX
			boxY = yLower + boxOffsetY
		elif boxAnchor == 'E':
			boxX = xUpper - longestName - spacerX - longestData - tabX * 2 + boxOffsetX
			boxY = (yLower + yUpper) / 2.0 - (len(statisticsData) * (fontHeight + spacerY) - spacerY) / 2.0 - tabY + boxOffsetY
		elif boxAnchor == 'SE':
			boxX = xUpper - longestName - spacerX - longestData - tabX * 2 + boxOffsetX
			boxY = yUpper - (len(statisticsData) * (fontHeight + spacerY) - spacerY) - tabY * 2 + boxOffsetY
		elif boxAnchor == 'S':
			boxX = (xLower + xUpper) / 2.0 - (longestName + spacerX + longestData) / 2.0 - tabX + boxOffsetX
			boxY = yUpper - (len(statisticsData) * (fontHeight + spacerY) - spacerY) - tabY * 2 + boxOffsetY
		elif boxAnchor == 'SW':
			boxX = xLower + boxOffsetX
			boxY = yUpper - (len(statisticsData) * (fontHeight + spacerY) - spacerY) - tabY * 2 + boxOffsetY
		elif boxAnchor == 'W':
			boxX = xLower + boxOffsetX
			boxY = (yLower + yUpper) / 2.0 - (len(statisticsData) * (fontHeight + spacerY) - spacerY) / 2.0 - tabY + boxOffsetY
		elif boxAnchor == 'NW':
			boxX = xLower + boxOffsetX
			boxY = yLower + boxOffsetY
		else:
			raise RuntimeException()
		nameX = boxX + tabX
		dataX = nameX + longestName + spacerX
		lineY = boxY + tabY

		boxWidth = tabX * 2 + longestName + spacerX + longestData
		boxHeight = len(statisticsData) * (fontHeight + spacerY) - spacerY + tabY * 2
		fillStyle = infoStyle._parameterData('fillStyle')
		lineStyle = infoStyle._parameterData('lineStyle')
		self.canvas_create_styledRectangle(lineStyle, fillStyle, tags, boxX, boxY, boxX + boxWidth, boxY + boxHeight)
		for [name, data] in statisticsData:
			self.canvas_create_styledText(textStyle, tags, nameX, lineY, name, NW)
			self.canvas_create_styledText(textStyle, tags, dataX, lineY, data, NW)
			lineY += fontHeight + spacerY

	def canvas_create_styledTextsBox(self, infoStyle, region, layout, textsData, tags):
		self.canvas_delete(tags)
		textStyle = infoStyle.textStyle()
		fontData = self._configureSvgFont(self._textsFont, textStyle)
		fontWidth = fontData.measure('W')
		fontHeight = fontData.metrics('linespace')

		longestData = 0
		for line in textsData:
			longestData = max(longestData, fontData.measure(line))

		xLower, xUpper = region._getAxisRangeX()
		yLower, yUpper = region._getAxisRangeY()
		regionLengthX = region._getRegionLengthX()
		regionLengthY = region._getRegionLengthY()
		tabX = max(5, int(0.014 * regionLengthX)) + 1
		tabY = max(5, int(0.014 * regionLengthY)) + 1
		spacerX = max(2, fontWidth / 2)
		spacerY = max(2, fontHeight / 4)
		boxOffsetX = self._convertToPixelX(layout._parameterData('textsBoxOffsetX'))
		boxOffsetY = self._convertToPixelY(layout._parameterData('textsBoxOffsetY'))
		boxAnchor = layout._parameterData('textsBoxAnchor')
		if boxAnchor == 'N':
			boxX = (xLower + xUpper) / 2.0 - longestData / 2.0 - tabX + boxOffsetX
			boxY = yLower + boxOffsetY
		elif boxAnchor == 'NE':
			boxX = xUpper - longestData - tabX * 2 + boxOffsetX
			boxY = yLower + boxOffsetY
		elif boxAnchor == 'E':
			boxX = xUpper - longestData - tabX * 2 + boxOffsetX
			boxY = (yLower + yUpper) / 2.0 - (len(textsData) * (fontHeight + spacerY) - spacerY) / 2.0 - tabY + boxOffsetY
		elif boxAnchor == 'SE':
			boxX = xUpper - longestData - tabX * 2 + boxOffsetX
			boxY = yUpper - (len(textsData) * (fontHeight + spacerY) - spacerY) - tabY * 2 + boxOffsetY
		elif boxAnchor == 'S':
			boxX = (xLower + xUpper) / 2.0 - longestData / 2.0 - tabX + boxOffsetX
			boxY = yUpper - (len(textsData) * (fontHeight + spacerY) - spacerY) - tabY * 2 + boxOffsetY
		elif boxAnchor == 'SW':
			boxX = xLower + boxOffsetX
			boxY = yUpper - (len(textsData) * (fontHeight + spacerY) - spacerY) - tabY * 2 + boxOffsetY
		elif boxAnchor == 'W':
			boxX = xLower + boxOffsetX
			boxY = (yLower + yUpper) / 2.0 - (len(textsData) * (fontHeight + spacerY) - spacerY) / 2.0 - tabY + boxOffsetY
		elif boxAnchor == 'NW':
			boxX = xLower + boxOffsetX
			boxY = yLower + boxOffsetY
		else:
			raise RuntimeException()
		dataX = boxX + tabX
		lineY = boxY + tabY

		boxWidth = tabX * 2 + longestData
		boxHeight = len(textsData) * (fontHeight + spacerY) - spacerY + tabY * 2
		fillStyle = infoStyle._parameterData('fillStyle')
		lineStyle = infoStyle._parameterData('lineStyle')
		self.canvas_create_styledRectangle(lineStyle, fillStyle, tags, boxX, boxY, boxX + boxWidth, boxY + boxHeight)
		for line in textsData:
			self.canvas_create_styledText(textStyle, tags, dataX, lineY, line, NW)
			lineY += fontHeight + spacerY

	def canvas_postscript(self, fileName, landscape):
		### Fix me!
		return

		postscriptCondition = self.getImageIOCondition()
		postscriptCondition.acquire()
		x = self.getScrollRegion()[2]
		y = self.getScrollRegion()[3]
		self.getCanvas().postscript(file = fileName, width = x, height = y, rotate = landscape)
		postscriptCondition.notifyAll()
		postscriptCondition.release()

	def canvas_postscriptStrings(self, landscape, bridge):
		### Fix me!
		return

		postscriptCondition = self.getImageIOCondition()
		postscriptCondition.acquire()
		x = self.getScrollRegion()[2]
		y = self.getScrollRegion()[3]
		bridge.append([self.getCanvas().postscript(pagewidth = x, pageheight = y, rotate = landscape)])
		postscriptCondition.notifyAll()
		postscriptCondition.release()

	def canvas_create_styledOval(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		command = []
		command.append(['_name_', 'ellipse'])
		command.append(['cx', str((x0 + x1) / 2.0)])
		command.append(['cy', str((y0 + y1) / 2.0)])
		command.append(['rx', str(x1 - cx)])
		command.append(['ry', str(y1 - cy)])
		command.append(['fill', fillStyle.color()])
		command.append(['stroke', lineStyle.color()])
		command.append(['stroke-width', str(lineStyle.thickness())])
		self._commands.append(command)

	def canvas_create_styledRectangle(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		lineType = lineStyle.lineType()
		thickness = lineStyle.thickness()

		command = []
		command.append(['_name_', 'rect'])
		command.append(['x', str(x0)])
		command.append(['y', str(y0)])
		command.append(['width', str(x1 - x0)])
		command.append(['height', str(y1 - y0)])
		command.append(['fill', fillStyle.color()])
		command.append(['stroke', lineStyle.color()])
		command.append(['stroke-width', str(lineStyle.thickness())])
		if lineType == 'solid':
			pass
		elif lineType == 'dot':
			command.append(['stroke-dasharray', '1,1'])
		elif lineType == 'dash':
			command.append(['stroke-dasharray', '3,3'])
		elif lineType == 'dash-dot':
			command.append(['stroke-dasharray', '3,2,1,2'])
		elif lineType == 'dash-dot-dot':
			command.append(['stroke-dasharray', '3,2,1,2,1,2'])
		else:
			raise RuntimeException()
		self._commands.append(command)

	def canvas_create_styledLine(self, lineStyle, tags, *points):
		lineType = lineStyle.lineType()

		command = []
		command.append(['_name_', 'polyline'])
		pointsString = ''
		for i in range(0, len(points) - 1, 2):
			pointsString += str(points[i]) + ',' + str(points[i + 1]) + ' '
		command.append(['points', pointsString])
		command.append(['fill', 'none'])
		command.append(['stroke', lineStyle.color()])
		command.append(['stroke-width', str(lineStyle.thickness())])
		if lineType == 'solid':
			pass
		elif lineType == 'dot':
			command.append(['stroke-dasharray', '1,1'])
		elif lineType == 'dash':
			command.append(['stroke-dasharray', '3,3'])
		elif lineType == 'dash-dot':
			command.append(['stroke-dasharray', '3,2,1,2'])
		elif lineType == 'dash-dot-dot':
			command.append(['stroke-dasharray', '3,2,1,2,1,2'])
		else:
			raise RuntimeException()
		self._commands.append(command)

	def canvas_create_styledPolygon(self, lineStyle, fillStyle, tags, *points):
		lineType = lineStyle.lineType()

		command = []
		command.append(['_name_', 'polyline'])
		pointsString = ''
		for i in range(0, len(points) - 1, 2):
			pointsString += str(points[i]) + ',' + str(points[i + 1]) + ' '
		command.append(['points', pointsString])
		command.append(['fill', fillStyle.color()])
		command.append(['stroke', lineStyle.color()])
		command.append(['stroke-width', str(lineStyle.thickness())])
		if lineType == 'solid':
			pass
		elif lineType == 'dot':
			command.append(['stroke-dasharray', '1,1'])
		elif lineType == 'dash':
			command.append(['stroke-dasharray', '3,3'])
		elif lineType == 'dash-dot':
			command.append(['stroke-dasharray', '3,2,1,2'])
		elif lineType == 'dash-dot-dot':
			command.append(['stroke-dasharray', '3,2,1,2,1,2'])
		else:
			raise RuntimeException()
		self._commands.append(command)

	def canvas_create_styledMarker(self, markerStyle, tags, x, y):
		shape = markerStyle.shape()
		shapeSize = markerStyle._parameterData('size')
		shapeSizeCanvasX = self._convertToPixelX(shapeSize)
		shapeSizeCanvasY = self._convertToPixelY(shapeSize)

		lineStyle = ILineStyle()
		lineStyle.setColor(markerStyle.color())
		fillStyle = IFillStyle()
		fillStyle.setColor('')

		if shape == '':
			return
		elif shape == 'circle':
			x0 = x - shapeSizeCanvasX / 2.0
			y0 = y - shapeSizeCanvasY / 2.0
			x1 = x0 + shapeSizeCanvasX
			y1 = y0 + shapeSizeCanvasY
			self.canvas_create_styledOval(lineStyle, fillStyle, tags, x0, y0, x1, y1)
		elif shape == 'square':
			x0 = x - shapeSizeCanvasX / 2.0
			y0 = y - shapeSizeCanvasY / 2.0
			x1 = x0 + shapeSizeCanvasX
			y1 = y0 + shapeSizeCanvasY
			self.canvas_create_styledRectangle(lineStyle, fillStyle, tags, x0, y0, x1, y1)
		elif shape == 'diamond':
			x0 = x
			y0 = y - shapeSizeCanvasY / 2.0
			x1 = x - shapeSizeCanvasX / 2.0
			y1 = y
			x2 = x
			y2 = y0 + shapeSizeCanvasY
			x3 = x1 + shapeSizeCanvasX
			y3 = y
			self.canvas_create_styledLine(lineStyle, tags, x0, y0, x1, y1, x2, y2, x3, y3, x0, y0)
		elif shape == 'triangle':
			sqrt3 = math.sqrt(3)
			x0 = x
			y0 = y - shapeSizeCanvasY / sqrt3
			x1 = x - shapeSizeCanvasX / 2.0
			y1 = y + shapeSizeCanvasY / sqrt3 / 2.0
			x2 = x1 + shapeSizeCanvasX
			y2 = y1
			self.canvas_create_styledLine(lineStyle, tags, x0, y0, x1, y1, x2, y2, x0, y0)
		elif shape == 'cross':
			x0 = x - shapeSizeCanvasX / 2.0
			y0 = y - shapeSizeCanvasY / 2.0
			x1 = x0 + shapeSizeCanvasX
			y1 = y0 + shapeSizeCanvasY
			self.canvas_create_styledLine(lineStyle, tags, x0, y0, x1, y1)
			self.canvas_create_styledLine(lineStyle, tags, x0, y1, x1, y0)

	def canvas_create_styledText(self, textStyle, tags, x, y, textData, anchor):
		fontData = self._configureSvgFont(self._canvasFont, textStyle)
		width = fontData.measure(textData)
		height = fontData.metrics('linespace')
		if anchor == N:
			x -= width / 2.0
			y += height
		elif anchor == NE:
			x -= width
			y += height
		elif anchor == E:
			x -= width
			y += height / 2.0
		elif anchor == SE:
			x -= width
		elif anchor == S:
			x -= width / 2.0
		elif anchor == SW:
			pass
		elif anchor == W:
			y += height / 2.0
		elif anchor == NW:
			y += height
		else:
			raise RuntimeException()

		command = []
		command.append(['_text_', textData])
		command.append(['x', str(x)])
		command.append(['y', str(y)])
		command.append(['font-size', str(textStyle.fontSize())])
		command.append(['font-family', textStyle.font()])
		self._commands.append(command)

	def canvas_delete(self, *args1):
		### Fix me!
		return

		self.getCanvas().delete(*args1)

	def canvas_create_styledExponent(self, textStyle, tags, x, y, a, b, anchor, fontRatio, overOffsetRatio):
		### Fix me!
		return

		canvas = self.getCanvas()
		widthSpacer = 1
		indexTextStyle = textStyle._createCopy()
		indexTextStyle.setFontSize(textStyle.fontSize() * fontRatio)
		fontDataBase = self._configureSvgFont(self._canvasExponentBaseFont, textStyle)
		fontDataIndex = self._configureSvgFont(self._canvasExponentIndexFont, indexTextStyle)
		widthBase = fontDataBase.measure(a)
		widthIndex = fontDataIndex.measure(b)
		widthAll = widthBase + widthIndex + widthSpacer
		heightBase = fontDataBase.metrics('linespace')
		heightIndex = fontDataIndex.metrics('linespace')
		heightAll = heightBase + heightIndex * overOffsetRatio
		heightCap = heightAll - heightBase
		textColor = textStyle.color()
		if anchor == N:
			xBase = x - widthAll / 2
			yBase = y + heightCap
		elif anchor == NE:
			xBase = x - widthAll
			yBase = y + heightCap
		elif anchor == E:
			xBase = x - widthAll
			yBase = y + heightAll / 2 - heightBase
		elif anchor == SE:
			xBase = x - widthAll
			yBase = y - heightBase
		elif anchor == S:
			xBase = x - widthAll / 2
			yBase = y - heightBase
		elif anchor == SW:
			xBase = x
			yBase = y - heightBase
		elif anchor == W:
			xBase = x
			yBase = y + heightAll / 2 - heightBase
		elif anchor == NW:
			xBase = x
			yBase = y + heightCap
		else:
			raise RuntimeException()
		xIndex = xBase + widthBase + widthSpacer
		yIndex = yBase - heightCap
		self.canvas_create_styledText(textStyle, tags, xBase, yBase, a, NW)
		self.canvas_create_styledText(indexTextStyle, tags, xIndex, yIndex, b, NW)
