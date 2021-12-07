from paida.paida_core.PAbsorber import *
import matplotlib.font_manager
import pylab

class _dummy_lock:
	def acquire(self):
		pass

	def release(self):
		pass

class _dummy_condition:
	def acquire(self):
		pass

	def notifyAll(self):
		pass

	def release(self):
		pass

	def wait(self):
		pass

N =  ('center', 'top')
NE = ('right', 'top')
E = ('right', 'center')
SE = ('right', 'bottom')
S = ('center', 'bottom')
SW = ('left', 'bottom')
W = ('left', 'center')
NW = ('left', 'top')
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
	fontProperties = matplotlib.font_manager.FontProperties()
	fontList = fontProperties.get_family()
	return fontList, fontList[-1]


class _Root:
	def __init__(self):
		self._setLock(_dummy_lock())
		self._setRootCondition(_dummy_condition())
		self._setQuitLoop(False)

	def start(self):
		rootCondition = self._getRootCondition()
		rootCondition.acquire()
		rootCondition.notifyAll()
		rootCondition.release()

	def _setLock(self, lock):
		self._rootLock = lock

	def _getLock(self):
		return self._rootLock

	def _setRootCondition(self, Condition):
		self._rootCondition = Condition

	def _getRootCondition(self):
		return self._rootCondition

	def _setQuitLoop(self, boolean):
		self._quitLoop = boolean

	def _getQuitLoop(self):
		return self._quitLoop

	def _requestTree(self):
		return _Tree()

	def _requestPlotter(self, viewWidth, viewHeight, width, height):
		return _Plotter(viewWidth, viewHeight, width, height)

class _Base:
	def __init__(self):
		pass

	def setTitle(self, title):
		pass

class _Tree(_Base):
	def __init__(self):
		_Base.__init__(self)

	def redrawTree(self, block, itree):
		pass

class _Plotter(_Base):
	def __init__(self, viewWidth, viewHeight, width, height):
		_Base.__init__(self)
		### self._sizes is original values. (may be strings)
		### self._sizes2 is converted to float values.
		self._sizes = (viewWidth, viewHeight, width, height)
		self._sizes2 = (self._convertToPixel(viewWidth),
				self._convertToPixel(viewHeight),
				self._convertToPixel(width),
				self._convertToPixel(height))
		self._figureHander = pylab.figure(facecolor = 'white')
		self._figureNumber = self._figureHander.number
		self._axes = {}

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

	def setTitle(self, title):
		pass

	def getScrollRegion(self):
		return self._sizes2

	def _createFontDict(self, textStyle):
		if textStyle.isItalic():
			style = 'italic'
		else:
			style = 'normal'
		if textStyle.isBold():
			weight = matplotlib.font_manager.weight_dict['bold']
		else:
			weight = matplotlib.font_manager.weight_dict['normal']
		return {'family': textStyle.font(), 
			    'style':  style,
			    'weight': weight,
			    'size':   textStyle.fontSize()}

	def _createFontProperty(self, textStyle):
		if textStyle.isItalic():
			style = 'italic'
		else:
			style = 'normal'
		if textStyle.isBold():
			weight = matplotlib.font_manager.weight_dict['bold']
		else:
			weight = matplotlib.font_manager.weight_dict['normal']
		return matplotlib.font_manager.FontProperties(family = textStyle.font(),
							      style = style,
							      weight = weight,
							      size = textStyle.fontSize())

	def create_styledText(self, textStyle, tags, x, y, textData, anchor):
		pylab.figure(self._figureNumber)
		x /= self._sizes2[2]
		y /= self._sizes2[3]
		pylab.figtext(x, 1.0 - y, textData,
			      fontdict = self._createFontDict(textStyle),
			      color = textStyle.color(),
			      horizontalalignment = anchor[0],
			      verticalalignment = anchor[1])

	def create_styledRectangle(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		pass

	def _requestRegion(self, serialNumber, allTags, x0, y0, x1, y1):
		pass

	def _getFontMeasurements(self, textDataList, bridge):
		result = []
		renderer = self._figureHander.canvas.get_renderer()
		for textStyle, text in textDataList:
			fontProperty = self._createFontProperty(textStyle)
			result.append(renderer.get_text_width_height(text, fontProperty, False))
		bridge.append(result)

	def getAxes(self, serialNumber):
		return self._axes[serialNumber]

	def createAxes(self, serialNumber, tagsAxes, x0, y0, x1, y1):
		x0 /= self._sizes2[2]
		y0 /= self._sizes2[3]
		x1 /= self._sizes2[2]
		y1 /= self._sizes2[3]
		self._axes[serialNumber] = pylab.axes([x0, 1.0 - y1, x1 - x0, y1 - y0])

	def delete(self, serialNumber):
		self._axes[serialNumber].clear()
