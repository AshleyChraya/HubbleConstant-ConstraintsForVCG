from paida.paida_core.PAbsorber import *
from paida.paida_core.IFillStyle import *
from paida.paida_core.ILineStyle import *
from paida.paida_core.IMarkerStyle import *
from paida.paida_core.ITextStyle import *

from javax.swing import JFrame, JPanel, JScrollPane, JTree, JLayeredPane, SwingUtilities, JMenuBar
from javax.swing.tree import DefaultTreeModel, DefaultMutableTreeNode
from javax.imageio import ImageIO
from java.awt import GraphicsEnvironment, Font, Color, Dimension, BasicStroke, RenderingHints, FlowLayout, Toolkit
from java.awt.geom import Rectangle2D, Ellipse2D, Line2D, GeneralPath
from java.awt.image import BufferedImage
from java.awt.event import ComponentListener, WindowAdapter
from java.lang import Runnable
from java.util import Timer, TimerTask

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

def startRoot():
	global _guiRoot
	_guiRoot.start()

def getRoot():
	global _guiRoot
	return _guiRoot

def getFontList(_defaultCandidates):
	fontList = list(GraphicsEnvironment.getLocalGraphicsEnvironment().getAvailableFontFamilyNames())
	fontList.sort()
	### Dialog, DialogInput, Monospaced, Serif and SansSerif are always available in JAVA.
	defaultFont = 'SansSerif'

	for _defaultCandidate in _defaultCandidates:
		if _defaultCandidate in fontList:
			defaultFont = _defaultCandidate

	return fontList, defaultFont

class _PlotterTask(TimerTask):
	def __init__(self):
		self._plotterSize = None
		self._treeSize = None

	def run(self):
		for plotter in getRoot()._getPlotters():
			if plotter._getFrame().getSize() != self._plotterSize:
				dispatch = _EventDispatch()
				dispatch._set(plotter._getFrame()._edtFitToFrameSize)
				SwingUtilities.invokeAndWait(dispatch)
				self._plotterSize = dispatch._getResult()

			if plotter._getCommandModified():
				plotter.refresh()
				plotter._setCommandModified(False)

		for tree in getRoot()._getTrees():
			if tree._getFrame().getSize() != self._treeSize:
				dispatch = _EventDispatch()
				dispatch._set(tree._getFrame()._edtFitToFrameSize)
				SwingUtilities.invokeAndWait(dispatch)
				self._treeSize = dispatch._getResult()

class _DummyCondition:
	def acquire(self):
		pass

	def wait(self):
		pass

	def notifyAll(self):
		pass

	def release(self):
		pass

class _DummyLock:
	def acquire(self):
		pass

	def release(self):
		pass

class _EventDispatch(Runnable):
	def _set(self, method, *data1, **data2):
		self._method = method
		self._data1 = data1
		self._data2 = data2

	def run(self):
		self._result = self._method(*self._data1, **self._data2)

	def _getResult(self):
		return self._result

class _Root:
	def __init__(self):
		self._trees = []
		self._plotters = []
		self._requestedTrees = []
		self._requestedPlotters = []
		self._setRootCondition(_DummyCondition())
		self._setLock(_DummyLock())

	def start(self):
		plotterTask = _PlotterTask()
		plotterTimer = Timer(True)
		plotterTimer.schedule(plotterTask, 500, 500)

	def _setLock(self, lock):
		self._lock = lock

	def _getLock(self):
		return self._lock

	def _setRootCondition(self, Condition):
		self._rootCondition = Condition

	def _getRootCondition(self):
		return self._rootCondition

	def _setQuitLoop(self, boolean):
		dispatch = _EventDispatch()
		dispatch._set(self._edtQuit)
		SwingUtilities.invokeLater(dispatch)

	def _edtQuit(self):
		import java.lang.System
		java.lang.System.exit(0)

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
		tree = _Tree()
		self._appendTree(tree)
		return tree

	def _requestPlotter(self, viewWidth, viewHeight, width, height):
		plotter = _Plotter(viewWidth, viewHeight, width, height)
		self._appendPlotter(plotter)
		return plotter

class _WindowAdapter(WindowAdapter):
	def __init__(self, showMethod):
		WindowAdapter.__init__(self)
		self._showMethod = showMethod

	def windowClosing(self, event):
		self._showMethod(False)

class _Menu(JMenuBar):
	def __init__(self):
		JMenuBar.__init__(self)
		self.setPreferredSize(Dimension(0, 0))

	def setPreferredSize(self, size):
		self._size = size
		JScrollPane.setPreferredSize(self, size)
		JScrollPane.setMinimumSize(self, size)
		JScrollPane.setMaximumSize(self, size)

	def getPreferredSize(self):
		return self._size

	def getMinimumSize(self):
		return self.getPreferredSize()

