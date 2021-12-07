from paida.paida_core.PAbsorber import *
from paida.paida_core.IFillStyle import *
from paida.paida_core.ILineStyle import *
from paida.paida_core.ITextStyle import *

from Tkinter import Tk, Toplevel, Button, PhotoImage, Frame, Canvas, Scrollbar, VERTICAL, HORIZONTAL
import Tkinter
import tkFont
try:
	import threading
except ImportError:
	import dummy_threading as threading
import time
import math

N = Tkinter.N
NE = Tkinter.NE
E = Tkinter.E
SE = Tkinter.SE
S = Tkinter.S
SW = Tkinter.SW
W = Tkinter.W
NW = Tkinter.NW
CENTER = Tkinter.CENTER

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
	_fontRoot = Tk()
	_fontRoot.withdraw()
	_fontRoot.tk.call('tk', 'useinputmethods', 'False')
	_fontRoot.tk.call('tk', 'scaling', '1.0')
	fontList = list(tkFont.families(_fontRoot))
	fontList.sort()
	defaultFont = Button(_fontRoot).cget('font')

	if not defaultFont in fontList:
		fontList.append(defaultFont)
	for _defaultCandidate in _defaultCandidates:
		if _defaultCandidate in fontList:
			defaultFont = _defaultCandidate

	_fontRoot.destroy()
	return fontList, defaultFont



