from paida.paida_core.PAbsorber import *
from paida.paida_core.IFillStyle import *
from paida.paida_core.ILineStyle import *
from paida.paida_core.ITextStyle import *

try:
	import threading
except ImportError:
	import dummy_threading as threading
import time

N = None
NE = None
E = None
SE = None
S = None
SW = None
W = None
NW = None
CENTER = None

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
	return [''], ''

class _Root(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._setRootCondition(threading.Condition())

	def run(self):
		rootCondition = self._getRootCondition()
		rootCondition.acquire()
		self._setRoot(None)

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

	def _mainloop(self):
		lock = self._getLock()
		while 1:
			if self._getQuitLoop() == True:
				rootCondition = self._getRootCondition()
				rootCondition.acquire()
				### Wait other threads.
				lock.acquire()
				lock.release()
				rootCondition.notifyAll()
				rootCondition.release()
				break
			else:
				if lock.acquire(blocking = 0):
					self._check()
					lock.release()
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
			self._requestedTrees = []
			treeCondition.notifyAll()
			treeCondition.release()

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
			self._requestedPlotters = []
			plotterCondition.notifyAll()
			plotterCondition.release()

		for plotter in self._getPlotters():
			plotter.update()

class _Base:
	def __init__(self, lock):
		self._canvasCommands = []
		self.setLock(lock)

		### Create widges.
		self.setRoot(None)
		self.setFrame(None)
		self.setCanvas(None)

		self._setFontCondition(threading.Condition())

		self.setShow(True)
		self.setTitle('')

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
		pass

	def canvas_yscroll(self, *args1):
		pass

	def canvas_xview(self, *args1):
		pass

	def canvas_yview(self, *args1):
		pass

	def canvas_title(self, title):
		self._title = title

	def canvas_show(self, boolean):
		self._show = boolean

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
		result = []
		for textStyle, text in textDataList:
			result.append([1, 1])
		bridge.append(result)

	def update(self):
		self.getLock().acquire()
		for [method, args1, args2] in self._canvasCommands:
			method(*args1, **args2)
		else:
			self._canvasCommands = []
		self.getLock().release()

class _Tree(_Base):
	def __init__(self, lock):
		_Base.__init__(self, lock)

	def setTree(self, tree):
		self._tree = tree

	def getTree(self):
		return self._tree

	def terminate(self):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_terminate, [], {}])
		self.getLock().release()

	def canvas_terminate(self):
		getRoot()._removeTree(self)
		self.setTree(None)
		self.setCanvas(None)
		self.setFrame(None)
		self.setRoot(None)

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
		pass

class _Plotter(_Base):
	def __init__(self, lock, viewWidth, viewHeight, width, height):
		_Base.__init__(self, lock)
		self.setPostscriptCondition(threading.Condition())

		self.setScrollRegion(0, 0, 100, 100)

	def _requestRegion(self, serialNumber, allTags, x0, y0, x1, y1):
		### Nothing to do for batch GUI.
		pass

	def setPostscriptCondition(self, condition):
		self._postscriptCondition = condition

	def getPostscriptCondition(self):
		return self._postscriptCondition

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

	def create_text(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.getCanvas().create_text, args1, args2])
		self.getLock().release()

	def create_oval(self, *args1, **args2):
		self.getLock().acquire()
		self._canvasCommands.append([self.getCanvas().create_oval, args1, args2])
		self.getLock().release()

	def create_rectangle(self, *args1, **args2):
		pass

	def create_line(self, *args1, **args2):
		pass

	def create_polygon(self, *args1, **args2):
		pass

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

	def setPostscript(self, fileName):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_postscript, [fileName], {}])
		self.getLock().release()

	def setPostscriptStrings(self):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_postscriptStrings, [], {}])
		self.getLock().release()

	def getPostscriptStrings(self):
		return self._postscriptStrings

	def terminate(self):
		self.getLock().acquire()
		self._canvasCommands.append([self.canvas_terminate, [], {}])
		self.getLock().release()

	def canvas_terminate(self):
		getRoot()._removePlotter(self)
		self.setPlotter(None)
		self.setCanvas(None)
		self.setFrame(None)
		self.setRoot(None)

	def canvas_scrollRegion(self, x0, y0, x1, y1):
		self._scrollRegion = (0, 0, 100, 100)

	def canvas_viewWidth(self, viewWidth):
		self._viewWidth = 1

	def canvas_viewHeight(self, viewHeight):
		self._viewHeight = 1

	def canvas_create_styledLegendsBox(self, infoStyle, region, layout, legends, tags):
		pass

	def canvas_create_styledStatisticsBox(self, infoStyle, region, layout, statisticsData, tags):
		pass

	def canvas_create_styledTextsBox(self, infoStyle, region, layout, textsData, tags):
		pass

	def canvas_postscript(self, fileName):
		postscriptCondition = self.getPostscriptCondition()
		postscriptCondition.acquire()
		postscriptCondition.notifyAll()
		postscriptCondition.release()

	def canvas_postscriptStrings(self):
		postscriptCondition = self.getPostscriptCondition()
		postscriptCondition.acquire()
		self._postscriptStrings = ''
		postscriptCondition.notifyAll()
		postscriptCondition.release()

	def canvas_create_styledOval(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		pass

	def canvas_create_styledRectangle(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		pass

	def canvas_create_styledLine(self, lineStyle, tags, *points):
		pass

	def canvas_create_styledPolygon(self, lineStyle, fillStyle, tags, *points):
		pass

	def canvas_create_styledMarker(self, markerStyle, tags, x, y):
		pass

	def canvas_create_styledText(self, textStyle, tags, x, y, textData, anchor):
		pass

	def canvas_delete(self, *args1):
		pass

	def canvas_create_styledExponent(self, textStyle, tags, x, y, a, b, anchor, fontRatio, overOffsetRatio):
		pass