class _Frame(JFrame, ComponentListener):
	def __init__(self, scroll, showMethod, offsetX, offsetY):
		JFrame.__init__(self)
		self.setBounds(offsetX, offsetY, 1, 1)
		self.setJMenuBar(_Menu())
		self._setScroll(scroll)
		self.getContentPane().setLayout(FlowLayout(FlowLayout.CENTER, 0, 0))
		self.getContentPane().add(scroll)
		self.addComponentListener(self)
		self.addWindowListener(_WindowAdapter(showMethod))
		self._setSizeChanged(False)

	def _setScroll(self, scroll):
		self._scroll = scroll

	def _getScroll(self):
		return self._scroll

	def _edtFitToFrameSize(self):
		frameSize = self.getSize()

		frameInsets = self.getInsets()
		frameX = frameInsets.left + frameInsets.right
		frameY = frameInsets.top + frameInsets.bottom

		menuInsets = self.getJMenuBar().getInsets()
		menuX = menuInsets.left + menuInsets.right
		menuY = menuInsets.top + menuInsets.bottom

		scrollPadX, scrollPadY = self._getScroll()._getScrollPad()

		viewSizeX = frameSize.width  - menuX - frameX - scrollPadX
		viewSizeY = frameSize.height - menuY - frameY - scrollPadY
		self._edtSetViewSize(viewSizeX, viewSizeY)

		self.validate()
		return self.getSize()

	def _edtSetViewSize(self, sizeX, sizeY):
		bounds = self.getBounds()

		screenInsets = self.getToolkit().getScreenInsets(self.getGraphicsConfiguration())
		screenX = screenInsets.left + screenInsets.right
		screenY = screenInsets.top + screenInsets.bottom

		frameInsets = self.getInsets()
		frameX = frameInsets.left + frameInsets.right
		frameY = frameInsets.top + frameInsets.bottom

		menuInsets = self.getJMenuBar().getInsets()
		menuX = menuInsets.left + menuInsets.right
		menuY = menuInsets.top + menuInsets.bottom

		scrollInsets = self._getScroll().getInsets()
		scrollX = scrollInsets.left + scrollInsets.right
		scrollY = scrollInsets.top + scrollInsets.bottom
		scrollPadX, scrollPadY = self._getScroll()._getScrollPad()

		screenSize = Toolkit.getDefaultToolkit().getScreenSize()
		widthMax = screenSize.width - bounds.x - screenX - (scrollPadX + frameX + menuX)
		heightMax = screenSize.height - bounds.y - screenY - (scrollPadY + frameY + menuY)
		width = min(sizeX, widthMax)
		height = min(sizeY, heightMax)
		self._getScroll().setPreferredSize(Dimension(width + scrollPadX + scrollX, height + scrollPadY + scrollY))
		self._getScroll().revalidate()

		frameSize = Dimension(width + scrollPadX + frameX + menuX, height + scrollPadY + frameY + menuY)
		self.setSize(frameSize)
		self.setBounds(bounds.x, bounds.y, frameSize.width, frameSize.height)

	def _setSizeChanged(self, boolean):
		self._sizeChanged = boolean

	def _getSizeChanged(self):
		return self._sizeChanged

	def componentResized(self, event):
		self._setSizeChanged(True)

	def componentMoved(self, event):
		pass

	def componentShown(self, event):
		pass

	def componentHidden(self, event):
		pass

class _Scroll(JScrollPane):
	def __init__(self, child, policyX, policyY):
		JScrollPane.__init__(self, child, policyX, policyY)
		self._size = Dimension(0, 0)
		self.setBackground(Color.white)

	def _getScrollPad(self):
		scrollBarX = int(self.getVerticalScrollBar().getMaximumSize().getWidth())
		scrollBarY = int(self.getHorizontalScrollBar().getMaximumSize().getHeight())
		return scrollBarX, scrollBarY

	def setPreferredSize(self, size):
		self._size = size
		JScrollPane.setPreferredSize(self, size)
		JScrollPane.setMinimumSize(self, size)
		JScrollPane.setMaximumSize(self, size)

	def getPreferredSize(self):
		return self._size

	def getMinimumSize(self):
		return self.getPreferredSize()

class _Base:
	def __init__(self, offsetX = 10, offsetY = 10):
		dispatch = _EventDispatch()
		dispatch._set(_Scroll, self._getViewComponent(), JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_ALWAYS)
		SwingUtilities.invokeAndWait(dispatch)
		scroll = dispatch._getResult()

		dispatch = _EventDispatch()
		dispatch._set(_Frame, scroll, self.setShow, offsetX, offsetY)
		SwingUtilities.invokeAndWait(dispatch)
		frame = dispatch._getResult()

		self._setFrame(frame)
		self.setTitle('')

	def _setFrame(self, frame):
		self._frame = frame

	def _getFrame(self):
		return self._frame

	def _getScroll(self):
		return self._getFrame()._getScroll()

	def _setViewComponent(self, component):
		self._viewComponent = component

	def _getViewComponent(self):
		return self._viewComponent

	def _terminateBase(self):
		self._setViewComponent(None)
		frame = self._getFrame()
		self._setFrame(None)

		dispatch = _EventDispatch()
		dispatch._set(frame.setVisible, False)
		SwingUtilities.invokeLater(dispatch)

		dispatch = _EventDispatch()
		dispatch._set(frame.removeAll)
		SwingUtilities.invokeLater(dispatch)

	def setTitle(self, title):
		self._title = title
		dispatch = _EventDispatch()
		dispatch._set(self._getFrame().setTitle, title)
		SwingUtilities.invokeLater(dispatch)

	def getTitle(self):
		return self._title

	def setShow(self, boolean):
		self._show = boolean
		frame = self._getFrame()

		dispatch = _EventDispatch()
		dispatch._set(frame.setVisible, boolean)
		SwingUtilities.invokeAndWait(dispatch)

		dispatch = _EventDispatch()
		dispatch._set(frame.validate)
		SwingUtilities.invokeAndWait(dispatch)

	def getShow(self):
		return self._show