class _Root(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._setRootCondition(threading.Condition())

	def run(self):
		rootCondition = self._getRootCondition()
		rootCondition.acquire()
		self._setRoot(Tk())
		root = self._getRoot()
		root.withdraw()
		root.tk.call('tk', 'useinputmethods', 'False')
		root.tk.call('tk', 'scaling', '1.0')
		root.grid()

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
		self._mainloop()

		while 1:
			if self._getQuitLoop():
				rootCondition = self._getRootCondition()
				rootCondition.acquire()
				### Wait other threads.
				lock = self._getLock()
				lock.acquire()
				lock.release()
				rootCondition.notifyAll()
				rootCondition.release()
				break
			root.update()
			time.sleep(0.1)

	def _mainloop(self):
		lock = self._getLock()
		if lock.acquire(blocking = 0):
			self._check()
			lock.release()
		self._getRoot().after(300, self._mainloop)

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

	def _setRoot(self, root):
		self._root = root

	def _getRoot(self):
		return self._root

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

		for tree in self._getTrees():
			tree.update()

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

		for plotter in self._getPlotters():
			plotter.update()

class _Base:
	def __init__(self, lock):
		self._canvasCommands = []
		self._sizeCommands = []
		self.setLock(lock)

		### Create widges.
		self.setRoot(Toplevel())
		root = self.getRoot()
		root.tk.call('tk', 'useinputmethods', 'False')
		root.grid_rowconfigure(0, weight = 1)
		root.grid_columnconfigure(0, weight = 1)
		self.setFrame(Frame(root))
		frame = self.getFrame()
		frame.grid()
		self.setCanvas(Canvas(frame))
		canvas = self.getCanvas()
		canvas.scrollX = Scrollbar(frame, orient = HORIZONTAL)
		canvas.scrollY = Scrollbar(frame, orient = VERTICAL)
		canvas.scrollX.grid(column = '0', row = '1', sticky= E + W)
		canvas.scrollY.grid(column = '1', row = '0', sticky= N + S)
		canvas.configure(xscrollcommand = self.xscroll)
		canvas.configure(yscrollcommand = self.yscroll)
		canvas.scrollX.configure(command = self.xview)
		canvas.scrollY.configure(command = self.yview)
		canvas.grid(column = '0', row = '0', sticky = N + E + S + W)

		self._setFontCondition(threading.Condition())
		textStyle = ITextStyle()
		textStyle.setBold(False)
		textStyle.setUnderlined(False)
		self._fontMeasurement = self._createTkFont(textStyle)

		self.setShow(True)
		self.setTitle('')

	def _sizeChanged(self, event):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_sizeChanged, [event], {}])
		self.getLock().release()

	def canvas_sizeChanged(self, event):
		root = self.getRoot()
		frame = self.getFrame()
		canvas = self.getCanvas()
		if (root is None) or (frame is None) or (canvas is None):
			return

		frame.unbind('<Configure>')
		canvas.configure(xscrollcommand = self.canvas_xscroll)
		canvas.configure(yscrollcommand = self.canvas_yscroll)
		canvas.scrollX.configure(command = self.canvas_xview)
		canvas.scrollY.configure(command = self.canvas_yview)

		pad = 5
		padX = int(canvas.scrollX.cget('width')) + pad
		padY = int(canvas.scrollY.cget('width')) + pad
		x = root.winfo_width()
		y = root.winfo_height()
		canvas.configure(width = x - padX, height = y - padY)
		root.update_idletasks()

		canvas.configure(xscrollcommand = self.xscroll)
		canvas.configure(yscrollcommand = self.yscroll)
		canvas.scrollX.configure(command = self.xview)
		canvas.scrollY.configure(command = self.yview)
		frame.bind('<Configure>', self._sizeChanged)

	def _setFontCondition(self, condition):
		self._fontCondition = condition

	def _getFontCondition(self):
		return self._fontCondition

	def getNCanvasCommands(self):
		return len(self._canvasCommands)

	def setRoot(self, root):
		self._root = root

	def getRoot(self):
		return self._root

	def setFrame(self, frame):
		self._frame = frame

	def getFrame(self):
		return self._frame

	def setCanvas(self, canvas):
		self._canvas = canvas

	def getCanvas(self):
		return self._canvas

	def setLock(self, lock):
		self._lock = lock

	def getLock(self):
		return  self._lock

	def xscroll(self, *args):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_xscroll, args, {}])
		self.getLock().release()

	def yscroll(self, *args):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_yscroll, args, {}])
		self.getLock().release()

	def xview(self, *args):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_xview, args, {}])
		self.getLock().release()

	def yview(self, *args):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_yview, args, {}])
		self.getLock().release()

	def canvas_xscroll(self, *args1):
		canvas = self.getCanvas()
		if canvas is not None:
			canvas.scrollX.set(*args1)

	def canvas_yscroll(self, *args1):
		canvas = self.getCanvas()
		if canvas is not None:
			canvas.scrollY.set(*args1)

	def canvas_xview(self, *args1):
		canvas = self.getCanvas()
		if canvas is not None:
			canvas.xview(*args1)

	def canvas_yview(self, *args1):
		canvas = self.getCanvas()
		if canvas is not None:
			canvas.yview(*args1)

	def canvas_title(self, title):
		self.getFrame().master.title(title)
		self._title = title

	def canvas_show(self, boolean):
		if boolean == True:
			self.getRoot().deiconify()
		else:
			self.getRoot().withdraw()
		self._show = boolean

	def canvas_terminate(self):
		self.getCanvas().destroy()
		self.setCanvas(None)
		self.getFrame().destroy()
		self.setFrame(None)
		self.getRoot().destroy()
		self.setRoot(None)

		self._fontMeasurement = None

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

	def _createTkFont(self, textStyle):
		fontFamily = textStyle.font()
		fontSize = int(textStyle.fontSize())
		if textStyle.isBold():
			fontWeight = 'bold'
		else:
			fontWeight = 'normal'
		if textStyle.isItalic():
			fontSlant = 'italic'
		else:
			fontSlant = 'roman'
		if textStyle.isUnderlined():
			fontUnderline = 1
		else:
			fontUnderline = 0
		return tkFont.Font(family=fontFamily, size=fontSize, weight=fontWeight, slant=fontSlant, underline=fontUnderline)

	def _configureTkFont(self, font, textStyle):
		fontFamily = textStyle.font()
		fontSize = int(textStyle.fontSize())
		if textStyle.isBold():
			fontWeight = 'bold'
		else:
			fontWeight = 'normal'
		if textStyle.isItalic():
			fontSlant = 'italic'
		else:
			fontSlant = 'roman'
		if textStyle.isUnderlined():
			fontUnderline = 1
		else:
			fontUnderline = 0
		font.configure(family=fontFamily, size=fontSize, weight=fontWeight, slant=fontSlant, underline=fontUnderline)
		return font

	def _getFontTuple(self, textStyle):
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
		fontCondition = self._getFontCondition()
		fontCondition.acquire()
		result = []
		fontMeasurement = self._fontMeasurement
		for textStyle, text in textDataList:
			fontMeasurement = self._configureTkFont(fontMeasurement, textStyle)
			result.append([fontMeasurement.measure(text), fontMeasurement.metrics('linespace')])
		bridge.append(result)
		fontCondition.notifyAll()
		fontCondition.release()

	def update(self):
		self.getLock().acquire()
		for [method, args1, args2] in self._canvasCommands:
			method(*args1, **args2)
		else:
			self._canvasCommands = []
		self.getLock().release()