class _Tree(_Base):
	def __init__(self):
		dispatch = _EventDispatch()
		dispatch._set(DefaultMutableTreeNode, '')
		SwingUtilities.invokeAndWait(dispatch)
		rootNode = dispatch._getResult()

		dispatch = _EventDispatch()
		dispatch._set(DefaultTreeModel, rootNode)
		SwingUtilities.invokeAndWait(dispatch)
		treeModel = dispatch._getResult()

		dispatch = _EventDispatch()
		dispatch._set(JTree, treeModel)
		SwingUtilities.invokeAndWait(dispatch)
		tree = dispatch._getResult()

		self._setViewComponent(tree)
		_Base.__init__(self)

		self.setShow(True)

		dispatch = _EventDispatch()
		dispatch._set(self._getFrame()._edtSetViewSize, 300, 300)
		SwingUtilities.invokeAndWait(dispatch)

	def _getTreeModel(self):
		return self._getViewComponent().getModel()

	def _getRootNode(self):
		return self._getTreeModel().getRoot()

	def terminate(self):
		getRoot()._removeTree(self)
		_Base._terminateBase(self)

	def redrawTree(self, block, itree):
		if block:
			invoker = SwingUtilities.invokeAndWait
		else:
			invoker = SwingUtilities.invokeLater

		dispatch = _EventDispatch()
		dispatch._set(self._edtDoRedrawTree, itree)
		invoker(dispatch)

		frame = self._getFrame()

		dispatch = _EventDispatch()
		dispatch._set(frame.validate)
		invoker(dispatch)

		dispatch = _EventDispatch()
		dispatch._set(frame.repaint)
		invoker(dispatch)

	def _edtDoRedrawTree(self, itree):
		rootNode = self._getRootNode()
		rootNode.removeAllChildren()
		pwd = itree._getPwd()
		self._edtRedrawTreeWalker(itree, rootNode, '/')
		self._getViewComponent().expandRow(0)
		self._getTreeModel().reload()

	def _edtRedrawTreeWalker(self, itree, node, directoryPath):
		for object in itree._listObjects(directoryPath):
			if object._instance:
				node.add(DefaultMutableTreeNode(object.name()))
			else:
				name = object.name()
				newNode = DefaultMutableTreeNode(name)
				node.add(newNode)
				self._edtRedrawTreeWalker(itree, newNode, '%s/%s' % (directoryPath, name))

class _Panel(JPanel):
	def __init__(self, sizeX, sizeY, plotter):
		JPanel.__init__(self)
		self._commands = []
		self._setPlotter(plotter)

		dispatch = _EventDispatch()
		dispatch._set(self._edtInit, Dimension(sizeX, sizeY))
		SwingUtilities.invokeAndWait(dispatch)

	def _edtInit(self, size):
		self.setPreferredSize(size)
		self.setOpaque(True)
		self.setBackground(Color.white)

	def _setPlotter(self, plotter):
		self._plotter = plotter

	def _getPlotter(self):
		return self._plotter

	def paintComponent(self, graphics):
		self.super__paintComponent(graphics)
		graphics.drawImage(self._getCurrentImageBuffer(), 0, 0, self)

	def _edtRepaintAll(self, graphics):
		currentGraphics = self._getCurrentGraphics()
		self._setCurrentGraphics(graphics)
		for [tags, [method, args1, args2]] in self._commands[:]:
			method(*args1, **args2)
		self._setCurrentGraphics(currentGraphics)

	def _setCurrentImageBuffer(self, imageBuffer):
		self._currentImageBuffer = imageBuffer

	def _getCurrentImageBuffer(self):
		return self._currentImageBuffer

	def _setCurrentGraphics(self, graphics):
		self._currentGraphics = graphics

	def _getCurrentGraphics(self):
		return self._currentGraphics

	def setPreferredSize(self, size):
		self._size = size
		JPanel.setPreferredSize(self, size)
		JPanel.setMinimumSize(self, size)
		JPanel.setMaximumSize(self, size)

	def getPreferredSize(self):
		return self._size

	def getMinimumSize(self):
		return self.getPreferredSize()

	def _addCommand(self, tags, command):
		self._commands.append([tags, command])

	def _removeCommands(self, targetTags):
		plotter = self._getPlotter()
		newCommands = []
		for i, command in enumerate(self._commands):
			if command[0] != targetTags:
				newCommands.append(command)
			elif command[1][0] == plotter._edt_delete:
				newCommands.extend(self._commands[i + 1:])
				break
		self._commands = newCommands

	def _existsTags(self, targetTags):
		for command in self._commands:
			if command[0] == targetTags:
				return True
		else:
			return False

class _Plotter(_Base):
	def __init__(self, viewWidth, viewHeight, width, height):
		x = int(self._convertToPixelX(width))
		y = int(self._convertToPixelY(height))
		viewX = int(self._convertToPixelX(viewWidth))
		viewY = int(self._convertToPixelY(viewHeight))
		self._setViewComponent(_Panel(x, y, self))
		self._scrollRegion = (0, 0, x, y)
		self._setCommandModified(False)
		self._setLock(_DummyLock())

		self._setPlotterCondition(_DummyCondition())
		self.setImageIOCondition(_DummyCondition())
		self._setFontCondition(_DummyCondition())

		self._fontMeasurement = self._createSwingFont(ITextStyle())
		self._legendsFont = self._createSwingFont(ITextStyle())
		self._statisticsFont = self._createSwingFont(ITextStyle())
		self._textsFont = self._createSwingFont(ITextStyle())
		self._canvasFont = self._createSwingFont(ITextStyle())
		self._canvasExponentBaseFont = self._createSwingFont(ITextStyle())
		self._canvasExponentIndexFont = self._createSwingFont(ITextStyle())

		_Base.__init__(self, 50, 50)
		self.setShow(True)

		dispatch = _EventDispatch()
		dispatch._set(self._edtInit, viewX, viewY)
		SwingUtilities.invokeAndWait(dispatch)

	def _edtInit(self, viewX, viewY):
		imageBuffer, graphics = self._createGraphicsForImageBuffer()
		graphics.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
		panel = self._getViewComponent()
		panel._setCurrentImageBuffer(imageBuffer)
		panel._setCurrentGraphics(graphics)
		self._getFrame()._edtSetViewSize(viewX, viewY)

	def _setLock(self, lock):
		self._lock = lock

	def getLock(self):
		return self._lock

	def getNCanvasCommands(self):
		return 0

	def _requestRegion(self, serialNumber, allTags, x0, y0, x1, y1):
		return

	def _setFontCondition(self, condition):
		self._fontCondition = condition

	def _getFontCondition(self):
		return self._fontCondition

	def _setCommandModified(self, boolean):
		self._commandModified = boolean

	def _getCommandModified(self):
		return self._commandModified

	def _createSwingFont(self, textStyle):
		if textStyle.isBold():
			if textStyle.isItalic():
				style = Font.BOLD | Font.ITALIC
			else:
				style = Font.BOLD
		else:
			if textStyle.isItalic():
				style = Font.ITALIC
			else:
				style = Font.PLAIN
		return Font(textStyle.font(), style, int(textStyle.fontSize()))

	def _configureSwingFont(self, font, textStyle):
		return self._createSwingFont(textStyle)

	def _getFontMeasurements(self, textDataList, bridge):
		result = []
		fontMeasurement = self._fontMeasurement
		for textStyle, text in textDataList:
			rectangle = self._fontMeasure(textStyle, text)[0]
			result.append((rectangle.getWidth(), rectangle.getHeight()))
		bridge.append(result)

	def _fontMeasure(self, textStyle, text):
		return self._swingFontMeasure(self._configureSwingFont(self._fontMeasurement, textStyle), text)

	def _swingFontMeasure(self, swingFont, text):
		fontRenderContext = self._getViewComponent().getGraphics().getFontRenderContext()
		rectangle = swingFont.getStringBounds(text, fontRenderContext)
		metrics = swingFont.getLineMetrics(text, fontRenderContext)
		return (rectangle, metrics)

	def getScrollRegion(self):
		return self._scrollRegion

	def setScrollRegion(self, x0, y0, x1, y1):
		cx0 = int(self._convertToPixelX(x0))
		cy0 = int(self._convertToPixelY(y0))
		cx1 = int(self._convertToPixelX(x1))
		cy1 = int(self._convertToPixelY(y1))
		dispatch = _EventDispatch()
		dispatch._set(self._edtSetScrollRegion, cx0, cy0, cx1, cy1)
		SwingUtilities.invokeAndWait(dispatch)

	def _edtSetScrollRegion(self, cx0, cy0, cx1, cy1):
		self._scrollRegion = (cx0, cy0, cx1, cy1)
		size = Dimension(cx1 - cx0, cy1 - cy0)

		self._getViewComponent().setPreferredSize(size)
		self._getViewComponent().revalidate()
		self._getFrame()._edtSetViewSize(size.width, size.height)

		imageBuffer, graphics = self._createGraphicsForImageBuffer()
		panel = self._getViewComponent()
		panel._setCurrentImageBuffer(imageBuffer)
		panel._setCurrentGraphics(graphics)

	def setViewWidth(self, viewWidth):
		frame = self._getFrame()
		scrollSize = frame._getScroll().getPreferredSize()
		width = int(self._convertToPixelX(viewWidth))
		height = scrollSize.height

		dispatch = _EventDispatch()
		dispatch._set(frame._edtSetViewSize, width, height)
		SwingUtilities.invokeLater(dispatch)

	def setViewHeight(self, viewHeight):
		frame = self._getFrame()
		scrollSize = frame._getScroll().getPreferredSize()
		width = scrollSize.width
		height = int(self._convertToPixelY(viewHeight))

		dispatch = _EventDispatch()
		dispatch._set(frame._edtSetViewSize, width, height)
		SwingUtilities.invokeLater(dispatch)

	def _setGraphics(self, graphics):
		self._getViewComponent()._setCurrentGraphics(graphics)

	def _getGraphics(self):
		return self._getViewComponent()._getCurrentGraphics()

	def _createGraphicsForImageBuffer(self):
		width = self.getScrollRegion()[2]
		height = self.getScrollRegion()[3]
		imageBuffer = BufferedImage(width, height, BufferedImage.TYPE_INT_BGR)
		graphics = imageBuffer.getGraphics()
		graphics.setBackground(Color.white)
		graphics.clearRect(0, 0, width, height)
		return imageBuffer, graphics

	def _convertToPixel(self, length):
		try:
			return float(length)
		except ValueError:
			if length.endswith('c'):
				return float(length[:-1]) / 2.54 * 72.0
			elif length.endswith('i'):
				return float(length[:-1]) * 72.0
			elif length.endswith('m'):
				return float(length[:-1]) / 25.4 * 72.0
			elif length.endswith('p'):
				return float(length[:-1]) / 72.27 * 72.0
			else:
				raise RuntimeError

	_convertToPixelX = _convertToPixel
	_convertToPixelY = _convertToPixel

	def _setPlotterCondition(self, condition):
		self._plotterCondition = condition

	def _getPlotterCondition(self):
		return self._plotterCondition

	def setImageIOCondition(self, condition):
		self._imageIOCondition = condition

	def getImageIOCondition(self):
		return self._imageIOCondition

	def getFormatNames(self):
		return list(ImageIO.getWriterFormatNames())

	def setImageWrite(self, fileName, landscape, fileType):
		imageBuffer = self._getViewComponent()._getCurrentImageBuffer()
		outputFile = file(fileName, 'wb')
		ImageIO.write(imageBuffer, fileType, outputFile)
		outputFile.close()

	def _doAndAddCommand(self, tags, command):
		dispatch = _EventDispatch()
		dispatch._set(self._edtDoAndAddCommand, tags, command)
		SwingUtilities.invokeAndWait(dispatch)

	def _edtDoAndAddCommand(self, tags, command):
		self._edtAddCommand(tags, command)
		command[0](*command[1], **command[2])
		self._setCommandModified(True)

	def _edtAddCommand(self, tags, command):
		self._getViewComponent()._addCommand(tags, command)

	def refresh(self):
		frame = self._getFrame()

		dispatch = _EventDispatch()
		dispatch._set(frame.validate)
		SwingUtilities.invokeAndWait(dispatch)

		dispatch = _EventDispatch()
		dispatch._set(frame.repaint)
		SwingUtilities.invokeAndWait(dispatch)

	def delete(self, tags):
		self._doAndAddCommand(tags, [self._edt_delete, [tags], {}])

	def create_styledText(self, textStyle, tags, x, y, textData, anchor):
		self._doAndAddCommand(tags, [self._edt_create_styledText, [textStyle, tags, x, y, textData, anchor], {}])

	def create_styledExponent(self, textStyle, tags, x, y, a, b, anchor, fontRatio, overOffsetRatio):
		self._doAndAddCommand(tags, [self._edt_create_styledExponent, [textStyle, tags, x, y, a, b, anchor, fontRatio, overOffsetRatio], {}])

	def create_styledOval(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		self._doAndAddCommand(tags, [self._edt_create_styledOval, [lineStyle, fillStyle, tags, x0, y0, x1, y1], {}])

	def create_styledRectangle(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		self._doAndAddCommand(tags, [self._edt_create_styledRectangle, [lineStyle, fillStyle, tags, x0, y0, x1, y1], {}])

	def create_styledLine(self, lineStyle, tags, *points):
		arg1 = [lineStyle, tags]
		arg1.extend(points)
		self._doAndAddCommand(tags, [self._edt_create_styledLine, arg1, {}])

	def create_styledPolygon(self, lineStyle, fillStyle, tags, x0, y0, x1, y1, x2, y2, x3, y3):
		self._doAndAddCommand(tags, [self._edt_create_styledPolygon, [lineStyle, fillStyle, tags, x0, y0, x1, y1, x2, y2, x3, y3], {}])

	def create_styledMarker(self, markerStyle, tags, x, y):
		self._doAndAddCommand(tags, [self._edt_create_styledMarker, [markerStyle, tags, x, y], {}])

	def create_styledTextsBox(self, infoStyle, region, layout, textsData, tags):
		self._doAndAddCommand(tags, [self._edt_create_styledTextsBox, [infoStyle, region, layout, textsData, tags], {}])

	def create_styledLegendsBox(self, infoStyle, region, layout, legends, tags):
		self._doAndAddCommand(tags, [self._edt_create_styledLegendsBox, [infoStyle, region, layout, legends, tags], {}])

	def create_styledStatisticsBox(self, infoStyle, region, layout, statisticsData, tags):
		self._doAndAddCommand(tags, [self._edt_create_styledStatisticsBox, [infoStyle, region, layout, statisticsData, tags], {}])

	def terminate(self):
		getRoot()._removePlotter(self)

		_Base._terminateBase(self)

		self._fontMeasurement = None
		self._legendsFont = None
		self._statisticsFont = None
		self._textsFont = None
		self._canvasFont = None
		self._canvasExponentBaseFont = None
		self._canvasExponentIndexFont = None

	def _edt_create_styledLegendsBox(self, infoStyle, region, layout, legends, tags):
		if self._getViewComponent()._existsTags(tags):
			self._edt_delete(tags)
			self._edtAddCommand(tags, [self._edt_create_styledLegendsBox, [infoStyle, region, layout, legends, tags], {}])

		textStyle = infoStyle.textStyle()
		rectangle, metrics = self._fontMeasure(textStyle, 'W')
		fontWidth = rectangle.getWidth()
		fontHeight = metrics.getHeight()
		fontHalf = metrics.getAscent() / 2.0

		longestDescription = 0
		for [style, description] in legends:
			rectangle, metrics = self._fontMeasure(textStyle, description)
			longestDescription = max(longestDescription, rectangle.getWidth())
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
		self._edt_create_styledRectangle(lineStyle, fillStyle, tags, boxX, boxY, boxX + boxWidth, boxY + boxHeight)
		for [style, description] in legends:
			style = style._createCopy()
			if isinstance(style, IFillStyle):
				originalColor = lineStyle.color()
				lineStyle.setColor(style.color())
				self._edt_create_styledRectangle(lineStyle, style, tags, styleX, lineY, styleX + fontWidth, lineY + fontHeight)
				lineStyle.setColor(originalColor)
			elif isinstance(style, ILineStyle):
				self._edt_create_styledLine(style, tags, styleX, lineY + fontHalf, styleX + fontWidth, lineY + fontHalf)
			elif isinstance(style, IMarkerStyle):
				originalSize = style._parameterData('size')
				style.setParameter('size', fontWidth)
				self._edt_create_styledMarker(style, tags, styleX + fontWidth / 2.0, lineY + fontHalf)
				style.setParameter('size', originalSize)
			else:
				raise RuntimeError, 'Unknown style in legends.'
			self._edt_create_styledText(textStyle, tags, descriptionX, lineY, description, NW)
			lineY += fontHeight + spacerY

	def _edt_create_styledStatisticsBox(self, infoStyle, region, layout, statisticsData, tags):
		if self._getViewComponent()._existsTags(tags):
			self._edt_delete(tags)
			self._edtAddCommand(tags, [self._edt_create_styledStatisticsBox, [infoStyle, region, layout, statisticsData, tags], {}])

		textStyle = infoStyle.textStyle()
		swingFont = self._configureSwingFont(self._statisticsFont, textStyle)
		rectangle, metrics = self._swingFontMeasure(swingFont, 'W')
		fontWidth = rectangle.getWidth()
		fontHeight = metrics.getHeight()

		longestName = 0
		longestData = 0
		for [name, data] in statisticsData:
			rectangle, metrics = self._swingFontMeasure(swingFont, name)
			longestName = max(longestName, rectangle.getWidth())
			rectangle, metrics = self._swingFontMeasure(swingFont, data)
			longestData = max(longestData, rectangle.getWidth())

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
		self._edt_create_styledRectangle(lineStyle, fillStyle, tags, boxX, boxY, boxX + boxWidth, boxY + boxHeight)
		for [name, data] in statisticsData:
			self._edt_create_styledText(textStyle, tags, nameX, lineY, name, NW)
			self._edt_create_styledText(textStyle, tags, dataX, lineY, data, NW)
			lineY += fontHeight + spacerY

	def _edt_create_styledTextsBox(self, infoStyle, region, layout, textsData, tags):
		if self._getViewComponent()._existsTags(tags):
			self._edt_delete(tags)
			self._edtAddCommand(tags, [self._edt_create_styledTextsBox, [infoStyle, region, layout, textsData, tags], {}])

		textStyle = infoStyle.textStyle()
		swingFont = self._configureSwingFont(self._statisticsFont, textStyle)
		rectangle, metrics = self._swingFontMeasure(swingFont, 'W')
		fontWidth = rectangle.getWidth()
		fontHeight = metrics.getHeight()

		longestData = 0
		for line in textsData:
			rectangle, metrics = self._swingFontMeasure(swingFont, line)
			longestData = max(longestData, rectangle.getWidth())

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
		self._edt_create_styledRectangle(lineStyle, fillStyle, tags, boxX, boxY, boxX + boxWidth, boxY + boxHeight)
		for line in textsData:
			self._edt_create_styledText(textStyle, tags, dataX, lineY, line, NW)
			lineY += fontHeight + spacerY

	def _getStroke(self, lineStyle):
		lineType = lineStyle.lineType()
		if lineType == 'solid':
			return BasicStroke(lineStyle.thickness())
		elif lineType == 'dot':
			return BasicStroke(lineStyle.thickness(), BasicStroke.CAP_BUTT, BasicStroke.JOIN_MITER, 2.0, [2.0, 4.0], 0.0)
		elif lineType == 'dash':
			return BasicStroke(lineStyle.thickness(), BasicStroke.CAP_BUTT, BasicStroke.JOIN_MITER, 2.0, [6.0, 2.0], 0.0)
		elif lineType == 'dash-dot':
			return BasicStroke(lineStyle.thickness(), BasicStroke.CAP_BUTT, BasicStroke.JOIN_MITER, 2.0, [6.0, 2.0, 4.0, 2.0], 0.0)
		elif lineType == 'dash-dot-dot':
			return BasicStroke(lineStyle.thickness(), BasicStroke.CAP_BUTT, BasicStroke.JOIN_MITER, 2.0, [6.0, 2.0, 4.0, 2.0, 4.0, 2.0], 0.0)
		else:
			raise RuntimeError, 'Unknown line type "%s".' % lineType

	def _getSwingColor(self, color):
		if color == '':
			return None
		elif color.startswith('#'):
			colorLength = len(color)
			if colorLength == 4:
				r = int(color[1], 16)
				g = int(color[2], 16)
				b = int(color[3], 16)
			elif colorLength == 7:
				r = int(color[1:3], 16)
				g = int(color[3:5], 16)
				b = int(color[5:7], 16)
			elif colorLength == 10:
				r = int(color[1:3], 16)
				g = int(color[4:6], 16)
				b = int(color[7:9], 16)
			elif colorLength == 13:
				r = int(color[1:3], 16)
				g = int(color[5:7], 16)
				b = int(color[9:11], 16)
			else:
				raise RuntimeError, 'Unknown color name "%s".' % color
			return Color(r, g, b)
		elif color == 'white':
			return Color.white
		elif color == 'black':
			return Color.black
		elif color == 'red':
			return Color.red
		elif color == 'green':
			return Color.green
		elif color == 'blue':
			return Color.blue
		elif color == 'cyan':
			return Color.cyan
		elif color == 'magenta':
			return Color.magenta
		elif color == 'yellow':
			return Color.yellow
		else:
			raise RuntimeError, 'Unknown color name "%s".' % color

	def _edt_delete(self, tags):
		panel = self._getViewComponent()
		graphics = self._getGraphics()
		panelSize = panel._size
		graphics.clearRect(0, 0, int(panelSize.getWidth()), int(panelSize.getHeight()))
		panel._removeCommands(tags)
		panel._edtRepaintAll(graphics)

	def _edt_create_styledOval(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		panel = self._getViewComponent()
		shape = Ellipse2D.Double(x0, y0, x1 - x0, y1 - y0)
		stroke = self._getStroke(lineStyle)
		colorFill = self._getSwingColor(fillStyle.color())
		colorLine = self._getSwingColor(lineStyle.color())

		graphics = self._getGraphics()
		graphics.setStroke(stroke)
		if colorFill:
			graphics.setPaint(colorFill)
			graphics.fill(shape)
		if colorLine:
			graphics.setPaint(colorLine)
			graphics.draw(shape)

	def _edt_create_styledRectangle(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		panel = self._getViewComponent()
		shape = Rectangle2D.Double(x0, y0, x1 - x0, y1 - y0)
		stroke = self._getStroke(lineStyle)
		colorFill = self._getSwingColor(fillStyle.color())
		colorLine = self._getSwingColor(lineStyle.color())

		graphics = self._getGraphics()
		graphics.setStroke(stroke)
		if colorFill:
			graphics.setPaint(colorFill)
			graphics.fill(shape)
		if colorLine:
			graphics.setPaint(colorLine)
			graphics.draw(shape)

	def _edt_create_styledLine(self, lineStyle, tags, *points):
		panel = self._getViewComponent()
		shape = GeneralPath(GeneralPath.WIND_EVEN_ODD)
		shape.moveTo(points[0], points[1])
		for i in range(2, len(points), 2):
			shape.lineTo(points[i], points[i + 1])
		stroke = self._getStroke(lineStyle)
		colorLine = self._getSwingColor(lineStyle.color())

		graphics = self._getGraphics()
		graphics.setStroke(stroke)
		if colorLine:
			graphics.setPaint(colorLine)
			graphics.draw(shape)

	def _edt_create_styledPolygon(self, lineStyle, fillStyle, tags, x0, y0, x1, y1, x2, y2, x3, y3):
		panel = self._getViewComponent()
		shape = GeneralPath(GeneralPath.WIND_EVEN_ODD)
		shape.moveTo(x0, y0)
		shape.lineTo(x1, y1)
		shape.lineTo(x2, y2)
		shape.lineTo(x3, y3)
		shape.closePath()
		stroke = self._getStroke(lineStyle)
		colorFill = self._getSwingColor(fillStyle.color())
		colorLine = self._getSwingColor(lineStyle.color())

		graphics = self._getGraphics()
		graphics.setStroke(stroke)
		if colorFill:
			graphics.setPaint(colorFill)
			graphics.fill(shape)
		if colorLine:
			graphics.setPaint(colorLine)
			graphics.draw(shape)

	def _edt_create_styledMarker(self, markerStyle, tags, x, y):
		panel = self._getViewComponent()
		marker = markerStyle.shape()
		markerSize = markerStyle._parameterData('size')
		markerSizeCanvasX = self._convertToPixelX(markerSize)
		markerSizeCanvasY = self._convertToPixelY(markerSize)

		lineStyle = ILineStyle()
		lineStyle.setColor(markerStyle.color())
		fillStyle = IFillStyle()
		fillStyle.setColor('')

		if marker == '':
			return
		elif marker == 'circle':
			x0 = x - markerSizeCanvasX / 2.0
			y0 = y - markerSizeCanvasY / 2.0
			x1 = x0 + markerSizeCanvasX
			y1 = y0 + markerSizeCanvasY
			self._edt_create_styledOval(lineStyle, fillStyle, tags, x0, y0, x1, y1)
		elif marker == 'square':
			x0 = x - markerSizeCanvasX / 2.0
			y0 = y - markerSizeCanvasY / 2.0
			self._edt_create_styledRectangle(lineStyle, fillStyle, tags, x0, y0, x0 + markerSizeCanvasX, y0 + markerSizeCanvasY)
		elif marker == 'diamond':
			x0 = x
			y0 = y - markerSizeCanvasY / 2.0
			x1 = x0 - markerSizeCanvasX / 2.0
			y1 = y
			x2 = x0
			y2 = y0 + markerSizeCanvasY
			x3 = x1 + markerSizeCanvasX
			y3 = y1
			self._edt_create_styledLine(lineStyle, tags, x0, y0, x1, y1, x2, y2, x3, y3, x0, y0)
		elif marker == 'triangle':
			sqrt3 = math.sqrt(3)
			x0 = x
			y0 = y - markerSizeCanvasY / sqrt3
			x1 = x0 - markerSizeCanvasX / 2.0
			y1 = y + markerSizeCanvasY / sqrt3 / 2.0
			x2 = x1 + markerSizeCanvasX
			y2 = y1
			self._edt_create_styledLine(lineStyle, tags, x0, y0, x1, y1, x2, y2, x0, y0)
		elif marker == 'cross':
			x0 = x - markerSizeCanvasX / 2.0
			y0 = y - markerSizeCanvasY / 2.0
			x1 = x0 + markerSizeCanvasX
			y1 = y0 + markerSizeCanvasY
			self._edt_create_styledLine(lineStyle, tags, x0, y0, x1, y1)
			self._edt_create_styledLine(lineStyle, tags, x0, y1, x1, y0)

	def _edt_create_styledText(self, textStyle, tags, x, y, textData, anchor):
		panel = self._getViewComponent()
		swingFont = self._createSwingFont(textStyle)
		colorText = self._getSwingColor(textStyle.color())

		rectangle, metrics = self._swingFontMeasure(swingFont, textData)
		if anchor == N:
			x0 = x - rectangle.getWidth() / 2.0
			y0 = y + metrics.getAscent()
		elif anchor == NE:
			x0 = x - rectangle.getWidth()
			y0 = y + metrics.getAscent()
		elif anchor == E:
			x0 = x - rectangle.getWidth()
			y0 = y + metrics.getAscent() / 2.0
		elif anchor == SE:
			x0 = x - rectangle.getWidth()
			y0 = y
		elif anchor == S:
			x0 = x - rectangle.getWidth() / 2.0
			y0 = y
		elif anchor == SW:
			x0 = x
			y0 = y
		elif anchor == W:
			x0 = x
			y0 = y + metrics.getAscent() / 2.0
		elif anchor == NW:
			x0 = x
			y0 = y + metrics.getAscent()
		else:
			raise RuntimeError, 'Unknown anchor "%s".' % anchor

		graphics = self._getGraphics()
		graphics.setFont(swingFont)
		if colorText:
			graphics.setPaint(colorText)
			graphics.drawString(textData, x0, y0)

	def _edt_create_styledExponent(self, textStyle, tags, x, y, a, b, anchor, fontRatio, overOffsetRatio):
		panel = self._getViewComponent()
		widthSpacer = 1
		indexTextStyle = textStyle._createCopy()
		indexTextStyle.setFontSize(textStyle.fontSize() * fontRatio)
		swingFontBase = self._configureSwingFont(self._canvasExponentBaseFont, textStyle)
		swingFontIndex = self._configureSwingFont(self._canvasExponentIndexFont, indexTextStyle)
		rectangle, metrics = self._swingFontMeasure(swingFontBase, a)
		widthBase = rectangle.getWidth()
		heightBase = metrics.getAscent() + metrics.getDescent()
		rectangle, metrics = self._swingFontMeasure(swingFontIndex, b)
		widthIndex = rectangle.getWidth()
		heightIndex = metrics.getAscent() + metrics.getDescent()
		widthAll = widthBase + widthIndex + widthSpacer
		heightAll = heightBase + heightIndex * overOffsetRatio
		heightCap = heightAll - heightBase
		textColor = textStyle.color()
		if anchor == N:
			xBase = x - widthAll / 2.0
			yBase = y + heightCap
		elif anchor == NE:
			xBase = x - widthAll
			yBase = y + heightCap
		elif anchor == E:
			xBase = x - widthAll
			yBase = y + heightAll / 2.0 - heightBase
		elif anchor == SE:
			xBase = x - widthAll
			yBase = y - heightBase
		elif anchor == S:
			xBase = x - widthAll / 2.0
			yBase = y - heightBase
		elif anchor == SW:
			xBase = x
			yBase = y - heightBase
		elif anchor == W:
			xBase = x
			yBase = y + heightAll / 2.0 - heightBase
		elif anchor == NW:
			xBase = x
			yBase = y + heightCap
		else:
			raise RuntimeException()
		xIndex = xBase + widthBase + widthSpacer
		yIndex = yBase - heightCap
		self._edt_create_styledText(textStyle, tags, xBase, yBase, a, NW)
		self._edt_create_styledText(indexTextStyle, tags, xIndex, yIndex, b, NW)