class _Tree(_Base):
	_folderIconString = 'R0lGODlhDgAPAIIAAA4ODkhz///U1ABV/46r/wAAAAAAAAAAACH5BAEAAAIALAAAAAAOAA8AAAhX\nAAUIHAgAwMCDBAEECFAQoYCCCyMyNChQocSLBiFelFgQAAGNHAEMKEigpMaCA1KSLGlSZEqVHll+\nfPlyJUuXNG2apKnyoUycPSvGxNkQYceRFB0KdRgQADs=\n'
	_fileIconString = 'R0lGODlhCgAKAIIAACVX/7HH/9Tj/2uP/////wAAAAAAAAAAACH5BAEAAAQALAAAAAAKAAoAAAg0\nAAkIHEiQAICDCAkiRDhAgMCFBwcEcAgRgESKEC8azDhR4ICPIDsSEBCgpEmHAgWoXEkgIAA7\n'

	def __init__(self, lock):
		_Base.__init__(self, lock)
		self.getCanvas().configure(bg='white', width=300)

		self._folderImage = PhotoImage(data = self._folderIconString)
		self._folderImageWidth = self._folderImage.width()
		self._folderImageHeight = self._folderImage.height()
		self._fileImage = PhotoImage(data = self._fileIconString)
		self._fileImageWidth = self._fileImage.width()
		self._fileImageHeight = self._fileImage.height()

		textStyle = ITextStyle()
		textStyle.setBold(False)
		textStyle.setUnderlined(False)
		self._fontNormal = self._createTkFont(textStyle)
		textStyle.setBold(True)
		textStyle.setUnderlined(True)
		self._fontSelected = self._createTkFont(textStyle)

		self.getFrame().bind('<Configure>', self._sizeChanged)

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
		canvas = self.getCanvas()
		canvas.delete(['allItems'])
		pwd = itree._getPwd()
		self.redrawTreeWalker(itree, pwd, canvas, '/', 10, 10)
		result = canvas.bbox('all')
		if result != None:
			cx1, cy1, cx2, cy2 = result
			canvas.configure(scrollregion = (0, 0, cx2 + 10, cy2 + 10))

	def redrawTreeWalker(self, itree, pwd, canvas, directoryPath, x, y):
		spaceX = 16
		spaceY = 4
		stringSpaceX = 4
		fileX = x + self._fileImageWidth + stringSpaceX
		fontNormal = self._fontNormal
		fileImage = self._fileImage
		tags = ['allItems']
		objects = itree._listObjects(directoryPath)
		for object in objects:
			if object._instance:
				canvas.create_image(x, y, image = fileImage, anchor = W, tags = tags)
				canvas.create_text(fileX, y, text = object.name(), font = fontNormal, anchor = W , tags = tags)
				y += spaceY + self._fileImageHeight
			else:
				### Subdirectory.
				canvas.create_image(x, y, image = self._folderImage, anchor = W, tags = tags)
				if object == pwd:
					canvas.create_text(x + self._folderImageWidth + stringSpaceX, y, text = object.name(), font = self._fontSelected, anchor = W , tags=tags)
				else:
					canvas.create_text(x + self._folderImageWidth + stringSpaceX, y, text = object.name(), font = fontNormal, anchor = W , tags=tags)
				y += spaceY + self._folderImageHeight
				x2, y = self.redrawTreeWalker(itree, pwd, canvas, '%s/%s' % (directoryPath, object.name()), x + spaceX, y)
		return x, y

class _Plotter(_Base):
	def __init__(self, lock, viewWidth, viewHeight, width, height):
		_Base.__init__(self, lock)
		canvas = self.getCanvas()
		canvas.configure(bg='white')
		self.setImageIOCondition(threading.Condition())

		self._legendsFont = self._createTkFont(ITextStyle())
		self._statisticsFont = self._createTkFont(ITextStyle())
		self._textsFont = self._createTkFont(ITextStyle())
		self._canvasFont = self._createTkFont(ITextStyle())
		self._canvasExponentBaseFont = self._createTkFont(ITextStyle())
		self._canvasExponentIndexFont = self._createTkFont(ITextStyle())

		self.setViewWidth(canvas.winfo_pixels(viewWidth))
		self.setViewHeight(canvas.winfo_pixels(viewHeight))
		self.setScrollRegion(0, 0, canvas.winfo_pixels(width), canvas.winfo_pixels(height))

		self.getFrame().bind('<Configure>', self._sizeChanged)

	def _requestRegion(self, serialNumber, allTags, x0, y0, x1, y1):
		### Nothing to do for Tkinter GUI.
		pass

	def _convertToPixelX(self, length):
		return self.getCanvas().winfo_pixels(length)

	def _convertToPixelY(self, length):
		return self.getCanvas().winfo_pixels(length)

	def setImageIOCondition(self, condition):
		self._imageIOCondition = condition

	def getImageIOCondition(self):
		return self._imageIOCondition

	def setScrollRegion(self, *args):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_scrollRegion, args, {}])
		self.getLock().release()

	def getScrollRegion(self):
		return self._scrollRegion

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
		canvas = self.getCanvas()
		cx0 = canvas.winfo_pixels(x0)
		cy0 = canvas.winfo_pixels(y0)
		cx1 = canvas.winfo_pixels(x1)
		cy1 = canvas.winfo_pixels(y1)
		self._scrollRegion = (cx0, cy0, cx1, cy1)
		canvas.configure(scrollregion = (cx0, cy0, cx1, cy1))

	def canvas_viewWidth(self, viewWidth):
		canvas = self.getCanvas()
		self._viewWidth = canvas.winfo_pixels(viewWidth)
		screenWidth = canvas.winfo_screenwidth()
		canvas.configure(width = min(self._viewWidth, screenWidth))

	def canvas_viewHeight(self, viewHeight):
		canvas = self.getCanvas()
		self._viewHeight = canvas.winfo_pixels(viewHeight)
		padY = 80
		screenHeight = canvas.winfo_screenheight() - padY
		canvas.configure(height = min(self._viewHeight, screenHeight))

	def canvas_create_styledLegendsBox(self, infoStyle, region, layout, legends, tags):
		self.canvas_delete(tags)
		textStyle = infoStyle.textStyle()
		fontData = self._configureTkFont(self._legendsFont, textStyle)
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
		fontData = self._configureTkFont(self._statisticsFont, textStyle)
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
		fontData = self._configureTkFont(self._textsFont, textStyle)
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
		postscriptCondition = self.getImageIOCondition()
		postscriptCondition.acquire()
		x = self.getScrollRegion()[2]
		y = self.getScrollRegion()[3]
		self.getCanvas().postscript(file = fileName, width = x, height = y, rotate = landscape)
		postscriptCondition.notifyAll()
		postscriptCondition.release()

	def canvas_postscriptStrings(self, landscape, bridge):
		postscriptCondition = self.getImageIOCondition()
		postscriptCondition.acquire()
		x = self.getScrollRegion()[2]
		y = self.getScrollRegion()[3]
		bridge.append([self.getCanvas().postscript(pagewidth = x, pageheight = y, rotate = landscape)])
		postscriptCondition.notifyAll()
		postscriptCondition.release()

	def canvas_create_styledOval(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		self.getCanvas().create_oval(x0, y0, x1, y1, fill=fillStyle.color(), outline = lineStyle.color(), width = lineStyle.thickness(), tags = tags)

	def canvas_create_styledRectangle(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		lineType = lineStyle.lineType()
		thickness = lineStyle.thickness()

		if lineType == 'solid':
			self.getCanvas().create_rectangle(x0, y0, x1, y1, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, tags = tags)
		elif lineType == 'dot':
			self.getCanvas().create_rectangle(x0, y0, x1, y1, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, dash = '.', tags = tags)
		elif lineType == 'dash':
			self.getCanvas().create_rectangle(x0, y0, x1, y1, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, dash = '-', tags = tags)
		elif lineType == 'dash-dot':
			self.getCanvas().create_rectangle(x0, y0, x1, y1, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, dash = '-.', tags = tags)
		elif lineType == 'dash-dot-dot':
			self.getCanvas().create_rectangle(x0, y0, x1, y1, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, dash = '-..', tags = tags)
		else:
			raise RuntimeException()

	def canvas_create_styledLine(self, lineStyle, tags, *points):
		lineType = lineStyle.lineType()
		thickness = lineStyle.thickness()

		if lineType == 'solid':
			self.getCanvas().create_line(points, fill = lineStyle.color(), width = thickness, tags = tags)
		elif lineType == 'dot':
			self.getCanvas().create_line(points, fill = lineStyle.color(), width = thickness, dash = '.', tags = tags)
		elif lineType == 'dash':
			self.getCanvas().create_line(points, fill = lineStyle.color(), width = thickness, dash = '-', tags = tags)
		elif lineType == 'dash-dot':
			self.getCanvas().create_line(points, fill = lineStyle.color(), width = thickness, dash = '-.', tags = tags)
		elif lineType == 'dash-dot-dot':
			self.getCanvas().create_line(points, fill = lineStyle.color(), width = thickness, dash = '-..', tags = tags)
		else:
			raise RuntimeException()

	def canvas_create_styledPolygon(self, lineStyle, fillStyle, tags, *points):
		lineType = lineStyle.lineType()
		thickness = lineStyle.thickness()

		if lineType == 'solid':
			self.getCanvas().create_polygon(points, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, tags = tags)
		elif lineType == 'dot':
			self.getCanvas().create_polygon(points, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, dash = '.', tags = tags)
		elif lineType == 'dash':
			self.getCanvas().create_polygon(points, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, dash = '-', tags = tags)
		elif lineType == 'dash-dot':
			self.getCanvas().create_polygon(points, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, dash = '-.', tags = tags)
		elif lineType == 'dash-dot-dot':
			self.getCanvas().create_polygon(points, fill = fillStyle.color(), outline = lineStyle.color(), width = thickness, dash = '-..', tags = tags)
		else:
			raise RuntimeException()

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
		self.getCanvas().create_text(x, y, text = textData, fill = textStyle.color(), font = self._getFontTuple(textStyle), anchor = anchor, tags = tags)

	def canvas_delete(self, *args1):
		self.getCanvas().delete(*args1)

	def canvas_create_styledExponent(self, textStyle, tags, x, y, a, b, anchor, fontRatio, overOffsetRatio):
		canvas = self.getCanvas()
		widthSpacer = 1
		indexTextStyle = textStyle._createCopy()
		indexTextStyle.setFontSize(textStyle.fontSize() * fontRatio)
		fontDataBase = self._configureTkFont(self._canvasExponentBaseFont, textStyle)
		fontDataIndex = self._configureTkFont(self._canvasExponentIndexFont, indexTextStyle)
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
