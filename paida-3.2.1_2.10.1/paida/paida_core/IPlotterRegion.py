from paida.paida_core.PAbsorber import *
from paida.paida_core.IHistogram1D import *
from paida.paida_core.IHistogram2D import *
from paida.paida_core.IHistogram3D import *
from paida.paida_core.ICloud1D import *
from paida.paida_core.ICloud2D import *
from paida.paida_core.ICloud3D import *
from paida.paida_core.IProfile1D import *
from paida.paida_core.IProfile2D import *
from paida.paida_core.IFunction import *
from paida.paida_core.IDataPointSet import *
from paida.paida_core.PExceptions import *
from paida.paida_core.PUtilities import *
from paida.paida_core.IPlotterStyle import *
from paida.paida_core.IAxis import *
from paida.paida_core.IRangeSet import *
from paida.paida_core.IFillStyle import *
from paida.paida_core.IInfo import *
from paida.paida_core.ILineStyle import *
from paida.paida_core.IMarkerStyle import *
from paida.paida_core.IPlotterLayout import *
from paida.paida_core.ITextStyle import *
from paida.math.array.matrix import matrix
import paida.paida_gui.PRoot as PRoot

import types
import math
from math import sqrt, fabs, pi, sin, cos, tan, floor
import time

try:
	time.mktime((2004, 13, 1, 1, 0, 0, 0, 0, 0))
	_mktime = time.mktime
except OverflowError:
	### For Jython2.1's time module.
	import java.util.Date
	def _mktime(timeTuple):
		_date = java.util.Date(timeTuple[0], timeTuple[1], timeTuple[2], timeTuple[3], timeTuple[4], timeTuple[5])
		return time.mktime((_date.getYear(), _date.getMonth(), _date.getDate(), _date.getHours(), _date.getMinutes(), _date.getSeconds(), 0, 0, 0))

N = PRoot.N
NE = PRoot.NE
E = PRoot.E
SE = PRoot.SE
S = PRoot.S
SW = PRoot.SW
W = PRoot.W
NW = PRoot.NW
CENTER = PRoot.CENTER

def log10(data):
	### Java1.4 doesn't calculate log10() correctly (log(x)/log(10))
	if 1000.0 <= data < 1000.0000000000002:
		return 3.0
	else:
		return math.log10(data)

class IPlotterRegion:
	def __init__(self, guiPlotter, serialNumber, x0, y0, x1, y1):
		### Check if the GUI engine is 'matplotlib'.
		import paida.paida_gui.PGuiSelector as PGuiSelector
		if PGuiSelector.getGuiEngineName() == 'matplotlib':
			self._isMatplotlib = True
		else:
			self._isMatplotlib = False

		self._parameters = {}
		self._setGuiPlotter(guiPlotter)
		self._setPrefix('%s' % serialNumber)
		self._serialNumber = serialNumber
		self._x0 = x0
		self._y0 = y0
		self._x1 = x1
		self._y1 = y1

		tagSeeds = ['regionBox', 'axes', 'plot', 'title', '_statisticsBox', '_legendsBox', '_textsBox']
		allTags = []
		for tagSeed in tagSeeds:
			allTags.append(self._createTags([tagSeed]))
		guiPlotter._requestRegion(serialNumber, allTags, x0, y0, x1, y1)

		self._initializeValues()

		### Just initialization. There is no meaning on [-10.0, 10.0].
		self._setAxisValueRangeX(-10.0, 10.0)
		self._setAxisValueRangeY(-10.0, 10.0)
		self._setAxisValueRangeZ(-10.0, 10.0)

		self.setXLimits()
		self.setYLimits()
		self.setZLimits()

		self._setUnderRescaling(False)
		self._setFinalRescaling(False)

		self._setCreateAxisBox(False)

		self._plotterStyle = IPlotterStyle()
		self._plotterLayout = IPlotterLayout()
		self._plotterInfo = IInfo(self)

		self.setTitle('')
		self._titleShown = False

		self._clearItemData()
		self._createRegionBox()

	def _initializeValues(self):
		canvasWidth = self._getCanvasWidth()
		canvasHeight = self._getCanvasHeight()
		self._regionX0 = int(canvasWidth * self._x0)
		self._regionY0 = int(canvasHeight * self._y0)
		self._regionX1 = max(int(canvasWidth * self._x1), 1)
		self._regionY1 = max(int(canvasHeight * self._y1), 1)
		self._regionWidth = self._regionX1 - self._regionX0
		self._regionHeight = self._regionY1 - self._regionY0

		self._axesMarginX0 = int(self._regionWidth * 0.22)
		self._axesMarginX1 = int(self._regionWidth * 0.11)
		self._axesMarginY0 = int(self._regionHeight * 0.15)
		self._axesMarginY1 = int(self._regionHeight * 0.20)
		self._axesX0 = self._regionX0 + self._axesMarginX0
		self._axesY0 = self._regionY0 + self._axesMarginY0
		self._axesX1 = self._regionX1 - self._axesMarginX1
		self._axesY1 = self._regionY1 - self._axesMarginY1
		self._axesWidth = self._axesX1 - self._axesX0
		self._axesHeight = self._axesY1 - self._axesY0

	def _setGuiPlotter(self, guiPlotter):
		self._guiPlotter = guiPlotter

	def _getGuiPlotter(self):
		return self._guiPlotter

	def _setPrefix(self, prefix):
		self._prefix = prefix

	def _getPrefix(self):
		return self._prefix

	def _createTags(self, tags):
		prefix = self._getPrefix()
		result = []
		for tag in tags:
			result.append(prefix + tag)
		try:
			if not result in self._taglist:
				self._taglist.append(result)
		except:
			self._taglist = [result]
		return result

	def _getCanvasHeight(self):
		return self._getGuiPlotter().getScrollRegion()[3]

	def _getCanvasWidth(self):
		return self._getGuiPlotter().getScrollRegion()[2]

	def _getRegionLengthX(self):
		return self._regionWidth

	def _getRegionRangeX(self):
		return self._regionX0, self._regionX1

	def _getRegionLengthY(self):
		return self._regionHeight

	def _getRegionRangeY(self):
		return self._regionY0, self._regionY1

	def _getAxisRangeX(self):
		return self._axesX0, self._axesX1

	def _getAxisRangeY(self):
		return self._axesY0, self._axesY1

	def _getAxisValueRangeX(self):
		return self._axisValueX0, self._axisValueX1

	def _setAxisValueRangeX(self, axisValueX0, axisValueX1):
		self._axisValueX0 = axisValueX0
		self._axisValueX1 = axisValueX1

	def _getAxisValueRangeY(self):
		return self._axisValueY0, self._axisValueY1

	def _setAxisValueRangeY(self, axisValueY0, axisValueY1):
		self._axisValueY0 = axisValueY0
		self._axisValueY1 = axisValueY1

	def _getAxisValueRangeZ(self):
		return self._axisValueZ0, self._axisValueZ1

	def _setAxisValueRangeZ(self, axisValueZ0, axisValueZ1):
		self._axisValueZ0 = axisValueZ0
		self._axisValueZ1 = axisValueZ1

	def _getTickSettingsX(self):
		return self._tickSettingsX

	def _setTickSettingsX(self, tickLowerX, tickUpperX, mainTicksX, subTicksX):
		self._tickSettingsX = (tickLowerX, tickUpperX, mainTicksX, subTicksX)

	def _getTickSettingsY(self):
		return self._tickSettingsY

	def _setTickSettingsY(self, tickLowerY, tickUpperY, mainTicksY, subTicksY):
		self._tickSettingsY = (tickLowerY, tickUpperY, mainTicksY, subTicksY)

	def _getTickSettingsZ(self):
		return self._tickSettingsZ

	def _setTickSettingsZ(self, tickLowerZ, tickUpperZ, mainTicksZ, subTicksZ):
		self._tickSettingsZ = (tickLowerZ, tickUpperZ, mainTicksZ, subTicksZ)

	def _getScalingX(self):
		return self._scalingX

	def _setScalingX(self, scaling):
		self._scalingX = scaling

	def _getScalingY(self):
		return self._scalingY

	def _setScalingY(self, scaling):
		self._scalingY = scaling

	def _getScalingZ(self):
		return self._scalingZ

	def _setScalingZ(self, scaling):
		self._scalingZ = scaling

	def _setItemData(self, item, plotterStyle, options):
		if item in self._items:
			self._items.remove(item)
		self._items.append(item)
		self._itemsData[item] = [plotterStyle, options]

	def _removeItemData(self, item):
		del self._itemsData[item]
		self._items.remove(item)

	def _getItemData(self, item):
		return self._itemsData[item]

	def _getItemDataKeys(self):
		return self._items

	def _getNItemData(self):
		return len(self._items)

	def _clearItemData(self):
		self._items = []
		self._itemsData = {}

	def _setUnderRescaling(self, boolean):
		self._underRescaling = boolean

	def _getUnderRescaling(self):
		return self._underRescaling

	def _setFinalRescaling(self, boolean):
		self._finalRescaling = boolean

	def _getFinalRescaling(self):
		return self._finalRescaling

	def _refresh(self, rescale = False):
		itemsData = self._itemsData.copy()
		items = self._getItemDataKeys()
		self._refreshClear()
		self._createRegionBox()
		if rescale:
			self._setUnderRescaling(True)
			if self.info()._getLegendVeto():
				flagEntireVeto = True
			else:
				flagEntireVeto = False
				self.info()._setLegendVeto(True)
			lowerXList = []
			upperXList = []
			lowerYList = []
			upperYList = []
			lowerZList = []
			upperZList = []
			for item in items:
				[plotterStyle, options] = itemsData[item]
				self._plot(item, plotterStyle, options)
				lowerX0, upperX0 = self._getAxisValueRangeX()
				lowerY0, upperY0 = self._getAxisValueRangeY()
				lowerZ0, upperZ0 = self._getAxisValueRangeZ()
				lowerXList.append(lowerX0)
				upperXList.append(upperX0)
				lowerYList.append(lowerY0)
				upperYList.append(upperY0)
				lowerZList.append(lowerZ0)
				upperZList.append(upperZ0)
			self._setAxisValueRangeX(min(lowerXList), max(upperXList))
			self._setAxisValueRangeY(min(lowerYList), max(upperYList))
			self._setAxisValueRangeZ(min(lowerZList), max(upperZList))
			self._setUnderRescaling(False)
			self._setFinalRescaling(True)
			self._setCreateAxisBox(True)
			self._clearItemData()
			for item in items:
				if (item == items[-1]) and (not flagEntireVeto):
					self.info()._setLegendVeto(False)
				[plotterStyle, options] = itemsData[item]
				self._plot(item, plotterStyle, options)
			self._setFinalRescaling(False)
		else:
			for item in items:
				[plotterStyle, options] = itemsData[item]
				self._plot(item, plotterStyle, options)

	def _convertRatioToColor(self, ratio):
		#  Original (and more flexible) C source code from:
		#  http://astronomy.swin.edu.au/~pbourke/colour/colourramp/
		#
		#    Return a RGB colour value given a scalar ratio in the range [0,1]

		#  Python version by apfeiffer. Thanks!

		# (r,g,b) here: white
		color = [1.0, 1.0, 1.0]

		if (ratio < 0.0):
			ratio = 0.0
		elif (ratio > 1.0):
			ratio = 1.0

		if (ratio < 0.25):
			color[0] = 0.0
			color[1] = 4.0 * ratio
		elif (ratio < 0.5):
			color[0] = 0.0
			color[2] = 1.0 + 4.0 * (0.25 - ratio)
		elif (ratio < 0.75):
			color[0] = 4.0 * (ratio - 0.5)
			color[2] = 0.0
		else :
			color[1] = 1.0 + 4.0 * (0.75 - ratio)
			color[2] = 0

		# now map to RGB values (0...255) and return
		scale = 255
		c = (color[0]*scale, color[1]*scale, color[2]*scale)

		return '#%02X%02X%02X' % c

	def _3DConvertToRatio(self, scaling, lower, upper, value):
		if scaling in ['lin', 'linear']:
			return (value - lower) / (upper - lower)
		elif scaling in ['log', 'logarithmic']:
			return log10(value / lower) / log10(upper / lower)
		else:
			raise RuntimeException()

	def _3DConvertToTickRatio(self, lower, upper, value):
		return (value - lower) / (upper - lower)

	def _3DConvertToCanvas(self, p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioX, ratioY, ratioZ):
		return p0x + ratioX * cXx + ratioY * cYx + ratioZ * cZx, p0y - ratioX * cXy - ratioY * cYy - ratioZ * cZy

	def _convertRatioToCanvas(self, p0x, p0y, p1x, p1y, ratio):
		return ratio * p1x + (1.0 - ratio) * p0x, ratio * p1y + (1.0 - ratio) * p0y

	def _convertToCanvasX(self, lower, upper, x):
		return self._axesWidth / (upper - lower) * (x - lower) + self._axesX0

	def _convertToCanvasLogX(self, lower, upper, x):
		if x in [IRangeSet._NINF, IRangeSet._PINF]:
			return x
		elif x <= 0:
			return IRangeSet._NINF
		else:
			return self._axesWidth / log10(upper / lower) * log10(x / lower) + self._axesX0

	def _convertToCanvasY(self, lower, upper, y):
		return self._axesY1 - self._axesHeight / (upper - lower) * (y - lower)

	def _convertToCanvasLogY(self, lower, upper, y):
		if y == IRangeSet._NINF:
			return IRangeSet._PINF
		elif y == IRangeSet._PINF:
			return IRangeSet._NINF
		elif y <= 0:
			return IRangeSet._PINF
		else:
			return self._axesY1 - self._axesHeight / log10(upper / lower) * log10(y / lower)

	def _getConvertersToCanvas(self):
		scalingX = self._getScalingX()
		scalingY = self._getScalingY()
		if scalingX in ['lin', 'linear']:
			convertX = self._convertToCanvasX
		elif scalingX in ['log', 'logarithmic']:
			convertX = self._convertToCanvasLogX
		else:
			raise RuntimeException()
		if scalingY in ['lin', 'linear']:
			convertY = self._convertToCanvasY
		elif scalingY in ['log', 'logarithmic']:
			convertY = self._convertToCanvasLogY
		else:
			raise RuntimeException()
		return convertX, convertY

	def _create_styledText(self, textStyle, tags, x, y, textData, anchor):
		self._getGuiPlotter().create_styledText(textStyle, tags, x, y, textData, anchor)

	def _create_styledExponent(self, textStyle, tags, x, y, a, b, anchor, fontRatio, overOffsetRatio):
		self._getGuiPlotter().create_styledExponent(textStyle, tags, x, y, a, b, anchor, fontRatio, overOffsetRatio)

	def _create_styledOval(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		self._getGuiPlotter().create_styledOval(lineStyle, fillStyle, tags, x0, y0, x1, y1)

	def _create_styledRectangle(self, lineStyle, fillStyle, tags, x0, y0, x1, y1):
		self._getGuiPlotter().create_styledRectangle(lineStyle, fillStyle, tags, x0, y0, x1, y1)

	def _create_styledLine(self, lineStyle, tags, *points):
		self._getGuiPlotter().create_styledLine(lineStyle, tags, *points)

	def _create_styledPolygon(self, lineStyle, fillStyle, tags, *points):
		self._getGuiPlotter().create_styledPolygon(lineStyle, fillStyle, tags, *points)

	def _create_styledRectangleInBox(self, lineStyle, fillStyle, tags, x0, y0, x1, y1, p0x, p0y, p1x, p1y):
		if (p0x > x1) or (p1x < x0) or (p0y > y1) or (p1y < y0):
			return
		else:
			p0x = max(p0x, x0)
			p0y = max(p0y, y0)
			p1x = min(p1x, x1)
			p1y = min(p1y, y1)
			self._create_styledRectangle(lineStyle, fillStyle, tags, p0x, p0y, p1x, p1y)

	def _create_styledLineInBox(self, lineStyle, tags, x0, y0, x1, y1, *points):
		for i in range(0, len(points) - 2, 2):
			p0x, p0y, p1x, p1y = points[i:i + 4]
			if p0x == p1x:
				if x0 <= p0x <= x1:
					if p0y > p1y:
						p0y, p1y = p1y, p0y
					if (p0y <= y1) and (y0 <= p1y):
						p0y = max(p0y, y0)
						p1y = min(p1y, y1)
					else:
						### Exclude.
						continue
				else:
					### Exclude.
					continue
			elif p0y == p1y:
				if y0 <= p0y <= y1:
					if p0x > p1x:
						p0x, p1x = p1x, p0x
					if (p0x <= x1) and (x0 <= p1x):
						p0x = max(p0x, x0)
						p1x = min(p1x, x1)
					else:
						### Exclude.
						continue
				else:
					### Exclude.
					continue
			else:
				raise RuntimeException()
			self._create_styledLine(lineStyle, tags, p0x, p0y, p1x, p1y)

	def _create_styledMarker(self, markerStyle, tags, x, y):
		self._getGuiPlotter().create_styledMarker(markerStyle, tags, x, y)

	def _bestRange(self, axis, axisStyle):
		scaling = axisStyle._parameterData('scale')

		if scaling in ['lin', 'linear']:
			### Linear scaling.
			rangeMin = axis.lowerEdge()
			rangeMax = axis.upperEdge()

		elif scaling in ['log', 'logarithmic']:
			### Log scaling.
			rangeMin = axis.lowerEdge()
			if rangeMin <= 0.0:
				for binNumber in range(axis.bins()):
					rangeMin = axis.binLowerEdge(binNumber)
					if rangeMin > 0.0:
						break
				else:
					upperEdge = axis.upperEdge()
					if upperEdge <= 0.0:
						rangeMin = 1.0
					else:
						rangeMin = upperEdge / 2.0
			rangeMax = axis.upperEdge()
			if rangeMax <= 0.0:
				rangeMax = 2.0

		else:
			### Unknown scaling.
			raise IllegalArgumentException('Unknown scaling "%s".' % (scaling))

		return rangeMin, rangeMax

	def _bestHeightRange(self, axes, axisStyle, dataStyle, item):
		scaling = axisStyle._parameterData('scale')
		countError = dataStyle._parameterData('showErrorBars')
		dimension = len(axes)
		if dimension == 1:
			axisX = axes[0]
		elif dimension == 2:
			axisX = axes[0]
			axisY = axes[1]

		if scaling in ['lin', 'linear']:
			### Linear scaling.
			rangeMin = item.minBinHeight()
			if rangeMin > 0.0:
				rangeMin = 0.0
			rangeMax = item.maxBinHeight()
			if rangeMax >= 0.0:
				if rangeMax >= 1.0:
					if countError == True:
						rangeMax += 2.0 * sqrt(rangeMax)
					else:
						rangeMax += sqrt(rangeMax)
				else:
					### 0.0 <= rangeMax < 1.0
					if countError == True:
						rangeMax += 1.2 * sqrt(rangeMax)
					else:
						rangeMax += 0.1 * rangeMax
			else:
				rangeMax = min(0.0, rangeMax + 0.1 * fabs(rangeMax))

		elif scaling in ['log', 'logarithmic']:
			### Log scaling.
			rangeMin = item.minBinHeight()
			if rangeMin <= 0.0:
				rangeMin = item.maxBinHeight()
				if rangeMin <= 0.0:
					rangeMin = 1.0
				else:
					if dimension == 1:
						nBinsX = axisX.bins()
						for binNumberX in range(nBinsX):
							tempMin = item.binHeight(binNumberX)
							if tempMin > 0.0:
								if countError == True:
									tempMin2 = tempMin - sqrt(tempMin)
									if tempMin2 <= 0.0:
										rangeMin = min(rangeMin, tempMin)
									else:
										rangeMin = min(rangeMin, tempMin2)
								else:
									rangeMin = min(rangeMin, tempMin)
					elif dimension == 2:
						nBinsX = axisX.bins()
						nBinsY = axisY.bins()
						for binNumberX in range(nBinsX):
							for binNumberY in range(nBinsY):
								tempMin = item.binHeight(binNumberX, binNumberY)
								if tempMin > 0.0:
									if countError == True:
										tempMin2 = tempMin - sqrt(tempMin)
										if tempMin2 <= 0.0:
											rangeMin = min(rangeMin, tempMin)
										else:
											rangeMin = min(rangeMin, tempMin2)
									else:
										rangeMin = min(rangeMin, tempMin)
			rangeMin *= 0.9
			rangeMax = item.maxBinHeight()
			if rangeMax <= 0.0:
				rangeMax = 10.0
			if countError == True:
				rangeMax = 10**(log10(rangeMax + sqrt(rangeMax)) + 0.1 * fabs(log10(rangeMax) + sqrt(rangeMax)))
			else:
				rangeMax = 10**(log10(rangeMax) + 0.1 * fabs(log10(rangeMax)))

		else:
			### Unknown scaling.
			raise IllegalArgumentException('Unknown scaling "%s".' % (scaling))

		return rangeMin, rangeMax

	def plot(self, data1, data2 = None, data3 = None):
		if (isinstance(data1, IHistogram1D)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, IHistogram1D)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, IHistogram1D)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, IHistogram1D)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		elif (isinstance(data1, IHistogram2D)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, IHistogram2D)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, IHistogram2D)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, IHistogram2D)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		elif (isinstance(data1, IHistogram3D)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, IHistogram3D)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, IHistogram3D)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, IHistogram3D)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		elif (isinstance(data1, ICloud1D)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, ICloud1D)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, ICloud1D)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, ICloud1D)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		elif (isinstance(data1, ICloud2D)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, ICloud2D)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, ICloud2D)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, ICloud2D)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		elif (isinstance(data1, ICloud3D)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, ICloud3D)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, ICloud3D)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, ICloud3D)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		elif (isinstance(data1, IProfile1D)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, IProfile1D)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, IProfile1D)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, IProfile1D)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		elif (isinstance(data1, IProfile2D)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, IProfile2D)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, IProfile2D)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, IProfile2D)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		elif (isinstance(data1, IFunction)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, IFunction)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, IFunction)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, IFunction)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		elif (isinstance(data1, IDataPointSet)) and (data2 == None) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(None)
		elif (isinstance(data1, IDataPointSet)) and (isinstance(data2, IPlotterStyle)) and (data3 == None):
			plotterStyle = data2
			options = optionAnalyzer(None)
		elif (isinstance(data1, IDataPointSet)) and (type(data2) in types.StringTypes) and (data3 == None):
			plotterStyle = self.style()
			options = optionAnalyzer(data2)
		elif (isinstance(data1, IDataPointSet)) and (isinstance(data2, IPlotterStyle)) and (type(data3) in types.StringTypes):
			plotterStyle = data2
			options = optionAnalyzer(data3)

		else:
			raise IllegalArgumentException('Invalid arguments.')

		if self._needReplace(options):
			self.clear()
		self._plot(data1, plotterStyle, options)

	def _plot(self, data, plotterStyle, options):
		newPlotterStyle = plotterStyle._createCopy()
		self._setItemData(data, newPlotterStyle, options)
		if isinstance(data, IHistogram1D):
			plotFunction = self._plotHistogram1D
		elif isinstance(data, IHistogram2D):
			plotFunction = self._plotHistogram2D
		elif isinstance(data, IHistogram3D):
			plotFunction = self._plotHistogram3D
		elif isinstance(data, ICloud1D):
			plotFunction = self._plotCloud1D
		elif isinstance(data, ICloud2D):
			plotFunction = self._plotCloud2D
		elif isinstance(data, ICloud3D):
			plotFunction = self._plotCloud3D
		elif isinstance(data, IProfile1D):
			plotFunction = self._plotProfile1D
		elif isinstance(data, IProfile2D):
			plotFunction = self._plotProfile2D
		elif isinstance(data, IFunction):
			dimension = data.dimension()
			if dimension == 1:
				plotFunction = self._plotFunction1D
			elif dimension == 2:
				plotFunction = self._plotFunction2D
			else:
				raise IllegalArgumentException("Function's dimension is over the system limitation.")
		elif isinstance(data, IDataPointSet):
			dimension = data.dimension()
			if dimension == 1:
				plotFunction = self._plotDataPointSet1D
			elif dimension == 2:
				plotFunction = self._plotDataPointSet2D
			elif dimension == 3:
				plotFunction = self._plotDataPointSet3D
			else:
				raise IllegalArgumentException("DataPointSet's dimension is over the system limitation.")
		else:
			raise IllegalArgumentException('Unsupported object for plotting.')

		if self._getUnderRescaling():
			plotFunction(data, newPlotterStyle, options)
		elif self._getFinalRescaling():
			plotFunction(data, self._getAutoPlotterStyle(data, newPlotterStyle), options)
		elif self._needRescale(options):
			self._refresh(rescale = True)
		else:
			plotFunction(data, self._getAutoPlotterStyle(data, newPlotterStyle), options)

	def _getAutoPlotterStyle(self, data, plotterStyle):
		if (self._getNItemData() > 1) and (not self.info()._getLegendCustomized()):
			autoPlotterStyle = plotterStyle._createCopy()
			autoDataStyle = autoPlotterStyle.dataStyle()
			autoLineStyle = autoDataStyle.lineStyle()
			autoFillStyle = autoDataStyle.fillStyle()
			autoMarkerStyle = autoDataStyle.markerStyle()
			autoColor = self._getAutoColor()
			if not autoLineStyle._getCustomized('color'):
				autoLineStyle.setParameter('color', autoColor, customize = False)
			if not autoFillStyle._getCustomized('color'):
				autoFillStyle.setParameter('color', autoColor, customize = False)
			if not autoMarkerStyle._getCustomized('color'):
				autoMarkerStyle.setParameter('color', autoColor, customize = False)
			if not autoMarkerStyle._getCustomized('shape'):
				autoMarkerStyle.setParameter('shape', self._getAutoMarker(), customize = False)
			return autoPlotterStyle
		else:
			return plotterStyle._createCopy()

	def _getAutoColor(self):
		colors = ['black', 'blue', 'red', 'green']
		return colors[(self._getNItemData() - 1) % len(colors)]

	def _getAutoMarker(self):
		markers = ['circle', 'square', 'diamond', 'triangle', 'cross']
		return markers[(self._getNItemData() - 1) % len(markers)]

	def _needInitialize(self, options):
		if self._getCreateAxisBox():
			self._setCreateAxisBox(False)
			return True
		elif self._getUnderRescaling():
			return True
		else:
			if self._needReplace(options):
				return True
			else:
				if self._getNItemData() == 1:
					return True
				else:
					return False

	def _needReplace(self, options):
		if options.has_key('mode'):
			if options['mode'] == 'replace':
				return True
			elif options['mode'] == 'overlay':
				return False
			else:
				raise IllegalArgumentException('Invalid plotting option "mode=%s".' % options['mode'])
		else:
			### Default mode is 'overlay'.
			return False

	def _needRescale(self, options):
		if self._needReplace(options):
			return False
		elif options.has_key('rescale'):
			if options['rescale'] == True:
				if self._getNItemData() == 1:
					return False
				else:
					return True
			elif options['rescale'] == False:
				return False
			else:
				raise IllegalArgumentException('Invalid plotting option "rescale=%s".' % options['rescale'])
		else:
			### Default is 'rescale=yes'.
			if self._getNItemData() == 1:
				return False
			else:
				return True

	def _setCreateAxisBox(self, boolean):
		self._createAxisBox = boolean

	def _getCreateAxisBox(self):
		return self._createAxisBox

	def _getMarginedPlus(self, data, showErrorBars, sample):
		if showErrorBars:
			return data + 1.2 * sqrt(fabs(data))
		else:
			return data + 0.1 * sample

	def _getMarginedMinus(self, data, showErrorBars, sample):
		if showErrorBars:
			return data - 1.2 * sqrt(fabs(data))
		else:
			return data - 0.1 * sample

	def _getOrderedBins2D(self, axisX, axisY, surfaceYZz, surfaceZXz):
		if surfaceYZz < 0.0 and surfaceZXz < 0.0:
			#0
			binsX = range(axisX.bins() - 1, -1, -1)
			binsY = range(axisY.bins() - 1, -1, -1)
		elif surfaceYZz < 0.0 and surfaceZXz >= 0.0:
			#3
			binsX = range(axisX.bins() - 1, -1, -1)
			binsY = range(axisY.bins())
		elif surfaceYZz >= 0.0 and surfaceZXz < 0.0:
			#1
			binsX = range(axisX.bins())
			binsY = range(axisY.bins() - 1, -1, -1)
		elif surfaceYZz >= 0.0 and surfaceZXz >= 0.0:
			#2
			binsX = range(axisX.bins())
			binsY = range(axisY.bins())
		return binsX, binsY

	def _getOrderedBins3D(self, axisX, axisY, axisZ, surfaceXYz, surfaceYZz, surfaceZXz):
		if surfaceXYz < 0.0 and surfaceYZz < 0.0 and surfaceZXz < 0.0:
			#0
			binsX = range(axisX.bins() - 1, -1, -1)
			binsY = range(axisY.bins() - 1, -1, -1)
			binsZ = range(axisZ.bins() - 1, -1, -1)
		elif surfaceXYz < 0.0 and surfaceYZz < 0.0 and surfaceZXz >= 0.0:
			#3
			binsX = range(axisX.bins() - 1, -1, -1)
			binsY = range(axisY.bins())
			binsZ = range(axisZ.bins() - 1, -1, -1)
		elif surfaceXYz < 0.0 and surfaceYZz >= 0.0 and surfaceZXz < 0.0:
			#1
			binsX = range(axisX.bins())
			binsY = range(axisY.bins() - 1, -1, -1)
			binsZ = range(axisZ.bins() - 1, -1, -1)
		elif surfaceXYz < 0.0 and surfaceYZz >= 0.0 and surfaceZXz >= 0.0:
			#2
			binsX = range(axisX.bins())
			binsY = range(axisY.bins())
			binsZ = range(axisZ.bins() - 1, -1, -1)
		elif surfaceXYz >= 0.0 and surfaceYZz < 0.0 and surfaceZXz < 0.0:
			#4
			binsX = range(axisX.bins() - 1, -1, -1)
			binsY = range(axisY.bins() - 1, -1, -1)
			binsZ = range(axisZ.bins())
		elif surfaceXYz >= 0.0 and surfaceYZz < 0.0 and surfaceZXz >= 0.0:
			#7
			binsX = range(axisX.bins() - 1, -1, -1)
			binsY = range(axisY.bins())
			binsZ = range(axisZ.bins())
		elif surfaceXYz >= 0.0 and surfaceYZz >= 0.0 and surfaceZXz < 0.0:
			#5
			binsX = range(axisX.bins())
			binsY = range(axisY.bins() - 1, -1, -1)
			binsZ = range(axisZ.bins())
		elif surfaceXYz >= 0.0 and surfaceYZz >= 0.0 and surfaceZXz >= 0.0:
			#6
			binsX = range(axisX.bins())
			binsY = range(axisY.bins())
			binsZ = range(axisZ.bins())
		return binsX, binsY, binsZ

	def _plotHistogram1D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Specific variables.
		axisX = item.axis()

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		if self._needInitialize(options):
			bestLowerX, bestUpperX = self._bestRange(axisX, xAxisStyle)
			bestLowerY, bestUpperY = self._bestHeightRange([axisX], yAxisStyle, dataStyle, item)
			self._createAxisBox2D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, plotterStyle)
		if self._getUnderRescaling():
			return
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		convertX, convertY = self._getConvertersToCanvas()

		### Plot.
		if self._isMatplotlib:
			import pylab
			### Line corners.
			axisX = item.axis()
			edges = axisX._getEdges()
			pointsX = [i for i in edges for dummy in [1, 2]]
			pointsY = [item.binHeight(i) for i in range(len(edges) - 1) for dummy in [1, 2]]
			pointsY.insert(0, item.binHeight(IAxis.UNDERFLOW_BIN))
			pointsY.append(item.binHeight(IAxis.OVERFLOW_BIN))
			pylab.axes(self._getGuiPlotter().getAxes(self._serialNumber))
			pylab.plot(pointsX, pointsY, color = plotterStyle.dataStyle().lineStyle().color())
			return
		parameterFormat = dataStyle._parameterData('histogram1DFormat')
		parameterDataPoint = dataStyle._parameterData('dataPoint')
		parameterShowMarkers = dataStyle._parameterData('showMarkers')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')
		binsX = [axisX.UNDERFLOW_BIN]
		binsX.extend(range(axisX.bins()))
		binsX.append(axisX.OVERFLOW_BIN)
		previousHeight = y1
		tempFillLineStyle = ILineStyle()
		tempFillLineStyle.setColor(fillStyle.color())
		tempErrorLineStyle = ILineStyle()
		if dataStyle._getCustomized('errorBarsColor'):
			tempErrorLineStyle.setColor(dataStyle._parameterData('errorBarsColor'))
		else:
			tempErrorLineStyle.setColor(lineStyle.color())
		for binNumber in binsX:
			binLowerValue = axisX.binLowerEdge(binNumber)
			binUpperValue = axisX.binUpperEdge(binNumber)
			if (binUpperValue <= lowerX) or (binLowerValue >= upperX):
				continue
			height = convertY(lowerY, upperY, item.binHeight(binNumber))
			binLower = convertX(lowerX, upperX, binLowerValue)
			binUpper = convertX(lowerX, upperX, binUpperValue)
			if parameterFormat == 'histogram':
				self._create_styledLineInBox(lineStyle, tagsPlot, x0, y0, x1, y1, binLower, previousHeight, binLower, height, binUpper, height)
				previousHeight = height
			elif parameterFormat == 'bar':
				self._create_styledRectangleInBox(tempFillLineStyle, fillStyle, tagsPlot, x0, y0, x1, y1, binLower + 1, height + 1, binUpper - 1, y1 - 1)
				self._create_styledLineInBox(lineStyle, tagsPlot, x0, y0, x1, y1, binLower, y1 - 1, binLower, height, binUpper, height, binUpper, y1 - 1)
			else:
				raise RuntimeException()

			if parameterDataPoint == 'center':
				dataPoint = (binLower + binUpper) / 2
			elif parameterDataPoint == 'mean':
				dataPoint = convertX(lowerX, upperX, item.binMean(binNumber))
			else:
				raise RuntimeException()

			### Marker.
			if parameterShowMarkers:
				self._create_styledMarker(markerStyle, tagsPlot, dataPoint, height)

			### Error bar.
			if parameterShowErrorBars == True:
				heightValue = item.binHeight(binNumber)
				errorValue = item.binError(binNumber)
				errorUpper = convertY(lowerY, upperY, heightValue + errorValue)
				errorLower = convertY(lowerY, upperY, heightValue - errorValue)
				endLineHalfLength = max(2, 3 * tempErrorLineStyle.thickness() / 2)
				self._create_styledLineInBox(tempErrorLineStyle, tagsPlot, x0, y0, x1, y1, dataPoint, errorLower, dataPoint, errorUpper)

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['entries', '%s' % item.entries()])
			StatisticsData.append(['under', '%s' % item.binEntries(IAxis.UNDERFLOW_BIN)])
			StatisticsData.append(['over', '%s' % item.binEntries(IAxis.OVERFLOW_BIN)])
			StatisticsData.append(['mean', '%f' % item.mean()])
			StatisticsData.append(['rms', '%f' % item.rms()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, lineStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotCloud1D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		### Parameters.
		parameterFormat = dataStyle._parameterData('cloud1DFormat')
		parameterDataPoint = dataStyle._parameterData('dataPoint')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')

		if parameterFormat == 'histogram':
			if options.has_key('nBinsX'):
				nBinsX = int(options['nBinsX'])
			else:
				nBinsX = 50
			item2 = item._getRawHistogram(nBinsX, item.lowerEdge(), item.upperEdge())
			item.fillHistogram(item2)
			self._removeItemData(item)
			return self._plot(item2, plotterStyle, options)

		if self._needInitialize(options):
			sample = item.upperEdge() - item.lowerEdge()
			bestLowerX = self._getMarginedMinus(item.lowerEdge(), parameterShowErrorBars, sample)
			bestUpperX = self._getMarginedPlus(item.upperEdge(), parameterShowErrorBars,sample)
			originalAxisYType = yAxisStyle.parameterValue('type')
			if parameterFormat == 'scatter':
				bestLowerY = -1
				bestUpperY = 1
			elif parameterFormat == 'scatterIndexed':
				bestLowerY = 0
				bestUpperY = self._getMarginedPlus(item.entries(), parameterShowErrorBars, sample)
			yAxisStyle.setParameter('type', 'int', customize = False)
			self._createAxisBox2D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, plotterStyle)
			yAxisStyle.setParameter('type', originalAxisYType, customize = False)
		if self._getUnderRescaling():
			return
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		convertX, convertY = self._getConvertersToCanvas()

		### Plot.
		canvasY = convertY(lowerY, upperY, 0)
		for i in range(item.entries()):
			valueX = item.value(i)
			if not (lowerX <= valueX <= upperX):
				continue
			canvasX = convertX(lowerX, upperX, valueX)
			if parameterFormat == 'scatterIndexed':
				canvasY = convertY(lowerY, upperY, i)
			self._create_styledMarker(markerStyle, tagsPlot, canvasX, canvasY)

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['entries', '%s' % item.entries()])
			StatisticsData.append(['mean', '%f' % item.mean()])
			StatisticsData.append(['rms', '%f' % item.rms()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, markerStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotProfile1D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Specific variables.
		axisX = item.axis()

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		if self._needInitialize(options):
			bestLowerX, bestUpperX = self._bestRange(axisX, xAxisStyle)
			bestLowerY, bestUpperY = self._bestHeightRange([axisX], yAxisStyle, dataStyle, item)
			self._createAxisBox2D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, plotterStyle)
		if self._getUnderRescaling():
			return
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		convertX, convertY = self._getConvertersToCanvas()

		### Plot.
		parameterDataPoint = dataStyle._parameterData('dataPoint')
		parameterShowMarkers = dataStyle._parameterData('showMarkers')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')
		binsX = [axisX.UNDERFLOW_BIN]
		binsX.extend(range(axisX.bins()))
		binsX.append(axisX.OVERFLOW_BIN)
		tempErrorLineStyle = ILineStyle()
		if dataStyle._getCustomized('errorBarsColor'):
			tempErrorLineStyle.setColor(dataStyle._parameterData('errorBarsColor'))
		else:
			tempErrorLineStyle.setColor(lineStyle.color())
		endLineHalfLength = max(2, 3 * tempErrorLineStyle.thickness() / 2)
		for binNumber in binsX:
			heightValue = item.binHeight(binNumber)
			height = convertY(lowerY, upperY, heightValue)
			binLower = convertX(lowerX, upperX, axisX.binLowerEdge(binNumber))
			binUpper = convertX(lowerX, upperX, axisX.binUpperEdge(binNumber))
			self._create_styledLineInBox(lineStyle, tagsPlot, x0, y0, x1, y1, binLower, height, binUpper, height)

			rmsPoint = convertX(lowerX, upperX, item.binMean(binNumber))
			rmsValue = item.binRms(binNumber)
			rmsUpper = convertY(lowerY, upperY, heightValue + rmsValue)
			rmsLower = convertY(lowerY, upperY, heightValue - rmsValue)
			rmsBarThickness = lineStyle.thickness()
			endLineHalfLength = 3 * lineStyle.thickness() / 2
			self._create_styledLineInBox(lineStyle, tagsPlot, x0, y0, x1, y1, rmsPoint, rmsLower, rmsPoint, rmsUpper)

			if parameterDataPoint == 'center':
				dataPoint = (binLower + binUpper) / 2.0
			elif parameterDataPoint == 'mean':
				dataPoint = convertX(lowerX, upperX, item.binMean(binNumber))
			else:
				raise RuntimeException()

			### Marker.
			if parameterShowMarkers:
				self._create_styledMarker(markerStyle, tagsPlot, dataPoint, height)

			### Error bar.
			if parameterShowErrorBars:
				heightValue = item.binHeight(binNumber)
				errorValue = item.binError(binNumber)
				errorUpper = convertY(lowerY, upperY, heightValue + errorValue)
				errorLower = convertY(lowerY, upperY, heightValue - errorValue)
				self._create_styledLineInBox(tempErrorLineStyle, tagsPlot, x0, y0, x1, y1, dataPoint, errorLower, dataPoint, errorUpper)

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['entries', '%s' % item.entries()])
			StatisticsData.append(['under', '%s' % item.binEntries(IAxis.UNDERFLOW_BIN)])
			StatisticsData.append(['over', '%s' % item.binEntries(IAxis.OVERFLOW_BIN)])
			StatisticsData.append(['mean', '%f' % item.mean()])
			StatisticsData.append(['rms', '%f' % item.rms()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, lineStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotDataPointSet1D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		### Parameters.
		parameterFormat = dataStyle._parameterData('dataPointSet1DFormat')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')

		if self._needInitialize(options):
			sample = item.upperExtent(0) - item.lowerExtent(0)
			bestLowerX = self._getMarginedMinus(item.lowerExtent(0), parameterShowErrorBars, sample)
			bestUpperX = self._getMarginedPlus(item.upperExtent(0), parameterShowErrorBars, sample)
			originalAxisYType = yAxisStyle.parameterValue('type')
			yAxisStyle.setParameter('type', 'int', customize = False)
			if parameterFormat == 'scatter':
				bestLowerY = -1
				bestUpperY = 1
			elif parameterFormat == 'scatterIndexed':
				bestLowerY = 0
				bestUpperY = self._getMarginedPlus(item.size(), parameterShowErrorBars, sample)
			self._createAxisBox2D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, plotterStyle)
			yAxisStyle.setParameter('type', originalAxisYType, customize = False)
		if self._getUnderRescaling():
			return
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		convertX, convertY = self._getConvertersToCanvas()

		### Plot.
		canvasY = convertY(lowerY, upperY, 0)
		tempErrorLineStyle = ILineStyle()
		if dataStyle._getCustomized('errorBarsColor'):
			tempErrorLineStyle.setColor(dataStyle._parameterData('errorBarsColor'))
		else:
			tempErrorLineStyle.setColor(lineStyle.color())
		endLineHalfLength = max(2, 3 * tempErrorLineStyle.thickness() / 2)
		for i in range(item.size()):
			measurementX = item.point(i).coordinate(0)
			valueX = measurementX.value()
			if not (lowerX <= valueX <= upperX):
				continue
			canvasX = convertX(lowerX, upperX, valueX)
			if parameterFormat == 'scatterIndexed':
				canvasY = convertY(lowerY, upperY, i)
			self._create_styledMarker(markerStyle, tagsPlot, canvasX, canvasY)

			### Error bar.
			if parameterShowErrorBars == True:
				errorUpper = convertX(lowerX, upperX, valueX + measurementX.errorPlus())
				errorLower = convertX(lowerX, upperX, valueX - measurementX.errorMinus())
				self._create_styledLineInBox(tempErrorLineStyle, tagsPlot, x0, y0, x1, y1, errorLower, canvasY, errorUpper, canvasY)

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['size', '%s' % item.size()])
			StatisticsData.append(['dimension', '%s' % item.dimension()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, markerStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotFunction1D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		if self._needInitialize(options):
			if self._getUnderRescaling():
				bestLowerX, bestUpperX = self._getAxisValueRangeX()
				bestLowerY, bestUpperY = self._getAxisValueRangeY()
			else:
				### X range.
				if options.has_key('minX'):
					bestLowerX = float(options['minX'])
				elif self._getXLimits()[0] != None:
					bestLowerX = self._getXLimits()[0]
				else:
					bestLowerX = -10.0
				if options.has_key('maxX'):
					bestUpperX = float(options['maxX'])
				elif self._getXLimits()[1] != None:
					bestUpperX = self._getXLimits()[1]
				else:
					bestUpperX = 10.0

				### Y range.
				if options.has_key('minY'):
					bestLowerY = float(options['minY'])
				elif self._getYLimits()[0] != None:
					bestLowerY = self._getYLimits()[0]
				else:
					bestLowerY = -10.0
				if options.has_key('maxY'):
					bestUpperY = float(options['maxY'])
				elif self._getYLimits()[1] != None:
					bestUpperY = self._getYLimits()[1]
				else:
					bestUpperY = 10.0

			### Create axis box.
			self._createAxisBox2D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, plotterStyle)

		if self._getUnderRescaling():
			return
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		convertX, convertY = self._getConvertersToCanvas()

		### Plot.
		if options.has_key('minX'):
			functionLowerX = float(options['minX'])
		else:
			functionLowerX = lowerX
		if options.has_key('maxX'):
			functionUpperX = float(options['maxX'])
		else:
			functionUpperX = upperX
		functionLowerCanvasX = convertX(lowerX, upperX, functionLowerX)
		functionUpperCanvasX = convertX(lowerX, upperX, functionUpperX)
		functionSpanX = functionUpperX - functionLowerX
		spanCanvasX = functionUpperCanvasX - functionLowerCanvasX
		points = []
		for i in range(int(spanCanvasX) + 1):
			valueX = functionLowerX + functionSpanX * i / spanCanvasX
			canvasY = convertY(lowerY, upperY, item.value([valueX]))
			if y0 <= canvasY <= y1:
				canvasX = functionLowerCanvasX + i
				points.append(canvasX)
				points.append(canvasY)
			elif not points == []:
				self._create_styledLine(lineStyle, tagsPlot, *points)
				points = []
		if not points == []:
			self._create_styledLine(lineStyle, tagsPlot, *points)

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['dimension', '%s' % item.dimension()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, lineStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotHistogram2D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Specific variables.
		axisX = item.xAxis()
		axisY = item.yAxis()

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		zAxisStyle = plotterStyle.zAxisStyle()
		scalingX = xAxisStyle._parameterData('scale')
		scalingY = yAxisStyle._parameterData('scale')
		scalingZ = zAxisStyle._parameterData('scale')
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		### Parameters.
		parameterFormat = dataStyle._parameterData('histogram2DFormat')
		parameterDataPoint = dataStyle._parameterData('dataPoint')
		parameterShowMarkers = dataStyle._parameterData('showMarkers')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')

		if self._needInitialize(options):
			bestLowerX, bestUpperX = self._bestRange(axisX, xAxisStyle)
			bestLowerY, bestUpperY = self._bestRange(axisY, yAxisStyle)
			bestLowerZ, bestUpperZ = self._bestHeightRange([axisX, axisY], zAxisStyle, dataStyle, item)
			if parameterFormat in ['bar']:
				self._createAxisBox3D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, bestLowerZ, bestUpperZ, plotterStyle)
			elif parameterFormat in ['box', 'ellipse', 'hit']:
				self._createAxisBox2D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, plotterStyle)
				if self._getFinalRescaling() != True:
					self._setAxisValueRangeZ(bestLowerZ, bestUpperZ)
			else:
				raise RuntimeException()
		if self._getUnderRescaling():
			return

		if fillStyle._getCustomized('color'):
			colorFlag = False
		else:
			colorFlag = True

		if parameterFormat in ['bar']:
			(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
			if colorFlag:
				self._drawColorZAxis()
		elif parameterFormat in ['box', 'ellipse', 'hit']:
			convertX, convertY = self._getConvertersToCanvas()
		else:
			raise RuntimeException()

		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		lowerZ, upperZ = self._getAxisValueRangeZ()

		### Plot.
		if parameterFormat in ['bar']:
			surfaceYZz = cYx * cZy - cZx * cYy
			surfaceZXz = cZx * cXy - cXx * cZy
			binsX, binsY = self._getOrderedBins2D(axisX, axisY, surfaceYZz, surfaceZXz)

			tempErrorLineStyle = ILineStyle()
			if dataStyle._getCustomized('errorBarsColor'):
				tempErrorLineStyle.setColor(dataStyle._parameterData('errorBarsColor'))
				colorFlagErrorLine = False
			else:
				tempErrorLineStyle.setColor(lineStyle.color())
				colorFlagErrorLine = True
			if not lineStyle._getCustomized('color'):
				lineStyle.setParameter('color', 'black', customize = False)

			_3DConvertToRatio = self._3DConvertToRatio
			_3DConvertToCanvas = self._3DConvertToCanvas
			_create_styledPolygon = self._create_styledPolygon
			_convertRatioToColor = self._convertRatioToColor
			for binNumberX in binsX:
				binLowerX, binUpperX = axisX._binEdges(binNumberX)
				for binNumberY in binsY:
					binLowerY, binUpperY = axisY._binEdges(binNumberY)
					if parameterDataPoint == 'center':
						dataPointX = (binLowerX + binUpperX) / 2.0
						dataPointY = (binLowerY + binUpperY) / 2.0
					else:
						dataPointX = item.binMeanX(binNumberX, binNumberY)
						dataPointY = item.binMeanY(binNumberX, binNumberY)
					if not (lowerX <= dataPointX <= upperX):
						continue
					if not (lowerY <= dataPointY <= upperY):
						continue
					ratioDataPointX = _3DConvertToRatio(scalingX, lowerX, upperX, dataPointX)
					ratioDataPointY = _3DConvertToRatio(scalingY, lowerY, upperY, dataPointY)
					height = min(upperZ, item.binHeight(binNumberX, binNumberY))
					if height < lowerZ:
						continue
					ratioLowerX = _3DConvertToRatio(scalingX, lowerX, upperX, binLowerX)
					ratioUpperX = _3DConvertToRatio(scalingX, lowerX, upperX, binUpperX)
					ratioLowerY = _3DConvertToRatio(scalingY, lowerY, upperY, binLowerY)
					ratioUpperY = _3DConvertToRatio(scalingY, lowerY, upperY, binUpperY)
					ratioHeight = _3DConvertToRatio(scalingZ, lowerZ, upperZ, height)
					ground0X, ground0Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioLowerY, 0.0)
					ground1X, ground1Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioLowerY, 0.0)
					ground2X, ground2Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioUpperY, 0.0)
					ground3X, ground3Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioUpperY, 0.0)
					point0X, point0Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioLowerY, ratioHeight)
					point1X, point1Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioLowerY, ratioHeight)
					point2X, point2Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioUpperY, ratioHeight)
					point3X, point3Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioUpperY, ratioHeight)

					if colorFlag:
						tempColor = _convertRatioToColor(ratioHeight)
						fillStyle = IFillStyle()
						fillStyle.setColor(tempColor)
						if colorFlagErrorLine:
							tempErrorLineStyle.setColor(tempColor)
					_create_styledPolygon(lineStyle, fillStyle, tagsPlot, point0X, point0Y, point1X, point1Y, point2X, point2Y, point3X, point3Y)
					if surfaceYZz < 0.0:
						_create_styledPolygon(lineStyle, fillStyle, tagsPlot, ground0X, ground0Y, ground3X, ground3Y, point3X, point3Y, point0X, point0Y)
					else:
						_create_styledPolygon(lineStyle, fillStyle, tagsPlot, ground1X, ground1Y, ground2X, ground2Y, point2X, point2Y, point1X, point1Y)
					if surfaceZXz < 0.0:
						_create_styledPolygon(lineStyle, fillStyle, tagsPlot, ground0X, ground0Y, ground1X, ground1Y, point1X, point1Y, point0X, point0Y)
					else:
						_create_styledPolygon(lineStyle, fillStyle, tagsPlot, ground3X, ground3Y, ground2X, ground2Y, point2X, point2Y, point3X, point3Y)

					### Marker.
					if parameterShowMarkers:
						markerX, markerY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioDataPointX, ratioDataPointY, ratioHeight)
						self._create_styledMarker(markerStyle, tagsPlot, markerX, markerY)

					### Error bar.
					if parameterShowErrorBars:
						errorValue = item.binError(binNumberX, binNumberY)
						ratioErrorUpper = _3DConvertToRatio(scalingZ, lowerZ, upperZ, height + errorValue)
						#ratioErrorLower = _3DConvertToRatio(scalingZ, lowerZ, upperZ, height - errorValue)
						errorBarX0, errorBarY0 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioDataPointX, ratioDataPointY, ratioHeight)
						errorBarX1, errorBarY1 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioDataPointX, ratioDataPointY, ratioErrorUpper)
						self._create_styledLine(tempErrorLineStyle, tagsPlot, errorBarX0, errorBarY0, errorBarX1, errorBarY1)
		elif parameterFormat in ['box', 'ellipse', 'hit']:
			### Minimum bin width of X axis.
			binLowerX, binUpperX = axisX._binEdges(0)
			minBinWidthX = binUpperX - binLowerX
			if axisX.isFixedBinning() == False:
				for binNumberX in range(axisX.bins()):
					binLowerX, binUpperX = axisX._binEdges(binNumberX)
					minBinWidthX = min(minBinWidthX, binUpperX - binLowerX)
			### Minimum bin width of Y axis.
			binLowerY, binUpperY = axisY._binEdges(0)
			minBinWidthY = binUpperY - binLowerY
			if axisY.isFixedBinning() == False:
				for binNumberY in range(axisY.bins()):
					binLowerY, binUpperY = axisY._binEdges(binNumberY)
					minBinWidthY = min(minBinWidthY, binUpperY - binLowerY)
			### Select styled plotter.
			if parameterFormat == 'box':
				styledPlotter = self._create_styledRectangle
			elif parameterFormat == 'ellipse':
				styledPlotter = self._create_styledOval
			elif parameterFormat == 'hit':
				styledPlotter = self._create_styledRectangle
			else:
				raise RuntimeException()

			### Line color check.
			if not lineStyle._getCustomized('color'):
				lineStyle.setParameter('color', '', customize = False)

			### Plot.
			_3DConvertToRatio = self._3DConvertToRatio
			_convertRatioToColor = self._convertRatioToColor
			for binNumberX in range(axisX.bins()):
				binLowerX, binUpperX = axisX._binEdges(binNumberX)
				centerX = (binLowerX + binUpperX) / 2.0
				if not (lowerX <= centerX <= upperX):
					continue
				for binNumberY in range(axisY.bins()):
					binLowerY, binUpperY = axisY._binEdges(binNumberY)
					centerY = (binLowerY + binUpperY) / 2.0
					if not (lowerY <= centerY <= upperY):
						continue
					height = item.binHeight(binNumberX, binNumberY)
					if height <= lowerZ:
						continue
					colorRatio = _3DConvertToRatio(scalingZ, lowerZ, upperZ, height)
					if colorFlag:
						tempColor = _convertRatioToColor(colorRatio)
						fillStyle = IFillStyle()
						fillStyle.setParameter('color', tempColor)
					if parameterFormat == 'hit':
						widthX = 0.9 * minBinWidthX
						widthY = 0.9 * minBinWidthY
					else:
						widthRatio = 0.9 * sqrt(colorRatio)
						widthX = widthRatio * minBinWidthX
						widthY = widthRatio * minBinWidthY
						if widthX * widthY == 0.0:
							continue
					cx0 = convertX(lowerX, upperX, centerX - widthX / 2.0)
					cy0 = convertY(lowerY, upperY, centerY + widthY / 2.0)
					cx1 = convertX(lowerX, upperX, centerX + widthX / 2.0)
					cy1 = convertY(lowerY, upperY, centerY - widthY / 2.0)
					styledPlotter(lineStyle, fillStyle, tagsPlot, cx0, cy0, cx1, cy1)
		else:
			raise RuntimeException()

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['entries', '%s' % item.entries()])
			StatisticsData.append(['Xunder', '%s' % item.binEntriesX(axisX.UNDERFLOW_BIN)])
			StatisticsData.append(['Xover', '%s' % item.binEntriesX(axisX.OVERFLOW_BIN)])
			StatisticsData.append(['Xmean', '%f' % item.meanX()])
			StatisticsData.append(['Xrms', '%f' % item.rmsX()])
			StatisticsData.append(['Yunder', '%s' % item.binEntriesY(axisY.UNDERFLOW_BIN)])
			StatisticsData.append(['Yover', '%s' % item.binEntriesY(axisY.OVERFLOW_BIN)])
			StatisticsData.append(['Ymean', '%f' % item.meanY()])
			StatisticsData.append(['Yrms', '%f' % item.rmsY()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, lineStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotCloud2D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		zAxisStyle = plotterStyle.zAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		### Parameters.
		parameterFormat = dataStyle._parameterData('cloud2DFormat')
		parameterDataPoint = dataStyle._parameterData('dataPoint')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')

		if parameterFormat == 'histogram':
			if options.has_key('nBinsX'):
				nBinsX = int(options['nBinsX'])
			else:
				nBinsX = 50
			if options.has_key('nBinsY'):
				nBinsY = int(options['nBinsY'])
			else:
				nBinsY = 50
			item2 = item._getRawHistogram(nBinsX, item.lowerEdgeX(), item.upperEdgeX(), nBinsY, item.lowerEdgeY(), item.upperEdgeY())
			item.fillHistogram(item2)
			self._removeItemData(item)
			return self._plot(item2, plotterStyle, options)

		if self._needInitialize(options):
			sampleX = item.upperEdgeX() - item.lowerEdgeX()
			sampleY = item.upperEdgeY() - item.lowerEdgeY()
			bestLowerX = self._getMarginedMinus(item.lowerEdgeX(), parameterShowErrorBars, sampleX)
			bestUpperX = self._getMarginedPlus(item.upperEdgeX(), parameterShowErrorBars, sampleX)
			bestLowerY = self._getMarginedMinus(item.lowerEdgeY(), parameterShowErrorBars, sampleY)
			bestUpperY = self._getMarginedPlus(item.upperEdgeY(), parameterShowErrorBars, sampleY)
			if parameterFormat in ['scatterIndexed', 'scatterColorIndexed']:
				bestLowerZ = 0
				#bestUpperZ = self._getMarginedPlus(item.entries(), parameterShowErrorBars, item.entries())
				bestUpperZ = item.entries() + 1.0
				originalAxisZType = zAxisStyle.parameterValue('type')
				zAxisStyle.setParameter('type', 'int', customize = False)
				self._createAxisBox3D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, bestLowerZ, bestUpperZ, plotterStyle)
				zAxisStyle.setParameter('type', originalAxisZType, customize = False)
			elif parameterFormat in ['scatter']:
				self._createAxisBox2D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, plotterStyle)
			else:
				raise RuntimeException()
		if self._getUnderRescaling():
			return

		if parameterFormat in ['scatterIndexed', 'scatterColorIndexed']:
			(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
			scalingZ = self._getScalingZ()
			lowerZ, upperZ = self._getAxisValueRangeZ()
		elif parameterFormat in ['scatter']:
			convertX, convertY = self._getConvertersToCanvas()
		else:
			raise RuntimeException()

		scalingX = self._getScalingX()
		scalingY = self._getScalingY()
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()

		### Plot.
		if parameterFormat in ['scatterIndexed', 'scatterColorIndexed']:
			_3DConvertToRatio = self._3DConvertToRatio
			_3DConvertToCanvas = self._3DConvertToCanvas
			_convertRatioToColor = self._convertRatioToColor
			_create_styledMarker = self._create_styledMarker
			(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()

			if parameterFormat == 'scatterColorIndexed':
				self._drawColorZAxis()

			for i in range(item.entries()):
				valueX = item.valueX(i)
				if not (lowerX <= valueX <= upperX):
					continue
				valueY = item.valueY(i)
				if not (lowerY <= valueY <= upperY):
					continue
				ratioValueX = _3DConvertToRatio(scalingX, lowerX, upperX, valueX)
				ratioValueY = _3DConvertToRatio(scalingY, lowerY, upperY, valueY)
				ratioIndexZ = _3DConvertToRatio(scalingZ, lowerZ, upperZ, i)
				pointValueX, pointValueY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioValueY, ratioIndexZ)
				if parameterFormat == 'scatterColorIndexed':
					colorRatio = _3DConvertToRatio(scalingZ, lowerZ, upperZ, i)
					tempColor = _convertRatioToColor(colorRatio)
					tempIndexMarkerStyle = markerStyle._createCopy()
					tempIndexMarkerStyle.setColor(tempColor)
					_create_styledMarker(tempIndexMarkerStyle, tagsPlot, pointValueX, pointValueY)
				else:
					_create_styledMarker(markerStyle, tagsPlot, pointValueX, pointValueY)
		elif parameterFormat in ['scatter']:
			_create_styledMarker = self._create_styledMarker
			for i in range(item.entries()):
				valueX = item.valueX(i)
				if not (lowerX <= valueX <= upperX):
					continue
				valueY = item.valueY(i)
				if not (lowerY <= valueY <= upperY):
					continue
				_create_styledMarker(markerStyle, tagsPlot, convertX(lowerX, upperX, valueX), convertY(lowerY, upperY, valueY))
		else:
			raise RuntimeException()

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['entries', '%s' % item.entries()])
			StatisticsData.append(['Xmean', '%f' % item.meanX()])
			StatisticsData.append(['Xrms', '%f' % item.rmsX()])
			StatisticsData.append(['Ymean', '%f' % item.meanY()])
			StatisticsData.append(['Yrms', '%f' % item.rmsY()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, markerStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotProfile2D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Specific variables.
		axisX = item.xAxis()
		axisY = item.yAxis()

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		zAxisStyle = plotterStyle.zAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		if self._needInitialize(options):
			bestLowerX, bestUpperX = self._bestRange(axisX, xAxisStyle)
			bestLowerY, bestUpperY = self._bestRange(axisY, yAxisStyle)
			bestLowerZ, bestUpperZ = self._bestHeightRange([axisX, axisY], zAxisStyle, dataStyle, item)
			self._createAxisBox3D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, bestLowerZ, bestUpperZ, plotterStyle)
		if self._getUnderRescaling():
			return
		(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
		surfaceXYz = cXx * cYy - cYx * cXy
		surfaceYZz = cYx * cZy - cZx * cYy
		surfaceZXz = cZx * cXy - cXx * cZy
		binsX, binsY = self._getOrderedBins2D(axisX, axisY, surfaceYZz, surfaceZXz)
		scalingX = self._getScalingX()
		scalingY = self._getScalingY()
		scalingZ = self._getScalingZ()
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		lowerZ, upperZ = self._getAxisValueRangeZ()

		if lineStyle._getCustomized('color') and fillStyle._getCustomized('color'):
			colorFlag = False
		else:
			colorFlag = True
			self._drawColorZAxis()

		### Plot.
		parameterDataPoint = dataStyle._parameterData('dataPoint')
		parameterShowMarkers = dataStyle._parameterData('showMarkers')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')
		tempErrorLineStyle = ILineStyle()
		if dataStyle._getCustomized('errorBarsColor'):
			tempErrorLineStyle.setColor(dataStyle._parameterData('errorBarsColor'))
		else:
			tempErrorLineStyle.setColor(lineStyle.color())
		endLineHalfLength = max(2, 3 * tempErrorLineStyle.thickness() / 2)

		for binNumberX in binsX:
			_3DConvertToRatio = self._3DConvertToRatio
			_3DConvertToCanvas = self._3DConvertToCanvas
			_convertRatioToColor = self._convertRatioToColor
			_create_styledLine = self._create_styledLine
			_create_styledPolygon = self._create_styledPolygon
			for binNumberY in binsY:
				rmsX = item.binMeanX(binNumberX, binNumberY)
				if not (lowerX <= rmsX <= upperX):
					continue
				rmsY = item.binMeanY(binNumberX, binNumberY)
				if not (lowerY <= rmsY <= upperY):
					continue
				height = item.binHeight(binNumberX, binNumberY)
				if not (lowerZ <= height <= upperZ):
					continue
				ratioHeight = _3DConvertToRatio(scalingZ, lowerZ, upperZ, height)

				binLowerX, binUpperX = axisX._binEdges(binNumberX)
				binLowerY, binUpperY = axisY._binEdges(binNumberY)
				ratioLowerX = _3DConvertToRatio(scalingX, lowerX, upperX, binLowerX)
				ratioUpperX = _3DConvertToRatio(scalingX, lowerX, upperX, binUpperX)
				ratioLowerY = _3DConvertToRatio(scalingY, lowerY, upperY, binLowerY)
				ratioUpperY = _3DConvertToRatio(scalingY, lowerY, upperY, binUpperY)
				point0X, point0Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioLowerY, ratioHeight)
				point1X, point1Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioLowerY, ratioHeight)
				point2X, point2Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioUpperY, ratioHeight)
				point3X, point3Y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioUpperY, ratioHeight)

				#rmsX = item.binMeanX(binNumberX, binNumberY)
				#rmsY = item.binMeanY(binNumberX, binNumberY)
				rms = item.binRms(binNumberX, binNumberY)
				rmsUpper = height + rms
				rmsLower = height - rms
				ratioRmsX = _3DConvertToRatio(scalingX, lowerX, upperX, rmsX)
				ratioRmsY = _3DConvertToRatio(scalingY, lowerY, upperY, rmsY)
				ratioRmsUpper = min(1.0, _3DConvertToRatio(scalingZ, lowerZ, upperZ, rmsUpper))
				ratioRmsLower = max(0.0, _3DConvertToRatio(scalingZ, lowerZ, upperZ, rmsLower))
				pointHeightX, pointHeightY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioRmsX, ratioRmsY, ratioHeight)
				pointRmsLowerX, pointRmsLowerY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioRmsX, ratioRmsY, ratioRmsLower)
				pointRmsUpperX, pointRmsUpperY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioRmsX, ratioRmsY, ratioRmsUpper)

				if colorFlag:
					tempColor = _convertRatioToColor(ratioHeight)
					tempLineStyle = lineStyle._createCopy()
					tempLineStyle.setColor('black')
					tempFillStyle = fillStyle._createCopy()
					tempFillStyle.setColor(tempColor)
				else:
					tempLineStyle = lineStyle
					tempFillStyle = fillStyle

				if surfaceXYz >= 0.0:
					_create_styledLine(tempLineStyle, tagsPlot, pointRmsLowerX, pointRmsLowerY, pointHeightX, pointHeightY)
					_create_styledPolygon(tempLineStyle, tempFillStyle, tagsPlot, point3X, point3Y, point0X, point0Y, point1X, point1Y, point2X, point2Y)
					_create_styledLine(tempLineStyle, tagsPlot, pointRmsUpperX, pointRmsUpperY, pointHeightX, pointHeightY)
				else:
					_create_styledLine(tempLineStyle, tagsPlot, pointRmsUpperX, pointRmsUpperY, pointHeightX, pointHeightY)
					_create_styledPolygon(tempLineStyle, tempFillStyle, tagsPlot, point3X, point3Y, point0X, point0Y, point1X, point1Y, point2X, point2Y)
					_create_styledLine(tempLineStyle, tagsPlot, pointRmsLowerX, pointRmsLowerY, pointHeightX, pointHeightY)

				if parameterDataPoint == 'center':
					dataPointX = (binLowerX + binUpperX) / 2.0
					dataPointY = (binLowerY + binUpperY) / 2.0
				elif parameterDataPoint == 'mean':
					dataPointX = item.binMeanX(binNumberX, binNumberY)
					dataPointY = item.binMeanY(binNumberX, binNumberY)
				else:
					raise RuntimeException()
				ratioDataPointX = _3DConvertToRatio(scalingX, lowerX, upperX, dataPointX)
				ratioDataPointY = _3DConvertToRatio(scalingY, lowerY, upperY, dataPointY)
				pointDataPointX, pointDataPointY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioDataPointX, ratioDataPointY, ratioHeight)

				### Marker.
				if parameterShowMarkers:
					self._create_styledMarker(markerStyle, tagsPlot, pointDataPointX, pointDataPointY)

				### Error bar.
				if parameterShowErrorBars:
					error = item.binError(binNumberX, binNumberY)
					ratioErrorUpper = _3DConvertToRatio(scalingZ, lowerZ, upperZ, height + error)
					ratioErrorLower = _3DConvertToRatio(scalingZ, lowerZ, upperZ, height - error)
					pointErrorUpperX, pointErrorUpperY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioDataPointX, ratioDataPointY, ratioErrorUpper)
					pointErrorLowerX, pointErrorLowerY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioDataPointX, ratioDataPointY, ratioErrorLower)
					_create_styledLine(tempErrorLineStyle, tagsPlot, pointErrorUpperX, pointErrorUpperY, pointErrorLowerX, pointErrorLowerY)

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['entries', '%s' % item.entries()])
			StatisticsData.append(['Xunder', '%s' % item.binEntriesX(axisX.UNDERFLOW_BIN)])
			StatisticsData.append(['Xover', '%s' % item.binEntriesX(axisX.OVERFLOW_BIN)])
			StatisticsData.append(['Xmean', '%f' % item.meanX()])
			StatisticsData.append(['Xrms', '%f' % item.rmsX()])
			StatisticsData.append(['Yunder', '%s' % item.binEntriesY(axisY.UNDERFLOW_BIN)])
			StatisticsData.append(['Yover', '%s' % item.binEntriesY(axisY.OVERFLOW_BIN)])
			StatisticsData.append(['Ymean', '%f' % item.meanY()])
			StatisticsData.append(['Yrms', '%f' % item.rmsY()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, lineStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotDataPointSet2D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		zAxisStyle = plotterStyle.zAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		### Parameters.
		parameterFormat = dataStyle._parameterData('dataPointSet2DFormat')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')
		parameterErrorBarsColor = dataStyle._parameterData('errorBarsColor')

		if self._needInitialize(options):
			sampleX = item.upperExtent(0) - item.lowerExtent(0)
			sampleY = item.upperExtent(1) - item.lowerExtent(1)
			bestLowerX = self._getMarginedMinus(item.lowerExtent(0), parameterShowErrorBars, sampleX)
			bestUpperX = self._getMarginedPlus(item.upperExtent(0), parameterShowErrorBars, sampleX)
			bestLowerY = self._getMarginedMinus(item.lowerExtent(1), parameterShowErrorBars, sampleY)
			bestUpperY = self._getMarginedPlus(item.upperExtent(1), parameterShowErrorBars, sampleY)
			if parameterFormat in ['scatterIndexed', 'scatterColorIndexed']:
				bestLowerZ = 0
				bestUpperZ = self._getMarginedPlus(item.size(), parameterShowErrorBars, item.size())
				originalAxisZType = zAxisStyle.parameterValue('type')
				zAxisStyle.setParameter('type', 'int', customize = False)
				self._createAxisBox3D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, bestLowerZ, bestUpperZ, plotterStyle)
				zAxisStyle.setParameter('type', originalAxisZType, customize = False)
			elif parameterFormat in ['scatter']:
				self._createAxisBox2D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, plotterStyle)
			else:
				raise RuntimeException()
		if self._getUnderRescaling():
			return

		if parameterFormat in ['scatterIndexed', 'scatterColorIndexed']:
			(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
			scalingZ = self._getScalingZ()
			lowerZ, upperZ = self._getAxisValueRangeZ()
		elif parameterFormat in ['scatter']:
			convertX, convertY = self._getConvertersToCanvas()
		else:
			raise RuntimeException()

		scalingX = self._getScalingX()
		scalingY = self._getScalingY()
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()

		### Plot.
		errorLineStyle = ILineStyle()
		errorLineStyle.setColor(parameterErrorBarsColor)
		endLineHalfLength = 3 * errorLineStyle.thickness() / 2

		if parameterFormat == 'scatterColorIndexed':
			self._drawColorZAxis()

		if parameterFormat in ['scatterIndexed', 'scatterColorIndexed']:
			_3DConvertToRatio = self._3DConvertToRatio
			_3DConvertToCanvas = self._3DConvertToCanvas
			_convertRatioToColor = self._convertRatioToColor
			_create_styledLine = self._create_styledLine
			_create_styledMarker = self._create_styledMarker
			(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
			itemSize = item.size()
			for i in range(itemSize):
				measurementX = item.point(i).coordinate(0)
				measurementY = item.point(i).coordinate(1)
				valueX = measurementX.value()
				if not (lowerX <= valueX <= upperX):
					continue
				valueY = measurementY.value()
				if not (lowerY <= valueY <= upperY):
					continue
				ratioValueX = _3DConvertToRatio(scalingX, lowerX, upperX, valueX)
				ratioValueY = _3DConvertToRatio(scalingY, lowerY, upperY, valueY)
				ratioIndexZ = _3DConvertToRatio(scalingZ, lowerZ, upperZ, i)
				pointValueX, pointValueY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioValueY, ratioIndexZ)
				if parameterFormat == 'scatterColorIndexed':
					tempColor = _convertRatioToColor(ratioIndexZ)
					tempIndexMarkerStyle = markerStyle._createCopy()
					tempIndexMarkerStyle.setColor(tempColor)
					_create_styledMarker(tempIndexMarkerStyle, tagsPlot, pointValueX, pointValueY)
					errorLineStyle = ILineStyle()
					errorLineStyle.setColor(tempColor)
				else:
					_create_styledMarker(markerStyle, tagsPlot, pointValueX, pointValueY)

				### Error bar.
				if parameterShowErrorBars == True:
					errorUpperX = valueX + measurementX.errorPlus()
					errorLowerX = valueX - measurementX.errorMinus()
					errorUpperY = valueY + measurementY.errorPlus()
					errorLowerY = valueY - measurementY.errorMinus()
					ratioErrorUpperX = _3DConvertToRatio(scalingX, lowerX, upperX, errorUpperX)
					ratioErrorLowerX = _3DConvertToRatio(scalingX, lowerX, upperX, errorLowerX)
					ratioErrorUpperY = _3DConvertToRatio(scalingY, lowerY, upperY, errorUpperY)
					ratioErrorLowerY = _3DConvertToRatio(scalingY, lowerY, upperY, errorLowerY)
					pointErrorUpperXX, pointErrorUpperXY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioErrorUpperX, ratioValueY, ratioIndexZ)
					pointErrorLowerXX, pointErrorLowerXY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioErrorLowerX, ratioValueY, ratioIndexZ)
					pointErrorUpperYX, pointErrorUpperYY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioErrorUpperY, ratioIndexZ)
					pointErrorLowerYX, pointErrorLowerYY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioErrorLowerY, ratioIndexZ)
					_create_styledLine(errorLineStyle, tagsPlot, pointErrorLowerXX, pointErrorLowerXY, pointErrorUpperXX, pointErrorUpperXY)
					_create_styledLine(errorLineStyle, tagsPlot, pointErrorLowerYX, pointErrorLowerYY, pointErrorUpperYX, pointErrorUpperYY)

		elif parameterFormat in ['scatter']:
			for i in range(item.size()):
				measurementX = item.point(i).coordinate(0)
				measurementY = item.point(i).coordinate(1)
				valueX = measurementX.value()
				if not (lowerX <= valueX <= upperX):
					continue
				valueY = measurementY.value()
				if not (lowerY <= valueY <= upperY):
					continue
				canvasX = convertX(lowerX, upperX, valueX)
				canvasY = convertY(lowerY, upperY, valueY)
				self._create_styledMarker(markerStyle, tagsPlot, canvasX, canvasY)

				### Error bar.
				if parameterShowErrorBars == True:
					errorUpperX = convertX(lowerX, upperX, valueX + measurementX.errorPlus())
					errorLowerX = convertX(lowerX, upperX, valueX - measurementX.errorMinus())
					errorUpperY = convertY(lowerY, upperY, valueY + measurementY.errorPlus())
					errorLowerY = convertY(lowerY, upperY, valueY - measurementY.errorMinus())
					self._create_styledLineInBox(errorLineStyle, tagsPlot, x0, y0, x1, y1, errorLowerX, canvasY, errorUpperX, canvasY)
					self._create_styledLineInBox(errorLineStyle, tagsPlot, x0, y0, x1, y1, canvasX, errorLowerY, canvasX, errorUpperY)

		else:
			raise RuntimeException()

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['size', '%s' % item.size()])
			StatisticsData.append(['dimension', '%s' % item.dimension()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, markerStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotFunction2D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		zAxisStyle = plotterStyle.zAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		if self._needInitialize(options):
			if self._getUnderRescaling():
				bestLowerX, bestUpperX = self._getAxisValueRangeX()
				bestLowerY, bestUpperY = self._getAxisValueRangeY()
				bestLowerZ, bestUpperZ = self._getAxisValueRangeZ()
			else:
				### X range.
				if options.has_key('minX'):
					bestLowerX = float(options['minX'])
				elif self._getXLimits()[0] != None:
					bestLowerX = self._getXLimits()[0]
				else:
					bestLowerX = -10.0
				if options.has_key('maxX'):
					bestUpperX = float(options['maxX'])
				elif self._getXLimits()[1] != None:
					bestUpperX = self._getXLimits()[1]
				else:
					bestUpperX = 10.0

				### Y range.
				if options.has_key('minY'):
					bestLowerY = float(options['minY'])
				elif self._getYLimits()[0] != None:
					bestLowerY = self._getYLimits()[0]
				else:
					bestLowerY = -10.0
				if options.has_key('maxY'):
					bestUpperY = float(options['maxY'])
				elif self._getYLimits()[1] != None:
					bestUpperY = self._getYLimits()[1]
				else:
					bestUpperY = 10.0

				### Z range.
				if options.has_key('minZ'):
					bestLowerZ = float(options['minZ'])
				elif self._getZLimits()[0] != None:
					bestLowerZ = self._getZLimits()[0]
				else:
					bestLowerZ = -10.0
				if options.has_key('maxZ'):
					bestUpperZ = float(options['maxZ'])
				elif self._getZLimits()[1] != None:
					bestUpperZ = self._getZLimits()[1]
				else:
					bestUpperZ = 10.0

			### Create axis box.
			self._createAxisBox3D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, bestLowerZ, bestUpperZ, plotterStyle)

		if self._getUnderRescaling():
			return

		(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
		scalingX = self._getScalingX()
		scalingY = self._getScalingY()
		scalingZ = self._getScalingZ()
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		lowerZ, upperZ = self._getAxisValueRangeZ()
		tickLowerX, tickUpperX, mainTicksX, subTicksX = self._getTickSettingsX()
		tickLowerY, tickUpperY, mainTicksY, subTicksY = self._getTickSettingsY()
		tickLowerZ, tickUpperZ, mainTicksZ, subTicksZ = self._getTickSettingsZ()
		ticksX = []
		ticksY = []
		ticksZ = []
		if scalingX in ['log', 'logarithmic']:
			for tickX in mainTicksX:
				ticksX.append(10.0**tickX)
			for tickX in subTicksX:
				ticksX.append(10.0**tickX)
		else:
			ticksX.extend(mainTicksX)
			ticksX.extend(subTicksX)
		if scalingY in ['log', 'logarithmic']:
			for tickY in mainTicksY:
				ticksY.append(10.0**tickY)
			for tickY in subTicksY:
				ticksY.append(10.0**tickY)
		else:
			ticksY.extend(mainTicksY)
			ticksY.extend(subTicksY)
		if scalingZ in ['log', 'logarithmic']:
			for tickZ in mainTicksZ:
				ticksZ.append(10.0**tickZ)
			for tickZ in subTicksZ:
				ticksZ.append(10.0**tickZ)
		else:
			ticksZ.extend(mainTicksZ)
			ticksZ.extend(subTicksZ)
		ticksX.sort()
		ticksY.sort()
		ticksZ.sort()

		if options.has_key('minX'):
			bestLowerX = float(options['minX'])
		else:
			bestLowerX = lowerX
		if options.has_key('maxX'):
			bestUpperX = float(options['maxX'])
		else:
			bestUpperX = upperX
		if options.has_key('minY'):
			bestLowerY = float(options['minY'])
		else:
			bestLowerY = lowerY
		if options.has_key('maxY'):
			bestUpperY = float(options['maxY'])
		else:
			bestUpperY = upperY

		valueLenghtX = bestUpperX - bestLowerX
		valueLenghtY = bestUpperY - bestLowerY
		pointLengthX = x1 - x0
		pointLengthY = y1 - y0
		valueXList = []
		valueYList = []
		for i in range(pointLengthX + 1):
			valueXList.append(bestLowerX + valueLenghtX * i / pointLengthX)
		for i in range(pointLengthY + 1):
			valueYList.append(bestLowerY + valueLenghtY * i / pointLengthY)

		if cXy > 0.0:
			valueXList.reverse()
			ticksX.reverse()
		valueYList.reverse()
		ticksY.reverse()

		if lineStyle._getCustomized('color'):
			colorFlag = False
		else:
			colorFlag = True
			self._drawColorZAxis()

		### Plot.
		ratioFuncLowerX = self._3DConvertToRatio(scalingX, lowerX, upperX, bestLowerX)
		ratioFuncUpperX = self._3DConvertToRatio(scalingX, lowerX, upperX, bestUpperX)
		pointsList = []
		colorsList = []
		_3DConvertToRatio = self._3DConvertToRatio
		_3DConvertToCanvas = self._3DConvertToCanvas
		_convertRatioToColor = self._convertRatioToColor
		_create_styledLine = self._create_styledLine
		for tickX in ticksX:
			points = []
			colors = []
			ratioTickX = _3DConvertToRatio(scalingX, lowerX, upperX, tickX)
			if not (ratioFuncLowerX <= ratioTickX <= ratioFuncUpperX):
				continue
			for valueY in valueYList:
				height = item.value([tickX, valueY])
				ratioHeight = _3DConvertToRatio(scalingZ, lowerZ, upperZ, height)
				if 0.0 <= ratioHeight <= 1.0:
					ratioValueY = _3DConvertToRatio(scalingY, lowerY, upperY, valueY)
					pointX, pointY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioTickX, ratioValueY, ratioHeight)
					points.append(pointX)
					points.append(pointY)
					colors.append(_convertRatioToColor(ratioHeight))
				else:
					pointsList.append(points)
					colorsList.append(colors)
					points = []
					colors = []
			pointsList.append(points)
			colorsList.append(colors)
		for pointsIndex, points in enumerate(pointsList):
			if points:
				if colorFlag:
					colors = colorsList[pointsIndex]
					for i in range(1, len(colors)):
						tempPoints = points[(i - 1) * 2:(i + 1) * 2]
						tempLineStyle = lineStyle._createCopy()
						tempLineStyle.setColor(colors[i])
						_create_styledLine(tempLineStyle, tagsPlot, *tempPoints)
				else:
					_create_styledLine(lineStyle, tagsPlot, *points)

		ratioFuncLowerY = _3DConvertToRatio(scalingY, lowerY, upperY, bestLowerY)
		ratioFuncUpperY = _3DConvertToRatio(scalingY, lowerY, upperY, bestUpperY)
		pointsList = []
		colorsList = []
		for tickY in ticksY:
			points = []
			colors = []
			ratioTickY = _3DConvertToRatio(scalingY, lowerY, upperY, tickY)
			if not (ratioFuncLowerY <= ratioTickY <= ratioFuncUpperY):
				continue
			for valueX in valueXList:
				height = item.value([valueX, tickY])
				ratioHeight = _3DConvertToRatio(scalingZ, lowerZ, upperZ, height)
				if 0.0 <= ratioHeight <= 1.0:
					ratioValueX = _3DConvertToRatio(scalingX, lowerX, upperX, valueX)
					pointX, pointY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioTickY, ratioHeight)
					points.append(pointX)
					points.append(pointY)
					colors.append(_convertRatioToColor(ratioHeight))
				else:
					pointsList.append(points)
					colorsList.append(colors)
					points = []
					colors = []
			pointsList.append(points)
			colorsList.append(colors)
		for pointsIndex, points in enumerate(pointsList):
			if points:
				if colorFlag:
					colors = colorsList[pointsIndex]
					for i in range(1, len(colors)):
						tempPoints = points[(i - 1) * 2:(i + 1) * 2]
						tempLineStyle = lineStyle._createCopy()
						tempLineStyle.setColor(colors[i])
						_create_styledLine(tempLineStyle, tagsPlot, *tempPoints)
				else:
					_create_styledLine(lineStyle, tagsPlot, *points)

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['dimension', '%s' % item.dimension()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, lineStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotHistogram3D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Specific variables.
		axisX = item.xAxis()
		axisY = item.yAxis()
		axisZ = item.zAxis()

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		zAxisStyle = plotterStyle.zAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		### Parameters.
		parameterFormat = dataStyle._parameterData('histogram3DFormat')
		parameterDataPoint = dataStyle._parameterData('dataPoint')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')

		if self._needInitialize(options):
			bestLowerX, bestUpperX = self._bestRange(axisX, xAxisStyle)
			bestLowerY, bestUpperY = self._bestRange(axisY, yAxisStyle)
			bestLowerZ, bestUpperZ = self._bestRange(axisZ, zAxisStyle)
			if parameterFormat in ['box']:
				self._createAxisBox3D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, bestLowerZ, bestUpperZ, plotterStyle)
			else:
				raise RuntimeException()
		if self._getUnderRescaling():
			return

		if parameterFormat in ['box']:
			pass
		else:
			raise RuntimeException()

		scalingX = self._getScalingX()
		scalingY = self._getScalingY()
		scalingZ = self._getScalingZ()
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		lowerZ, upperZ = self._getAxisValueRangeZ()
		maxHeight = item.maxBinHeight()
		minHeight = item.minBinHeight()

		### Plot.
		if parameterFormat in ['box', 'color']:
			(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
			surfaceXYz = cXx * cYy - cYx * cXy
			surfaceYZz = cYx * cZy - cZx * cYy
			surfaceZXz = cZx * cXy - cXx * cZy
			binsX, binsY, binsZ = self._getOrderedBins3D(axisX, axisY, axisZ, surfaceXYz, surfaceYZz, surfaceZXz)

			### Minimum bin width of X axis.
			binLowerX, binUpperX = axisX._binEdges(0)
			minBinWidthX = binUpperX - binLowerX
			if axisX.isFixedBinning() == False:
				for binNumberX in binsX:
					binLowerX, binUpperX = axisX._binEdges(binNumberX)
					minBinWidthX = min(minBinWidthX, binUpperX - binLowerX)

			### Minimum bin width of Y axis.
			binLowerY, binUpperY = axisY._binEdges(0)
			minBinWidthY = binUpperY - binLowerY
			if axisY.isFixedBinning() == False:
				for binNumberY in binsY:
					binLowerY, binUpperY = axisY._binEdges(binNumberY)
					minBinWidthY = min(minBinWidthY, binUpperY - binLowerY)

			### Minimum bin width of Z axis.
			binLowerZ, binUpperZ = axisZ._binEdges(0)
			minBinWidthZ = binUpperZ - binLowerZ
			if axisZ.isFixedBinning() == False:
				for binNumberZ in binsZ:
					binLowerZ, binUpperZ = axisZ._binEdges(binNumberZ)
					minBinWidthZ = min(minBinWidthZ, binUpperZ - binLowerZ)

			### Check the max and min height.
			heightMax = item.maxBinHeight()
			heightMin = min(0.0, item.minBinHeight())
			heightSpan = heightMax - heightMin

			if fillStyle._getCustomized('color'):
				colorFlag = False
			else:
				colorFlag = True

			oneThird = 1.0 / 3.0
			_3DConvertToRatio = self._3DConvertToRatio
			_3DConvertToCanvas = self._3DConvertToCanvas
			_convertRatioToColor = self._convertRatioToColor
			_create_styledPolygon = self._create_styledPolygon
			for binNumberX in binsX:
				binLowerX, binUpperX = axisX._binEdges(binNumberX)
				dataPointX = (binLowerX + binUpperX) / 2.0
				if not (lowerX <= dataPointX <= upperX):
					continue
				for binNumberY in binsY:
					binLowerY, binUpperY = axisY._binEdges(binNumberY)
					dataPointY = (binLowerY + binUpperY) / 2.0
					if not (lowerY <= dataPointY <= upperY):
						continue
					for binNumberZ in binsZ:
						binLowerZ, binUpperZ = axisZ._binEdges(binNumberZ)
						dataPointZ = (binLowerZ + binUpperZ) / 2.0
						if not (lowerZ <= dataPointZ <= upperZ):
							continue
						height = item.binHeight(binNumberX, binNumberY, binNumberZ) - heightMin
						if height <= 0.0:
							continue

						tempFillStyle = IFillStyle()
						if colorFlag:
							colorRatio = _3DConvertToRatio(scalingZ, minHeight, maxHeight, height)
							tempColor = _convertRatioToColor(colorRatio)
							tempFillStyle.setColor(tempColor)
						else:
							tempFillStyle = fillStyle

						heightRatio = (height / heightSpan)**oneThird
						widthX = heightRatio * minBinWidthX * 0.9
						widthY = heightRatio * minBinWidthY * 0.9
						widthZ = heightRatio * minBinWidthZ * 0.9

						if widthX * widthY * widthZ != 0.0:
							ratioLowerX = _3DConvertToRatio(scalingX, lowerX, upperX, dataPointX - widthX / 2.0)
							ratioUpperX = _3DConvertToRatio(scalingX, lowerX, upperX, dataPointX + widthX / 2.0)
							ratioLowerY = _3DConvertToRatio(scalingY, lowerY, upperY, dataPointY - widthY / 2.0)
							ratioUpperY = _3DConvertToRatio(scalingY, lowerY, upperY, dataPointY + widthY / 2.0)
							ratioLowerZ = _3DConvertToRatio(scalingZ, lowerZ, upperZ, dataPointZ - widthZ / 2.0)
							ratioUpperZ = _3DConvertToRatio(scalingZ, lowerZ, upperZ, dataPointZ + widthZ / 2.0)
							point7x, point7y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioUpperY, ratioUpperZ)
							point4x, point4y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioLowerY, ratioUpperZ)
							point5x, point5y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioLowerY, ratioUpperZ)
							point6x, point6y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioUpperY, ratioUpperZ)
							point3x, point3y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioUpperY, ratioLowerZ)
							point0x, point0y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioLowerX, ratioLowerY, ratioLowerZ)
							point1x, point1y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioLowerY, ratioLowerZ)
							point2x, point2y = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioUpperX, ratioUpperY, ratioLowerZ)

							if surfaceXYz < 0.0:
								_create_styledPolygon(lineStyle, tempFillStyle, tagsPlot, point0x, point0y, point1x, point1y, point2x, point2y, point3x, point3y)
							else:
								_create_styledPolygon(lineStyle, tempFillStyle, tagsPlot, point4x, point4y, point5x, point5y, point6x, point6y, point7x, point7y)
							if surfaceYZz < 0.0:
								_create_styledPolygon(lineStyle, tempFillStyle, tagsPlot, point0x, point0y, point3x, point3y, point7x, point7y, point4x, point4y)
							else:
								_create_styledPolygon(lineStyle, tempFillStyle, tagsPlot, point1x, point1y, point2x, point2y, point6x, point6y, point5x, point5y)
							if surfaceZXz < 0.0:
								_create_styledPolygon(lineStyle, tempFillStyle, tagsPlot, point0x, point0y, point1x, point1y, point5x, point5y, point4x, point4y)
							else:
								_create_styledPolygon(lineStyle, tempFillStyle, tagsPlot, point3x, point3y, point2x, point2y, point6x, point6y, point7x, point7y)
		else:
			raise RuntimeException()

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['entries', '%s' % item.entries()])
			StatisticsData.append(['Xunder', '%s' % item.binEntriesX(axisX.UNDERFLOW_BIN)])
			StatisticsData.append(['Xover', '%s' % item.binEntriesX(axisX.OVERFLOW_BIN)])
			StatisticsData.append(['Xmean', '%f' % item.meanX()])
			StatisticsData.append(['Xrms', '%f' % item.rmsX()])
			StatisticsData.append(['Yunder', '%s' % item.binEntriesY(axisY.UNDERFLOW_BIN)])
			StatisticsData.append(['Yover', '%s' % item.binEntriesY(axisY.OVERFLOW_BIN)])
			StatisticsData.append(['Ymean', '%f' % item.meanY()])
			StatisticsData.append(['Yrms', '%f' % item.rmsY()])
			StatisticsData.append(['Zunder', '%s' % item.binEntriesZ(axisZ.UNDERFLOW_BIN)])
			StatisticsData.append(['Zover', '%s' % item.binEntriesZ(axisZ.OVERFLOW_BIN)])
			StatisticsData.append(['Zmean', '%f' % item.meanZ()])
			StatisticsData.append(['Zrms', '%f' % item.rmsZ()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, lineStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotCloud3D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		zAxisStyle = plotterStyle.zAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		### Parameters.
		parameterFormat = dataStyle._parameterData('cloud3DFormat')
		parameterDataPoint = dataStyle._parameterData('dataPoint')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')

		if parameterFormat == 'histogram':
			if options.has_key('nBinsX'):
				nBinsX = int(options['nBinsX'])
			else:
				nBinsX = 50
			if options.has_key('nBinsY'):
				nBinsY = int(options['nBinsY'])
			else:
				nBinsY = 50
			if options.has_key('nBinsZ'):
				nBinsZ = int(options['nBinsZ'])
			else:
				nBinsZ = 50
			item2 = item._getRawHistogram(nBinsX, item.lowerEdgeX(), item.upperEdgeX(), nBinsY, item.lowerEdgeY(), item.upperEdgeY(), nBinsZ, item.lowerEdgeZ(), item.upperEdgeZ())
			item.fillHistogram(item2)
			self._removeItemData(item)
			return self._plot(item2, plotterStyle, options)

		if self._needInitialize(options):
			sampleX = item.upperEdgeX() - item.lowerEdgeX()
			sampleY = item.upperEdgeY() - item.lowerEdgeY()
			sampleZ = item.upperEdgeZ() - item.lowerEdgeZ()
			bestLowerX = self._getMarginedMinus(item.lowerEdgeX(), parameterShowErrorBars, sampleX)
			bestUpperX = self._getMarginedPlus(item.upperEdgeX(), parameterShowErrorBars, sampleX)
			bestLowerY = self._getMarginedMinus(item.lowerEdgeY(), parameterShowErrorBars, sampleY)
			bestUpperY = self._getMarginedPlus(item.upperEdgeY(), parameterShowErrorBars, sampleY)
			bestLowerZ = self._getMarginedMinus(item.lowerEdgeZ(), parameterShowErrorBars, sampleZ)
			bestUpperZ = self._getMarginedPlus(item.upperEdgeZ(), parameterShowErrorBars, sampleZ)
			if parameterFormat in ['scatter']:
				self._createAxisBox3D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, bestLowerZ, bestUpperZ, plotterStyle)
			else:
				raise RuntimeException()
		if self._getUnderRescaling():
			return

		if parameterFormat in ['scatter']:
			(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
		else:
			raise RuntimeException()

		scalingX = self._getScalingX()
		scalingY = self._getScalingY()
		scalingZ = self._getScalingZ()
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		lowerZ, upperZ = self._getAxisValueRangeZ()

		### Plot.
		if parameterFormat in ['scatter']:
			_3DConvertToRatio = self._3DConvertToRatio
			_3DConvertToCanvas = self._3DConvertToCanvas
			_create_styledMarker = self._create_styledMarker
			for i in range(item.entries()):
				valueX = item.valueX(i)
				if not (lowerX <= valueX <= upperX):
					continue
				valueY = item.valueY(i)
				if not (lowerY <= valueY <= upperY):
					continue
				valueZ = item.valueZ(i)
				if not (lowerZ <= valueZ <= upperZ):
					continue
				ratioValueX = _3DConvertToRatio(scalingX, lowerX, upperX, valueX)
				ratioValueY = _3DConvertToRatio(scalingY, lowerY, upperY, valueY)
				ratioValueZ = _3DConvertToRatio(scalingZ, lowerZ, upperZ, valueZ)
				pointValueX, pointValueY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioValueY, ratioValueZ)
				_create_styledMarker(markerStyle, tagsPlot, pointValueX, pointValueY)
		else:
			raise RuntimeException()

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['entries', '%s' % item.entries()])
			StatisticsData.append(['Xmean', '%f' % item.meanX()])
			StatisticsData.append(['Xrms', '%f' % item.rmsX()])
			StatisticsData.append(['Ymean', '%f' % item.meanY()])
			StatisticsData.append(['Yrms', '%f' % item.rmsY()])
			StatisticsData.append(['Zmean', '%f' % item.meanZ()])
			StatisticsData.append(['Zrms', '%f' % item.rmsZ()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, markerStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotDataPointSet3D(self, item, plotterStyle, options):
		### Common variables.
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		tagsPlot = self._createTags(['plot'])

		### Styles.
		infoStyle = plotterStyle.infoStyle()
		xAxisStyle = plotterStyle.xAxisStyle()
		yAxisStyle = plotterStyle.yAxisStyle()
		zAxisStyle = plotterStyle.zAxisStyle()
		dataStyle = plotterStyle.dataStyle()
		lineStyle = dataStyle.lineStyle()
		fillStyle = dataStyle.fillStyle()
		markerStyle = dataStyle.markerStyle()

		### Parameters.
		parameterFormat = dataStyle._parameterData('dataPointSet3DFormat')
		parameterShowErrorBars = dataStyle._parameterData('showErrorBars')
		parameterErrorBarsColor = dataStyle._parameterData('errorBarsColor')

		if self._needInitialize(options):
			sampleX = item.upperExtent(0) - item.lowerExtent(0)
			sampleY = item.upperExtent(1) - item.lowerExtent(1)
			sampleZ = item.upperExtent(2) - item.lowerExtent(2)
			bestLowerX = self._getMarginedMinus(item.lowerExtent(0), parameterShowErrorBars, sampleX)
			bestUpperX = self._getMarginedPlus(item.upperExtent(0), parameterShowErrorBars, sampleX)
			bestLowerY = self._getMarginedMinus(item.lowerExtent(1), parameterShowErrorBars, sampleY)
			bestUpperY = self._getMarginedPlus(item.upperExtent(1), parameterShowErrorBars, sampleY)
			bestLowerZ = self._getMarginedMinus(item.lowerExtent(2), parameterShowErrorBars, sampleZ)
			bestUpperZ = self._getMarginedPlus(item.upperExtent(2), parameterShowErrorBars, sampleZ)
			if parameterFormat in ['scatter']:
				self._createAxisBox3D(bestLowerX, bestUpperX, bestLowerY, bestUpperY, bestLowerZ, bestUpperZ, plotterStyle)
			else:
				raise RuntimeException()
		if self._getUnderRescaling():
			return

		if parameterFormat in ['scatter']:
			(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
		else:
			raise RuntimeException()

		scalingX = self._getScalingX()
		scalingY = self._getScalingY()
		scalingZ = self._getScalingZ()
		lowerX, upperX = self._getAxisValueRangeX()
		lowerY, upperY = self._getAxisValueRangeY()
		lowerZ, upperZ = self._getAxisValueRangeZ()

		### Plot.
		errorLineStyle = ILineStyle()
		errorLineStyle.setColor(parameterErrorBarsColor)
		endLineHalfLength = 3 * errorLineStyle.thickness() / 2
		if parameterFormat in ['scatter']:
			_3DConvertToRatio = self._3DConvertToRatio
			_3DConvertToCanvas = self._3DConvertToCanvas
			_create_styledMarker = self._create_styledMarker
			_create_styledLine = self._create_styledLine
			for i in range(item.size()):
				pointI = item.point(i)
				measurementX = pointI.coordinate(0)
				valueX = measurementX.value()
				if not (lowerX <= valueX <= upperX):
					continue
				measurementY = pointI.coordinate(1)
				valueY = measurementY.value()
				if not (lowerY <= valueY <= upperY):
					continue
				measurementZ = pointI.coordinate(2)
				valueZ = measurementZ.value()
				if not (lowerZ <= valueZ <= upperZ):
					continue
				ratioValueX = _3DConvertToRatio(scalingX, lowerX, upperX, valueX)
				ratioValueY = _3DConvertToRatio(scalingY, lowerY, upperY, valueY)
				ratioValueZ = _3DConvertToRatio(scalingZ, lowerZ, upperZ, valueZ)
				pointValueX, pointValueY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioValueY, ratioValueZ)
				_create_styledMarker(markerStyle, tagsPlot, pointValueX, pointValueY)

				### Error bar.
				if parameterShowErrorBars == True:
					errorUpperX = valueX + measurementX.errorPlus()
					errorLowerX = valueX - measurementX.errorMinus()
					errorUpperY = valueY + measurementY.errorPlus()
					errorLowerY = valueY - measurementY.errorMinus()
					errorUpperZ = valueZ + measurementZ.errorPlus()
					errorLowerZ = valueZ - measurementZ.errorMinus()
					ratioErrorUpperX = _3DConvertToRatio(scalingX, lowerX, upperX, errorUpperX)
					ratioErrorLowerX = _3DConvertToRatio(scalingX, lowerX, upperX, errorLowerX)
					ratioErrorUpperY = _3DConvertToRatio(scalingY, lowerY, upperY, errorUpperY)
					ratioErrorLowerY = _3DConvertToRatio(scalingY, lowerY, upperY, errorLowerY)
					ratioErrorUpperZ = _3DConvertToRatio(scalingZ, lowerZ, upperZ, errorUpperZ)
					ratioErrorLowerZ = _3DConvertToRatio(scalingZ, lowerZ, upperZ, errorLowerZ)
					pointErrorUpperXX, pointErrorUpperXY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioErrorUpperX, ratioValueY, ratioValueZ)
					pointErrorLowerXX, pointErrorLowerXY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioErrorLowerX, ratioValueY, ratioValueZ)
					pointErrorUpperYX, pointErrorUpperYY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioErrorUpperY, ratioValueZ)
					pointErrorLowerYX, pointErrorLowerYY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioErrorLowerY, ratioValueZ)
					pointErrorUpperZX, pointErrorUpperZY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioValueY, ratioErrorUpperZ)
					pointErrorLowerZX, pointErrorLowerZY = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, ratioValueX, ratioValueY, ratioErrorLowerZ)
					_create_styledLine(errorLineStyle, tagsPlot, pointErrorUpperXX, pointErrorUpperXY, pointErrorLowerXX, pointErrorLowerXY)
					_create_styledLine(errorLineStyle, tagsPlot, pointErrorUpperYX, pointErrorUpperYY, pointErrorLowerYX, pointErrorLowerYY)
					_create_styledLine(errorLineStyle, tagsPlot, pointErrorUpperZX, pointErrorUpperZY, pointErrorLowerZX, pointErrorLowerZY)

		else:
			raise RuntimeException()

		### Statistics box.
		if plotterStyle._parameterData('showStatisticsBox') == True:
			StatisticsData = []
			StatisticsData.append(['size', '%s' % item.size()])
			StatisticsData.append(['dimension', '%s' % item.dimension()])
			self.info()._create_styledStatisticsBox(infoStyle, StatisticsData)
		else:
			self.info()._clear_styledStatisticsBox()

		self._plotLegendsBox(plotterStyle, item, markerStyle)
		self._plotTextsBox(plotterStyle, item)
		self._plotTitle(plotterStyle, item)

	def _plotLegendsBox(self, plotterStyle, item, targetStyle):
		infoStyle = plotterStyle.infoStyle()
		if not self.info()._getLegendCustomized():
			### Auto legends.
			if not self.info()._getLegendVeto():
				self.info()._addLegend(targetStyle, item.annotation().value('Title'))
		if plotterStyle._getCustomized('showLegendsBox'):
			if plotterStyle._parameterData('showLegendsBox'):
				self.info()._create_styledLegendsBox(infoStyle)
			else:
				self.info()._clear_styledLegendsBox()
		else:
			if self._getNItemData() > 1:
				self.info()._create_styledLegendsBox(infoStyle)

	def _plotTextsBox(self, plotterStyle, item):
		if plotterStyle._parameterData('showTextsBox') == True:
			infoStyle = plotterStyle.infoStyle()
			self.info()._create_styledTextsBox(infoStyle)
		else:
			self.info()._clear_styledTextsBox()

	def _plotTitle(self, plotterStyle, item):
		if plotterStyle._parameterData('showTitle') == True:
			titleStyle = plotterStyle.titleStyle()
			x0, x1 = self._getAxisRangeX()
			y0, y1 = self._getAxisRangeY()
			titleMargin = max(1, int(0.015 * self._getRegionLengthY()))
			self._appendTitle(item.annotation().value('Title'))
			self._createTitle(titleStyle, (x0 + x1) / 2, y0 - titleMargin)
		else:
			self._clearTitle()

	def _getFontMeasurements(self, textDataList):
		guiPlotter = self._getGuiPlotter()
		bridge = []
		guiPlotter._getFontMeasurements(textDataList, bridge)
		return bridge[0]

	def _createAxisBox2D(self, lowerX, upperX, lowerY, upperY, plotterStyle):
		tagsAxes = self._createTags(['axes'])

		axisStyleX = plotterStyle.xAxisStyle()
		axisStyleY = plotterStyle.yAxisStyle()
		axisStyleZ = plotterStyle.zAxisStyle()
		scalingX = axisStyleX._parameterData('scale')
		scalingY = axisStyleY._parameterData('scale')
		scalingZ = axisStyleZ._parameterData('scale')
		self._setScalingX(scalingX)
		self._setScalingY(scalingY)
		self._setScalingZ(scalingZ)
		axisLineStyleX = axisStyleX.lineStyle()
		axisLineStyleY = axisStyleY.lineStyle()
		axisLabelStyleX = axisStyleX.labelStyle()
		axisLabelStyleY = axisStyleY.labelStyle()
		axisTickLabelStyleX = axisStyleX.tickLabelStyle()
		axisTickLabelStyleY = axisStyleY.tickLabelStyle()

		if self._getFinalRescaling():
			lowerX, upperX = self._getAxisValueRangeX()
			lowerY, upperY = self._getAxisValueRangeY()
		else:
			### Range check.
			lowerX = float(lowerX)
			upperX = float(upperX)
			lowerY = float(lowerY)
			upperY = float(upperY)
			limitMinX, limitMaxX = self._getXLimits()
			limitMinY, limitMaxY = self._getYLimits()
			if limitMinX != None:
				if scalingX in ['log', 'logarithmic']:
					if limitMinX > 0.0:
						lowerX = limitMinX
				else:
					lowerX = limitMinX
			if limitMaxX != None:
				if scalingX in ['log', 'logarithmic']:
					if limitMaxX > 0.0:
						upperX = limitMaxX
				else:
					upperX = limitMaxX
			if limitMinY != None:
				if scalingY in ['log', 'logarithmic']:
					if limitMinY > 0.0:
						lowerY = limitMinY
				else:
					lowerY = limitMinY
			if limitMaxY != None:
				if scalingY in ['log', 'logarithmic']:
					if limitMaxY > 0.0:
						upperY = limitMaxY
				else:
					upperY = limitMaxY

			if lowerX == upperX:
				lowerX -= 5.0
				upperX += 5.0
			if lowerY == upperY:
				lowerY -= 5.0
				upperY += 5.0

			if scalingX in ['log', 'logarithmic']:
				if upperX <= 0.0:
					lowerX = 0.1
					upperX = 10.1
				elif lowerX <= 0.0:
					lowerX = 0.1
			if scalingY in ['log', 'logarithmic']:
				if upperY <= 0.0:
					lowerY = 0.1
					upperY = 10.1
				elif lowerY <= 0.0:
					lowerY = 0.1

			self._setAxisValueRangeX(lowerX, upperX)
			self._setAxisValueRangeY(lowerY, upperY)

			if self._getUnderRescaling():
				return

		### Box.
		boxLineStyle = ILineStyle()
		boxFillStyle = IFillStyle()
		boxFillStyle.setColor(plotterStyle._parameterData('backgroundColor'))
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		axisLengthX = x1 - x0
		axisLengthY = y1 - y0
		if self._isMatplotlib:
			self._getGuiPlotter().createAxes(self._serialNumber, tagsAxes, x0, y0, x1, y1)
			return
		else:
			self._create_styledRectangle(boxLineStyle, boxFillStyle, tagsAxes, x0, y0, x1, y1)

		### Axes.
		axisTypeX, tickLabelConverterX = self._getTickLabelConverter(axisStyleX._parameterData('type'), lowerX, upperX)
		axisTypeY, tickLabelConverterY = self._getTickLabelConverter(axisStyleY._parameterData('type'), lowerY, upperY)
		tickLowerX, tickUpperX, mainTicksX, subTicksX = self._getTicks(lowerX, upperX, scalingX, axisTypeX)
		tickLowerY, tickUpperY, mainTicksY, subTicksY = self._getTicks(lowerY, upperY, scalingY, axisTypeY)
		regionLengthX = self._getRegionLengthX()
		regionLengthY = self._getRegionLengthY()
		tickLengthMainX = max(6.0, 0.014 * regionLengthY)
		tickLengthMainY = max(6.0, 0.014 * regionLengthX)
		tickLengthSubX = max(4.0, 0.007 * regionLengthY)
		tickLengthSubY = max(4.0, 0.007 * regionLengthX)
		tickLabelMarginX = max(2.0, 0.005 * regionLengthY)
		tickLabelMarginY = max(2.0, 0.005 * regionLengthX)
		axisStyleGridMainX = axisStyleX._parameterData('grid')
		axisStyleGridMainY = axisStyleY._parameterData('grid')
		axisStyleGridSubX = axisStyleX._parameterData('gridSub')
		axisStyleGridSubY = axisStyleY._parameterData('gridSub')

		### Auto tick label size control for axes.
		tickLabelSizeNotCustomizedX = not axisTickLabelStyleX._getCustomized('fontSize')
		tickLabelSizeNotCustomizedY = not axisTickLabelStyleY._getCustomized('fontSize')
		labelSizeNotCustomizedX = not axisLabelStyleX._getCustomized('fontSize')
		labelSizeNotCustomizedY = not axisLabelStyleY._getCustomized('fontSize')
		axisLabelX = axisStyleX._parameterData('label')
		axisLabelY = axisStyleY._parameterData('label')
		textDataList = []
		textDataList.append([axisTickLabelStyleX, '10'])
		textDataList.append([axisTickLabelStyleX, str(tickLabelConverterX(mainTicksX[0]))])
		textDataList.append([axisTickLabelStyleX, str(tickLabelConverterX(mainTicksX[-1]))])
		textDataList.append([axisTickLabelStyleY, '10'])
		textDataList.append([axisTickLabelStyleY, str(tickLabelConverterY(mainTicksY[0]))])
		textDataList.append([axisTickLabelStyleY, str(tickLabelConverterY(mainTicksY[-1]))])
		textDataList.append([axisLabelStyleX, axisLabelX])
		textDataList.append([axisLabelStyleY, axisLabelY])
		fontMeasurements = self._getFontMeasurements(textDataList)

		### Auto tick label size control for x axis.
		if scalingX in ['lin', 'linear']:
			tickLabelLengthTickMinX = fontMeasurements[1][0]
			tickLabelLengthTickMaxX = fontMeasurements[2][0]
			maxTickLabelHeightX = fontMeasurements[2][1]
		elif scalingX in ['log', 'logarithmic']:
			tickLabelLengthTickMinX = fontMeasurements[1][0] * 0.9 + fontMeasurements[0][0]
			tickLabelLengthTickMaxX = fontMeasurements[2][0] * 0.9 + fontMeasurements[0][0]
			maxTickLabelHeightX = fontMeasurements[2][1] * 0.9 * 0.4 + fontMeasurements[0][1]
		canvasMin = self._convertToCanvasX(tickLowerX, tickUpperX, mainTicksX[0])
		canvasMax = self._convertToCanvasX(tickLowerX, tickUpperX, mainTicksX[-1])
		maxTickLabelLengthX = max(tickLabelLengthTickMinX, tickLabelLengthTickMaxX)
		if tickLabelSizeNotCustomizedX:
			### Width.
			tickLabelSizeX = axisTickLabelStyleX.fontSize()
			tickLabelSpace = canvasMax - canvasMin + (tickLabelLengthTickMinX + tickLabelLengthTickMaxX) / 2.0
			tickLabelFactor = tickLabelSpace / ((maxTickLabelLengthX + 3.0) * len(mainTicksX))
			if tickLabelFactor < 1.0:
				tickLabelSizeX *= tickLabelFactor
				maxTickLabelLengthX *= tickLabelFactor
				tickLabelLengthTickMinX *= tickLabelFactor
				tickLabelLengthTickMaxX *= tickLabelFactor
				maxTickLabelHeightX *= tickLabelFactor
			### Left.
			tickLabelSpace = x0 - self._getRegionRangeX()[0]
			tickLabelFactor = tickLabelSpace / (tickLabelLengthTickMinX * 0.55)
			if tickLabelFactor < 1.0:
				tickLabelSizeX *= tickLabelFactor
				maxTickLabelLengthX *= tickLabelFactor
				tickLabelLengthTickMinX *= tickLabelFactor
				tickLabelLengthTickMaxX *= tickLabelFactor
				maxTickLabelHeightX *= tickLabelFactor
			### Right.
			tickLabelSpace = self._getRegionRangeX()[1] - x1
			tickLabelFactor = tickLabelSpace / (tickLabelLengthTickMaxX * 0.55)
			if tickLabelFactor < 1.0:
				tickLabelSizeX *= tickLabelFactor
				maxTickLabelLengthX *= tickLabelFactor
				tickLabelLengthTickMinX *= tickLabelFactor
				tickLabelLengthTickMaxX *= tickLabelFactor
				maxTickLabelHeightX *= tickLabelFactor
			### Bottom.
			tickLabelSpace = self._getRegionRangeY()[1] - y1
			tickLabelFactor = tickLabelSpace / (maxTickLabelHeightX + 2.0)
			if tickLabelFactor < 1.0:
				tickLabelSizeX *= tickLabelFactor
				maxTickLabelLengthX *= tickLabelFactor
				tickLabelLengthTickMinX *= tickLabelFactor
				tickLabelLengthTickMaxX *= tickLabelFactor
				maxTickLabelHeightX *= tickLabelFactor
			axisTickLabelStyleX.setFontSize(tickLabelSizeX)

		### Auto tick label size control for y axis.
		if scalingY in ['lin', 'linear']:
			tickLabelLengthTickMinY = fontMeasurements[4][0]
			tickLabelLengthTickMaxY = fontMeasurements[5][0]
			maxTickLabelHeightY = fontMeasurements[5][1]
		elif scalingY in ['log', 'logarithmic']:
			tickLabelLengthTickMinY = fontMeasurements[4][0] * 0.9 + fontMeasurements[3][0]
			tickLabelLengthTickMaxY = fontMeasurements[5][0] * 0.9 + fontMeasurements[3][0]
			maxTickLabelHeightY = fontMeasurements[5][1] * 0.9 * 0.4 + fontMeasurements[3][1]
		maxTickLabelLengthY = max(tickLabelLengthTickMinY, tickLabelLengthTickMaxY)
		if tickLabelSizeNotCustomizedY:
			### Width.
			tickLabelSizeY = axisTickLabelStyleY.fontSize()
			tickLabelSpace = x0 - self._getRegionRangeX()[0] - tickLengthMainY - tickLabelMarginY
			tickLabelFactor = tickLabelSpace / (maxTickLabelLengthY + 3.0)
			if tickLabelFactor < 1.0:
				tickLabelSizeY *= tickLabelFactor
				maxTickLabelLengthY *= tickLabelFactor
				maxTickLabelHeightY *= tickLabelFactor
			### Height.
			canvasMin = self._convertToCanvasY(tickLowerY, tickUpperY, mainTicksY[-1])
			canvasMax = self._convertToCanvasY(tickLowerY, tickUpperY, mainTicksY[0])
			tickLabelSpace = canvasMax - canvasMin + maxTickLabelHeightY
			tickLabelFactor = tickLabelSpace / (maxTickLabelHeightY * len(mainTicksY))
			if tickLabelFactor < 1.0:
				tickLabelSizeY *= tickLabelFactor
				maxTickLabelLengthY *= tickLabelFactor
				maxTickLabelHeightY *= tickLabelFactor
			axisTickLabelStyleY.setFontSize(tickLabelSizeY)

		### Auto label.
		axisLabelMarginX = int(tickLengthMainX + tickLabelMarginX + maxTickLabelHeightX + 1)
		axisLabelMarginY = max(2, int(0.005 * regionLengthY))
		labelXSize = axisLabelStyleX.fontSize()
		labelXLength = max(1, fontMeasurements[6][0])
		labelXHeight = max(1, fontMeasurements[6][1])
		if labelSizeNotCustomizedX:
			### Width.
			labelFactor = (self._getRegionRangeX()[1] - 3.0 - (x1 - axisLengthX / 2.0)) / labelXLength
			if labelFactor < 1.0:
				labelXSize *= labelFactor
				labelXLength *= labelFactor
				labelXHeight *= labelFactor
			### Height.
			labelFactor = (self._getRegionRangeY()[1] - y1 - axisLabelMarginX - 1.0) / labelXHeight
			if labelFactor < 1.0:
				labelXSize *= labelFactor
				labelXLength *= labelFactor
				labelXHeight *= labelFactor
			axisLabelStyleX.setFontSize(labelXSize)
		labelYSize = axisLabelStyleY.fontSize()
		labelYLength = max(1, fontMeasurements[7][0])
		labelYHeight = max(1, fontMeasurements[7][1])
		if labelSizeNotCustomizedY:
			### Width.
			labelFactor = (x0 + axisLengthX * 0.1 - self._getRegionRangeX()[0]) / (labelYLength + 3.0)
			if labelFactor < 1.0:
				labelYSize *= labelFactor
				labelYLength *= labelFactor
				labelYHeight *= labelFactor
			### Height.
			labelFactor = (y0 - self._getRegionRangeY()[0] - axisLabelMarginY - 1.0) / labelYHeight
			if labelFactor < 1.0:
				labelYSize *= labelFactor
				labelYLength *= labelFactor
				labelYHeight *= labelFactor
			axisLabelStyleY.setFontSize(labelYSize)
		if labelSizeNotCustomizedX and labelSizeNotCustomizedY:
			labelSize = min(labelXSize, labelYSize)
			axisLabelStyleX.setFontSize(labelSize)
			axisLabelStyleY.setFontSize(labelSize)

		### Labels for x.
		gridLineStyleX = axisLineStyleX._createCopy()
		gridLineStyleX.setLineType('dot')
		tickLineStyle = axisStyleX._parameterData('tickLine')
		for tickX in mainTicksX:
			tickCanvasX = self._convertToCanvasX(tickLowerX, tickUpperX, tickX)
			if tickLineStyle in ['in', 'both']:
				self._create_styledLine(axisLineStyleX, tagsAxes, tickCanvasX, y1, tickCanvasX, y1 - tickLengthMainX / 2.0)
			if tickLineStyle in ['out', 'both']:
				self._create_styledLine(axisLineStyleX, tagsAxes, tickCanvasX, y1, tickCanvasX, y1 + tickLengthMainX / 2.0)
			if scalingX in ['log', 'logarithmic']:
				self._create_styledExponent(axisTickLabelStyleX, tagsAxes, tickCanvasX, y1 + tickLengthMainX + tickLabelMarginX, '10', '%s' % tickLabelConverterX(tickX), N, fontRatio = 0.9, overOffsetRatio = 0.4)
			elif scalingX in ['lin', 'linear']:
				self._create_styledText(axisTickLabelStyleX, tagsAxes, tickCanvasX, y1 + tickLengthMainX + tickLabelMarginX, '%s' % tickLabelConverterX(tickX), N)
			### Grid lines.
			if (axisStyleGridMainX == True) and (tickX != tickLowerX) and (tickX != tickUpperX):
				self._create_styledLine(gridLineStyleX, tagsAxes, tickCanvasX, y0, tickCanvasX, y1)
		for tickX in subTicksX:
			tickCanvasX = self._convertToCanvasX(tickLowerX, tickUpperX, tickX)
			if tickLineStyle in ['in', 'both']:
				self._create_styledLine(axisLineStyleX, tagsAxes, tickCanvasX, y1, tickCanvasX, y1 - tickLengthSubX / 2.0)
			if tickLineStyle in ['out', 'both']:
				self._create_styledLine(axisLineStyleX, tagsAxes, tickCanvasX, y1, tickCanvasX, y1 + tickLengthSubX / 2.0)
			### Grid lines.
			if (axisStyleGridSubX == True) and (tickX != tickLowerX) and (tickX != tickUpperX):
				self._create_styledLine(gridLineStyleX, tagsAxes, tickCanvasX, y0, tickCanvasX, y1)
		if axisLabelX != '':
			if labelXLength / 2.0 > (self._getRegionRangeX()[1] - 3.0 - x1):
				x = self._getRegionRangeX()[1] - 3.0
				anchor = NE
			else:
				x = x1
				anchor = N
			self._create_styledText(axisLabelStyleX, tagsAxes, x, y1 + axisLabelMarginX, axisLabelX, anchor)

		### Labels for y.
		gridLineStyleY = axisLineStyleY._createCopy()
		gridLineStyleY.setLineType('dot')
		tickLineStyle = axisStyleY._parameterData('tickLine')
		for tickY in mainTicksY:
			tickCanvasY = self._convertToCanvasY(tickLowerY, tickUpperY, tickY)
			if tickLineStyle in ['in', 'both']:
				self._create_styledLine(axisLineStyleY, tagsAxes, x0, tickCanvasY, x0 + tickLengthMainY / 2.0, tickCanvasY)
			if tickLineStyle in ['out', 'both']:
				self._create_styledLine(axisLineStyleY, tagsAxes, x0, tickCanvasY, x0 - tickLengthMainY / 2.0, tickCanvasY)
			if scalingY in ['log', 'logarithmic']:
				self._create_styledExponent(axisTickLabelStyleY, tagsAxes, x0 - tickLengthMainY - tickLabelMarginY, tickCanvasY, '10', '%s' % tickLabelConverterY(tickY), E, fontRatio = 0.9, overOffsetRatio = 0.4)
			elif scalingY in ['lin', 'linear']:
				self._create_styledText(axisTickLabelStyleY, tagsAxes, x0 - tickLengthMainY - tickLabelMarginY, tickCanvasY, '%s' % tickLabelConverterY(tickY), E)
			### Grid lines.
			if (axisStyleGridMainY == True) and (tickY != tickLowerY) and (tickY != tickUpperY):
				self._create_styledLine(gridLineStyleY, tagsAxes, x0, tickCanvasY, x1, tickCanvasY)
		for tickY in subTicksY:
			tickCanvasY = self._convertToCanvasY(tickLowerY, tickUpperY, tickY)
			if tickLineStyle in ['in', 'both']:
				self._create_styledLine(axisLineStyleY, tagsAxes, x0, tickCanvasY, x0 + tickLengthSubY / 2.0, tickCanvasY)
			if tickLineStyle in ['out', 'both']:
				self._create_styledLine(axisLineStyleY, tagsAxes, x0, tickCanvasY, x0 - tickLengthSubY / 2.0, tickCanvasY)
			### Grid lines.
			if (axisStyleGridSubY == True) and (tickY != tickLowerY) and (tickY != tickUpperY):
				self._create_styledLine(gridLineStyleY, tagsAxes, x0, tickCanvasY, x1, tickCanvasY)
		if axisLabelY != '':
			if labelYLength / 2.0 > axisLengthX * 0.1:
				x = x0 + axisLengthX * 0.1
				anchor = SE
			else:
				x = x0
				anchor = S
			self._create_styledText(axisLabelStyleY, tagsAxes, x, y0 - axisLabelMarginY, axisLabelY, anchor)

	def _createAxisBox3D(self, lowerX, upperX, lowerY, upperY, lowerZ, upperZ, plotterStyle, ratio = None, rotation = None):
		tagsAxes = self._createTags(['axes'])

		axisStyleX = plotterStyle.xAxisStyle()
		axisStyleY = plotterStyle.yAxisStyle()
		axisStyleZ = plotterStyle.zAxisStyle()
		scalingX = axisStyleX._parameterData('scale')
		scalingY = axisStyleY._parameterData('scale')
		scalingZ = axisStyleZ._parameterData('scale')
		self._setScalingX(scalingX)
		self._setScalingY(scalingY)
		self._setScalingZ(scalingZ)
		axisLineStyleX = axisStyleX.lineStyle()
		axisLineStyleY = axisStyleY.lineStyle()
		axisLineStyleZ = axisStyleZ.lineStyle()
		axisLabelStyleX = axisStyleX.labelStyle()
		axisLabelStyleY = axisStyleY.labelStyle()
		axisLabelStyleZ = axisStyleZ.labelStyle()
		axisTickLabelStyleX = axisStyleX.tickLabelStyle()
		axisTickLabelStyleY = axisStyleY.tickLabelStyle()
		axisTickLabelStyleZ = axisStyleZ.tickLabelStyle()

		if self._getFinalRescaling():
			lowerX, upperX = self._getAxisValueRangeX()
			lowerY, upperY = self._getAxisValueRangeY()
			lowerZ, upperZ = self._getAxisValueRangeZ()
		else:
			### Range check.
			lowerX = float(lowerX)
			upperX = float(upperX)
			lowerY = float(lowerY)
			upperY = float(upperY)
			lowerZ = float(lowerZ)
			upperZ = float(upperZ)
			limitMinX, limitMaxX = self._getXLimits()
			limitMinY, limitMaxY = self._getYLimits()
			limitMinZ, limitMaxZ = self._getZLimits()
			if limitMinX != None:
				if scalingX in ['log', 'logarithmic']:
					if limitMinX > 0.0:
						lowerX = limitMinX
				else:
					lowerX = limitMinX
			if limitMaxX != None:
				if scalingX in ['log', 'logarithmic']:
					if limitMaxX > 0.0:
						upperX = limitMaxX
				else:
					upperX = limitMaxX
			if limitMinY != None:
				if scalingY in ['log', 'logarithmic']:
					if limitMinY > 0.0:
						lowerY = limitMinY
				else:
					lowerY = limitMinY
			if limitMaxY != None:
				if scalingY in ['log', 'logarithmic']:
					if limitMaxY > 0.0:
						upperY = limitMaxY
				else:
					upperY = limitMaxY
			if limitMinZ != None:
				if scalingZ in ['log', 'logarithmic']:
					if limitMinZ > 0.0:
						lowerZ = limitMinZ
				else:
					lowerZ = limitMinZ
			if limitMaxZ != None:
				if scalingZ in ['log', 'logarithmic']:
					if limitMaxZ > 0.0:
						upperZ = limitMaxZ
				else:
					upperZ = limitMaxZ

			if lowerX == upperX:
				lowerX -= 5.0
				upperX += 5.0
			if lowerY == upperY:
				lowerY -= 5.0
				upperY += 5.0
			if lowerZ == upperZ:
				lowerZ -= 5.0
				upperZ += 5.0

			if scalingX in ['log', 'logarithmic']:
				if upperX <= 0.0:
					lowerX = 0.1
					upperX = 10.1
				elif lowerX <= 0.0:
					lowerX = 0.1
			if scalingY in ['log', 'logarithmic']:
				if upperY <= 0.0:
					lowerY = 0.1
					upperY = 10.1
				elif lowerY <= 0.0:
					lowerY = 0.1
			if scalingZ in ['log', 'logarithmic']:
				if upperZ <= 0.0:
					lowerZ = 0.1
					upperZ = 10.1
				elif lowerZ <= 0.0:
					lowerZ = 0.1

			self._setAxisValueRangeX(lowerX, upperX)
			self._setAxisValueRangeY(lowerY, upperY)
			self._setAxisValueRangeZ(lowerZ, upperZ)

			if self._getUnderRescaling():
				return

		### Box.
		boxLineStyle = ILineStyle()
		boxFillStyle = IFillStyle()
		boxFillStyle.setColor(plotterStyle._parameterData('backgroundColor'))
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		axisLengthX = x1 - x0
		axisLengthY = y1 - y0

		### Default plotting angle?
		if plotterStyle._getCustomized('rotationAxis'):
			if plotterStyle._getCustomized('rotationRatio'):
				rotationMode = ['rotationRatio', plotterStyle._parameterData('rotationRatio')]
			else:
				rotationMode = ['rotationAxis', plotterStyle._parameterData('rotationAxis')]
		else:
			if plotterStyle._getCustomized('rotationRatio'):
				rotationMode = ['rotationRatio', plotterStyle._parameterData('rotationRatio')]
			else:
				rotationMode = ['rotationRatio', plotterStyle._parameterData('rotationRatio')]

		if rotationMode[0] == 'rotationRatio':
			ratioXyYy, ratioXyZy = rotationMode[1]
			self._setAxisBox3DLayoutByRatio(ratioXyYy, ratioXyZy)
			[x, y, z] = self._get3DRotationVector()
			R = x * z / y
			R2 = R**2
			cosR = (R2 - 1.0) / (R2 + 1.0)
			sinR = 2.0 * R / (R2 + 1.0)
			square = False
		elif rotationMode[0] == 'rotationAxis':
			rotationArgs = rotationMode[1]
			if len(rotationArgs) == 4:
				[_x, _y, _z, angle] = rotationArgs
				square = False
			elif len(rotationArgs) == 5:
				[_x, _y, _z, angle, square] = rotationArgs
				if square != True:
					square = False
			else:
				raise RuntimeError('%s' % rotationArgs)
			### Set counterclockwise
			angle *= -1
			_length = sqrt(_x**2 + _y**2 + _z**2)
			x = _x / _length
			y = _y / _length
			z = sqrt(1.0 - x**2 - y**2)
			self._set3DRotationVector([x, y, z])
			cosR = cos(angle)
			sinR = sin(angle)
		else:
			raise RuntimeError('RotationMode was not determined.')

		### Rotation around (x, y, z) direction
		cosR1 = 1.0 - cosR
		Xx = x * x * cosR1 + cosR
		Xy = x * y * cosR1 - z * sinR
		Xz = x * z * cosR1 + y * sinR
		Yx = y * x * cosR1 + z * sinR
		Yy = y * y * cosR1 + cosR
		Yz = y * z * cosR1 - x * sinR
		Zx = z * x * cosR1 - y * sinR
		Zy = z * y * cosR1 + x * sinR
		Zz = z * z * cosR1 + cosR

		if (rotationMode[0] == 'rotationRatio') and (Zy < 0):
			flagZy = True
			Zx *= -1
			Zy *= -1
			Zz *= -1
		else:
			flagZy = False

		Vx = matrix([Xx, Xy, Xz])
		Vy = matrix([Yx, Yy, Yz])
		Vz = matrix([Zx, Zy, Zz])
		V06 = Vx + Vy + Vz
		V17 = Vy + Vz - Vx
		V24 = Vz - Vx - Vy
		V35 = Vx + Vz - Vy

		### V06 zero point
		zeroX06 = 0.0
		zeroY06 = 0.0
		### V17 zero point
		if V17[0] >= 0.0:
			zeroX17 = fabs(Xx / V17[0])
		else:
			zeroX17 = 1.0 - fabs(Xx / V17[0])
		if V17[1] >= 0.0:
			zeroY17 = fabs(Xy / V17[1])
		else:
			zeroY17 = 1.0 - fabs(Xy / V17[1])
		### V24 zero point
		if V24[0] >= 0.0:
			zeroX24 = 1.0 - fabs(Zx / V24[0])
		else:
			zeroX24 = fabs(Zx / V24[0])
		if V24[1] >= 0.0:
			zeroY24 = 1.0 - fabs(Zy / V24[1])
		else:
			zeroY24 = fabs(Zy / V24[1])
		### V35 zero point
		if V35[0] >= 0.0:
			zeroX35 = fabs(Yx / V35[0])
		else:
			zeroX35 = 1.0 - fabs(Yx / V35[0])
		if V35[1] >= 0.0:
			zeroY35 = fabs(Yy / V35[1])
		else:
			zeroY35 = 1.0 - fabs(Yy / V35[1])

		### Check width and height
		maxW = 0.0
		maxH = 0.0
		for (vector, zeroXab, zeroYab) in [(V06, zeroX06, zeroY06), (V17, zeroX17, zeroY17), (V24, zeroX24, zeroY24), (V35, zeroX35, zeroY35)]:
			if maxW < fabs(vector[0]):
				maxW = fabs(vector[0])
				zeroX = zeroXab
			if maxH < fabs(vector[1]):
				maxH = fabs(vector[1])
				zeroY = zeroYab
		if square:
			coefficientX = min(axisLengthX / maxW, axisLengthY / maxH)
			coefficientY = coefficientX
			coefficientZ = coefficientX
		else:
			coefficientX = axisLengthX / maxW
			coefficientY = axisLengthY / maxH
			coefficientZ = min(coefficientX, coefficientY)

		absXx = fabs(Xx)
		absXy = fabs(Xy)
		absYx = fabs(Yx)
		absYy = fabs(Yy)
		absZx = fabs(Zx)
		absZy = fabs(Zy)

		cXx = coefficientX * Xx
		cXy = coefficientY * Xy
		cXz = coefficientZ * Xz
		cYx = coefficientX * Yx
		cYy = coefficientY * Yy
		cYz = coefficientZ * Yz
		cZx = coefficientX * Zx
		cZy = coefficientY * Zy
		cZz = coefficientZ * Zz
		cZeroX = coefficientX * maxW * zeroX
		cZeroY = coefficientY * maxH * zeroY

		### Zero point is the center of the region
		p0x = (x0 + x1) / 2.0 - coefficientX * maxW / 2.0 + cZeroX
		p0y = (y0 + y1) / 2.0 + coefficientY * maxH / 2.0 - cZeroY
		p0z = 0.0

		p1x = p0x + cXx
		p1y = p0y - cXy
		p1z = p0z + cXz
		p2x = p1x + cYx
		p2y = p1y - cYy
		p2z = p1z + cYz
		p3x = p0x + cYx
		p3y = p0y - cYy
		p3z = p0z + cYz
		p4x = p0x + cZx
		p4y = p0y - cZy
		p4z = p0z + cZz
		p5x = p1x + cZx
		p5y = p1y - cZy
		p5z = p1z + cZz
		p6x = p2x + cZx
		p6y = p2y - cZy
		p6z = p2z + cZz
		p7x = p3x + cZx
		p7y = p3y - cZy
		p7z = p3z + cZz

		### Determine axes
		_create_styledPolygon = self._create_styledPolygon
		### x
		middle01x = (p0x + p1x) / 2.0
		middle01y = (p0y + p1y) / 2.0
		middle32x = (p3x + p2x) / 2.0
		middle32y = (p3y + p2y) / 2.0
		middle76x = (p7x + p6x) / 2.0
		middle76y = (p7y + p6y) / 2.0
		middle45x = (p4x + p5x) / 2.0
		middle45y = (p4y + p5y) / 2.0
		### y
		middle03x = (p0x + p3x) / 2.0
		middle03y = (p0y + p3y) / 2.0
		middle47x = (p4x + p7x) / 2.0
		middle47y = (p4y + p7y) / 2.0
		middle56x = (p5x + p6x) / 2.0
		middle56y = (p5y + p6y) / 2.0
		middle12x = (p1x + p2x) / 2.0
		middle12y = (p1y + p2y) / 2.0
		### z
		middle04x = (p0x + p4x) / 2.0
		middle04y = (p0y + p4y) / 2.0
		middle15x = (p1x + p5x) / 2.0
		middle15y = (p1y + p5y) / 2.0
		middle26x = (p2x + p6x) / 2.0
		middle26y = (p2y + p6y) / 2.0
		middle37x = (p3x + p7x) / 2.0
		middle37y = (p3y + p7y) / 2.0
		### Diagonal distance on x-y plane
		length06 = (p6x - p0x)**2 + (p6y - p0y)**2
		length17 = (p7x - p1x)**2 + (p7y - p1y)**2
		length24 = (p4x - p2x)**2 + (p4y - p2y)**2
		length35 = (p5x - p3x)**2 + (p5y - p3y)**2
		### Axis candidates
		axisPoints = []
		axisLSideCandidates = []
		axisRSideCandidates = []
		axisXCandidates = []
		axisYCandidates = []
		axisZCandidates = []
		lengthList = [length06, length17, length24, length35]
		lengthMin = min(lengthList)
		### Hexagonal shape
		lengthIndex = lengthList.index(lengthMin)
		if lengthIndex == 0:
			### exclude 06
			if flagZy:
				if p0z < p6z:
					flag = False
				else:
					flag = True
			else:
				if p0z < p6z:
					flag = True
				else:
					flag = False
			if flag:
				axisPoints.append(([p3x, p3y, p2x, p2y], [p3x - p0x, p3y - p0y, p3z - p0z]))
				axisPoints.append(([p4x, p4y, p5x, p5y], [p4x - p0x, p4y - p0y, p4z - p0z]))
				axisPoints.append(([p4x, p4y, p7x, p7y], [p4x - p0x, p4y - p0y, p4z - p0z]))
				axisPoints.append(([p1x, p1y, p2x, p2y], [p1x - p0x, p1y - p0y, p1z - p0z]))
				axisPoints.append(([p1x, p1y, p5x, p5y], [p1x - p0x, p1y - p0y, p1z - p0z]))
				axisPoints.append(([p3x, p3y, p7x, p7y], [p3x - p0x, p3y - p0y, p3z - p0z]))
			else:
				axisPoints.append(([p3x, p3y, p2x, p2y], [p2x - p6x, p2y - p6y, p2z - p6z]))
				axisPoints.append(([p4x, p4y, p5x, p5y], [p5x - p6x, p5y - p6y, p5z - p6z]))
				axisPoints.append(([p4x, p4y, p7x, p7y], [p7x - p6x, p7y - p6y, p7z - p6z]))
				axisPoints.append(([p1x, p1y, p2x, p2y], [p2x - p6x, p2y - p6y, p2z - p6z]))
				axisPoints.append(([p1x, p1y, p5x, p5y], [p5x - p6x, p5y - p6y, p5z - p6z]))
				axisPoints.append(([p3x, p3y, p7x, p7y], [p7x - p6x, p7y - p6y, p7z - p6z]))

			axisLSideCandidates.append((middle32x, middle32y, 'x'))
			axisLSideCandidates.append((middle45x, middle45y, 'x'))
			axisLSideCandidates.append((middle47x, middle47y, 'y'))
			axisLSideCandidates.append((middle12x, middle12y, 'y'))
			axisLSideCandidates.append((middle15x, middle15y, 'z'))
			axisLSideCandidates.append((middle37x, middle37y, 'z'))

			axisRSideCandidates.append((-middle32y, -middle32x, 'x'))
			axisRSideCandidates.append((-middle45y, -middle45x, 'x'))
			axisRSideCandidates.append((-middle47y, -middle47x, 'y'))
			axisRSideCandidates.append((-middle12y, -middle12x, 'y'))
			axisRSideCandidates.append((-middle15y, -middle15x, 'z'))
			axisRSideCandidates.append((-middle37y, -middle37x, 'z'))

			axisXCandidates.append((-middle32y, middle32x, 'x'))
			axisXCandidates.append((-middle45y, middle45x, 'x'))
			axisYCandidates.append((-middle47y, middle47x, 'y'))
			axisYCandidates.append((-middle12y, middle12x, 'y'))
			axisZCandidates.append((-middle15y, middle15x, 'z'))
			axisZCandidates.append((-middle37y, middle37x, 'z'))
		elif lengthIndex == 1:
			### exclude 17
			if flagZy:
				if p1z < p7z:
					flag = False
				else:
					flag = True
			else:
				if p1z < p7z:
					flag = True
				else:
					flag = False
			if flag:
				axisPoints.append(([p3x, p3y, p2x, p2y], [p2x - p1x, p2y - p1y, p2z - p1z]))
				axisPoints.append(([p4x, p4y, p5x, p5y], [p5x - p1x, p5y - p1y, p5z - p1z]))
				axisPoints.append(([p0x, p0y, p3x, p3y], [p0x - p1x, p0y - p1y, p0z - p1z]))
				axisPoints.append(([p5x, p5y, p6x, p6y], [p5x - p1x, p5y - p1y, p5z - p1z]))
				axisPoints.append(([p0x, p0y, p4x, p4y], [p0x - p1x, p0y - p1y, p0z - p1z]))
				axisPoints.append(([p2x, p2y, p6x, p6y], [p2x - p1x, p2y - p1y, p2z - p1z]))
			else:
				axisPoints.append(([p3x, p3y, p2x, p2y], [p3x - p7x, p3y - p7y, p3z - p7z]))
				axisPoints.append(([p4x, p4y, p5x, p5y], [p4x - p7x, p4y - p7y, p4z - p7z]))
				axisPoints.append(([p0x, p0y, p3x, p3y], [p3x - p7x, p3y - p7y, p3z - p7z]))
				axisPoints.append(([p5x, p5y, p6x, p6y], [p6x - p7x, p6y - p7y, p6z - p7z]))
				axisPoints.append(([p0x, p0y, p4x, p4y], [p4x - p7x, p4y - p7y, p4z - p7z]))
				axisPoints.append(([p2x, p2y, p6x, p6y], [p6x - p7x, p6y - p7y, p6z - p7z]))

			axisLSideCandidates.append((middle32x, middle32y, 'x'))
			axisLSideCandidates.append((middle45x, middle45y, 'x'))
			axisLSideCandidates.append((middle03x, middle03y, 'y'))
			axisLSideCandidates.append((middle56x, middle56y, 'y'))
			axisLSideCandidates.append((middle04x, middle04y, 'z'))
			axisLSideCandidates.append((middle26x, middle26y, 'z'))

			axisRSideCandidates.append((-middle32y, -middle32x, 'x'))
			axisRSideCandidates.append((-middle45y, -middle45x, 'x'))
			axisRSideCandidates.append((-middle03y, -middle03x, 'y'))
			axisRSideCandidates.append((-middle56y, -middle56x, 'y'))
			axisRSideCandidates.append((-middle04y, -middle04x, 'z'))
			axisRSideCandidates.append((-middle26y, -middle26x, 'z'))

			axisXCandidates.append((-middle32y, middle32x, 'x'))
			axisXCandidates.append((-middle45y, middle45x, 'x'))
			axisYCandidates.append((-middle03y, middle03x, 'y'))
			axisYCandidates.append((-middle56y, middle56x, 'y'))
			axisZCandidates.append((-middle04y, middle04x, 'z'))
			axisZCandidates.append((-middle26y, middle26x, 'z'))
		elif lengthIndex == 2:
			### exclude 24
			if flagZy:
				if p2z < p4z:
					flag = False
				else:
					flag = True
			else:
				if p2z < p4z:
					flag = True
				else:
					flag = False
			if flag:
				axisPoints.append(([p0x, p0y, p1x, p1y], [p1x - p2x, p1y - p2y, p1z - p2z]))
				axisPoints.append(([p7x, p7y, p6x, p6y], [p6x - p2x, p6y - p2y, p6z - p2z]))
				axisPoints.append(([p0x, p0y, p3x, p3y], [p3x - p2x, p3y - p2y, p3z - p2z]))
				axisPoints.append(([p5x, p5y, p6x, p6y], [p6x - p2x, p6y - p2y, p6z - p2z]))
				axisPoints.append(([p1x, p1y, p5x, p5y], [p1x - p2x, p1y - p2y, p1z - p2z]))
				axisPoints.append(([p3x, p3y, p7x, p7y], [p3x - p2x, p3y - p2y, p3z - p2z]))
			else:
				axisPoints.append(([p0x, p0y, p1x, p1y], [p0x - p4x, p0y - p4y, p0z - p4z]))
				axisPoints.append(([p7x, p7y, p6x, p6y], [p7x - p4x, p7y - p4y, p7z - p4z]))
				axisPoints.append(([p0x, p0y, p3x, p3y], [p0x - p4x, p0y - p4y, p0z - p4z]))
				axisPoints.append(([p5x, p5y, p6x, p6y], [p5x - p4x, p5y - p4y, p5z - p4z]))
				axisPoints.append(([p1x, p1y, p5x, p5y], [p5x - p4x, p5y - p4y, p5z - p4z]))
				axisPoints.append(([p3x, p3y, p7x, p7y], [p7x - p4x, p7y - p4y, p7z - p4z]))

			axisLSideCandidates.append((middle01x, middle01y, 'x'))
			axisLSideCandidates.append((middle76x, middle76y, 'x'))
			axisLSideCandidates.append((middle03x, middle03y, 'y'))
			axisLSideCandidates.append((middle56x, middle56y, 'y'))
			axisLSideCandidates.append((middle15x, middle15y, 'z'))
			axisLSideCandidates.append((middle37x, middle37y, 'z'))

			axisRSideCandidates.append((-middle01y, -middle01x, 'x'))
			axisRSideCandidates.append((-middle76y, -middle76x, 'x'))
			axisRSideCandidates.append((-middle03y, -middle03x, 'y'))
			axisRSideCandidates.append((-middle56y, -middle56x, 'y'))
			axisRSideCandidates.append((-middle15y, -middle15x, 'z'))
			axisRSideCandidates.append((-middle37y, -middle37x, 'z'))

			axisXCandidates.append((-middle01y, middle01x, 'x'))
			axisXCandidates.append((-middle76y, middle76x, 'x'))
			axisYCandidates.append((-middle03y, middle03x, 'y'))
			axisYCandidates.append((-middle56y, middle56x, 'y'))
			axisZCandidates.append((-middle15y, middle15x, 'z'))
			axisZCandidates.append((-middle37y, middle37x, 'z'))
		else:
			### exclude 35
			if flagZy:
				if p3z < p5z:
					flag = False
				else:
					flag = True
			else:
				if p3z < p5z:
					flag = True
				else:
					flag = False
			if flag:
				axisPoints.append(([p0x, p0y, p1x, p1y], [p0x - p3x, p0y - p3y, p0z - p3z]))
				axisPoints.append(([p7x, p7y, p6x, p6y], [p7x - p3x, p7y - p3y, p7z - p3z]))
				axisPoints.append(([p4x, p4y, p7x, p7y], [p7x - p3x, p7y - p3y, p7z - p3z]))
				axisPoints.append(([p1x, p1y, p2x, p2y], [p2x - p3x, p2y - p3y, p2z - p3z]))
				axisPoints.append(([p0x, p0y, p4x, p4y], [p0x - p3x, p0y - p3y, p0z - p3z]))
				axisPoints.append(([p2x, p2y, p6x, p6y], [p2x - p3x, p2y - p3y, p2z - p3z]))
			else:
				axisPoints.append(([p0x, p0y, p1x, p1y], [p1x - p5x, p1y - p5y, p1z - p5z]))
				axisPoints.append(([p7x, p7y, p6x, p6y], [p6x - p5x, p6y - p5y, p6z - p5z]))
				axisPoints.append(([p4x, p4y, p7x, p7y], [p4x - p5x, p4y - p5y, p4z - p5z]))
				axisPoints.append(([p1x, p1y, p2x, p2y], [p1x - p5x, p1y - p5y, p1z - p5z]))
				axisPoints.append(([p0x, p0y, p4x, p4y], [p4x - p5x, p4y - p5y, p4z - p5z]))
				axisPoints.append(([p2x, p2y, p6x, p6y], [p6x - p5x, p6y - p5y, p6z - p5z]))

			axisLSideCandidates.append((middle01x, middle01y, 'x'))
			axisLSideCandidates.append((middle76x, middle76y, 'x'))
			axisLSideCandidates.append((middle47x, middle47y, 'y'))
			axisLSideCandidates.append((middle12x, middle12y, 'y'))
			axisLSideCandidates.append((middle04x, middle04y, 'z'))
			axisLSideCandidates.append((middle26x, middle26y, 'z'))

			axisRSideCandidates.append((-middle01y, -middle01x, 'x'))
			axisRSideCandidates.append((-middle76y, -middle76x, 'x'))
			axisRSideCandidates.append((-middle47y, -middle47x, 'y'))
			axisRSideCandidates.append((-middle12y, -middle12x, 'y'))
			axisRSideCandidates.append((-middle04y, -middle04x, 'z'))
			axisRSideCandidates.append((-middle26y, -middle26x, 'z'))

			axisXCandidates.append((-middle01y, middle01x, 'x'))
			axisXCandidates.append((-middle76y, middle76x, 'x'))
			axisYCandidates.append((-middle47y, middle47x, 'y'))
			axisYCandidates.append((-middle12y, middle12x, 'y'))
			axisZCandidates.append((-middle04y, middle04x, 'z'))
			axisZCandidates.append((-middle26y, middle26x, 'z'))

		### Determine axis
		anchors = [None] * 3
		tickLineVectors = [None] * 3
		tickVectors = [None] * 3
		axisLSideSorted = axisLSideCandidates[:]
		axisRSideSorted = axisRSideCandidates[:]
		axisLSideSorted.sort()
		axisRSideSorted.sort()

		axisPoint = axisPoints[axisLSideCandidates.index(axisLSideSorted[0])]
		length = sqrt(axisPoint[1][0]**2 + axisPoint[1][1]**2)
		if length == 0.0:
			length = 1.0
		if axisLSideSorted[0][2] == 'x':
			anchors[0] = E
			tickLineVectors[0] = [-axisPoint[1][0] / length, -axisPoint[1][1] / length]
			tickVectors[0] = tickLineVectors[0]
			axisX0x, axisX0y, axisX1x, axisX1y = axisPoint[0]
		elif axisLSideSorted[0][2] == 'y':
			anchors[1] = E
			tickLineVectors[1] = [-axisPoint[1][0] / length, -axisPoint[1][1] / length]
			tickVectors[1] = tickLineVectors[1]
			axisY0x, axisY0y, axisY1x, axisY1y = axisPoint[0]
		else:
			anchors[2] = E
			tickLineVectors[2] = [-axisPoint[1][0] / length, -axisPoint[1][1] / length]
			tickVectors[2] = tickLineVectors[2]
			axisZ0x, axisZ0y, axisZ1x, axisZ1y = axisPoint[0]

		axisXVectorX = axisPoint[0][2] - axisPoint[0][0]
		axisXVectorY = axisPoint[0][3] - axisPoint[0][1]
		axisXVectorLength = sqrt(axisXVectorX**2 + axisXVectorY**2)
		if axisXVectorLength == 0.0:
			axisXVectorLength = 1.0
		axisXVectorX /= axisXVectorLength
		axisXVectorY /= axisXVectorLength
		axisXVector = [axisXVectorX, axisXVectorY]

		axisPoint = axisPoints[axisRSideCandidates.index(axisRSideSorted[0])]
		length = sqrt(axisPoint[1][0]**2 + axisPoint[1][1]**2)
		if length == 0.0:
			length = 1.0
		if axisRSideSorted[0][2] == 'x':
			anchors[0] = NW
			tickLineVectors[0] = [-axisPoint[1][0] / length, -axisPoint[1][1] / length]
			tickVectors[0] = axisXVector
			axisX0x, axisX0y, axisX1x, axisX1y = axisPoint[0]
		elif axisRSideSorted[0][2] == 'y':
			anchors[1] = NW
			tickLineVectors[1] = [-axisPoint[1][0] / length, -axisPoint[1][1] / length]
			tickVectors[1] = axisXVector
			axisY0x, axisY0y, axisY1x, axisY1y = axisPoint[0]
		else:
			anchors[2] = NW
			tickLineVectors[2] = [-axisPoint[1][0] / length, -axisPoint[1][1] / length]
			tickVectors[2] = axisXVector
			axisZ0x, axisZ0y, axisZ1x, axisZ1y = axisPoint[0]

		axisXSorted = axisXCandidates[:]
		axisYSorted = axisYCandidates[:]
		axisZSorted = axisZCandidates[:]
		axisXSorted.sort()
		axisYSorted.sort()
		axisZSorted.sort()
		undeterminedAxis = ['x', 'y', 'z']
		undeterminedAxis.remove(axisLSideSorted[0][2])
		undeterminedAxis.remove(axisRSideSorted[0][2])
		if undeterminedAxis[0] == 'x':
			axisPoint = axisPoints[axisXCandidates.index(axisXSorted[0])]
			length = sqrt(axisPoint[1][0]**2 + axisPoint[1][1]**2)
			if length == 0.0:
				length = 1.0
			anchors[0] = NE
			tickLineVectors[0] = [-axisPoint[1][0] / length, -axisPoint[1][1] / length]
			tickVectors[0] = axisXVector
			axisX0x, axisX0y, axisX1x, axisX1y = axisPoint[0]
		elif undeterminedAxis[0] == 'y':
			axisPoint = axisPoints[axisYCandidates.index(axisYSorted[0]) + 2]
			length = sqrt(axisPoint[1][0]**2 + axisPoint[1][1]**2)
			if length == 0.0:
				length = 1.0
			anchors[1] = NE
			tickLineVectors[1] = [-axisPoint[1][0] / length, -axisPoint[1][1] / length]
			tickVectors[1] = axisXVector
			axisY0x, axisY0y, axisY1x, axisY1y = axisPoint[0]
		else:
			axisPoint = axisPoints[axisZCandidates.index(axisZSorted[0]) + 4]
			length = sqrt(axisPoint[1][0]**2 + axisPoint[1][1]**2)
			if length == 0.0:
				length = 1.0
			anchors[2] = NE
			tickLineVectors[2] = [-axisPoint[1][0] / length, -axisPoint[1][1] / length]
			tickVectors[2] = axisXVector
			axisZ0x, axisZ0y, axisZ1x, axisZ1y = axisPoint[0]

		labelVectors = [None] * 3
		labelVectors[0] = [tickVectors[0][0] + tickLineVectors[0][0], tickVectors[0][1] + tickLineVectors[0][1]]
		labelVectors[1] = [tickVectors[1][0] + tickLineVectors[1][0], tickVectors[1][1] + tickLineVectors[1][1]]
		labelVectors[2] = [tickVectors[2][0] + tickLineVectors[2][0], tickVectors[2][1] + tickLineVectors[2][1]]

		### Background surfaces and grids
		surfaceXYz = Xx * Yy - Yx * Xy
		surfaceYZz = Yx * Zy - Zx * Yy
		surfaceZXz = Zx * Xy - Xx * Zy
		if surfaceXYz >= 0.0:
			_create_styledPolygon(boxLineStyle, boxFillStyle, tagsAxes, p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y)
			gridXYx = [p0x, p0y, p1x, p1y, p3x, p3y, p2x, p2y]
			gridXYy = [p0x, p0y, p3x, p3y, p1x, p1y, p2x, p2y]
		else:
			_create_styledPolygon(boxLineStyle, boxFillStyle, tagsAxes, p4x, p4y, p5x, p5y, p6x, p6y, p7x, p7y)
			gridXYx = [p4x, p4y, p5x, p5y, p7x, p7y, p6x, p6y]
			gridXYy = [p4x, p4y, p7x, p7y, p5x, p5y, p6x, p6y]
		if surfaceYZz >= 0.0:
			_create_styledPolygon(boxLineStyle, boxFillStyle, tagsAxes, p0x, p0y, p3x, p3y, p7x, p7y, p4x, p4y)
			gridYZy = [p0x, p0y, p3x, p3y, p4x, p4y, p7x, p7y]
			gridYZz = [p0x, p0y, p4x, p4y, p3x, p3y, p7x, p7y]
		else:
			_create_styledPolygon(boxLineStyle, boxFillStyle, tagsAxes, p1x, p1y, p2x, p2y, p6x, p6y, p5x, p5y)
			gridYZy = [p1x, p1y, p2x, p2y, p5x, p5y, p6x, p6y]
			gridYZz = [p1x, p1y, p5x, p5y, p2x, p2y, p6x, p6y]
		if surfaceZXz >= 0.0:
			_create_styledPolygon(boxLineStyle, boxFillStyle, tagsAxes, p0x, p0y, p1x, p1y, p5x, p5y, p4x, p4y)
			gridZXx = [p0x, p0y, p1x, p1y, p4x, p4y, p5x, p5y]
			gridZXz = [p0x, p0y, p4x, p4y, p1x, p1y, p5x, p5y]
		else:
			_create_styledPolygon(boxLineStyle, boxFillStyle, tagsAxes, p3x, p3y, p2x, p2y, p6x, p6y, p7x, p7y)
			gridZXx = [p3x, p3y, p2x, p2y, p7x, p7y, p6x, p6y]
			gridZXz = [p3x, p3y, p7x, p7y, p2x, p2y, p6x, p6y]

		### Axes.
		_3DConvertToTickRatio = self._3DConvertToTickRatio
		_3DConvertToCanvas = self._3DConvertToCanvas
		_convertRatioToCanvas = self._convertRatioToCanvas
		_create_styledLine = self._create_styledLine
		_create_styledText = self._create_styledText
		_create_styledExponent = self._create_styledExponent
		axisTypeX, tickLabelConverterX = self._getTickLabelConverter(axisStyleX._parameterData('type'), lowerX, upperX)
		axisTypeY, tickLabelConverterY = self._getTickLabelConverter(axisStyleY._parameterData('type'), lowerY, upperY)
		axisTypeZ, tickLabelConverterZ = self._getTickLabelConverter(axisStyleZ._parameterData('type'), lowerZ, upperZ)
		tickLowerX, tickUpperX, mainTicksX, subTicksX = self._getTicks(lowerX, upperX, scalingX, axisTypeX)
		tickLowerY, tickUpperY, mainTicksY, subTicksY = self._getTicks(lowerY, upperY, scalingY, axisTypeY)
		tickLowerZ, tickUpperZ, mainTicksZ, subTicksZ = self._getTicks(lowerZ, upperZ, scalingZ, axisTypeZ)
		regionLengthX = self._getRegionLengthX()
		regionLengthY = self._getRegionLengthY()
		tickLengthMainX = max(5.0, 0.014 * regionLengthY)
		tickLengthMainY = max(5.0, 0.014 * regionLengthY)
		tickLengthMainZ = max(5.0, 0.014 * regionLengthX)
		tickLengthSubX = max(3.0, 0.007 * regionLengthY)
		tickLengthSubY = max(3.0, 0.007 * regionLengthY)
		tickLengthSubZ = max(3.0, 0.007 * regionLengthX)
		tickLabelMarginX = max(2.0, 0.005 * regionLengthY)
		tickLabelMarginY = max(2.0, 0.005 * regionLengthY)
		tickLabelMarginZ = max(2.0, 0.005 * regionLengthX)
		axisStyleGridMainX = axisStyleX._parameterData('grid')
		axisStyleGridMainY = axisStyleY._parameterData('grid')
		axisStyleGridMainZ = axisStyleZ._parameterData('grid')
		axisStyleGridSubX = axisStyleX._parameterData('gridSub')
		axisStyleGridSubY = axisStyleY._parameterData('gridSub')
		axisStyleGridSubZ = axisStyleZ._parameterData('gridSub')

		### Auto tick label size control for axes.
		tickLabelSizeNotCustomizedX = not axisTickLabelStyleX._getCustomized('fontSize')
		tickLabelSizeNotCustomizedY = not axisTickLabelStyleY._getCustomized('fontSize')
		tickLabelSizeNotCustomizedZ = not axisTickLabelStyleZ._getCustomized('fontSize')
		labelSizeNotCustomizedX = not axisLabelStyleX._getCustomized('fontSize')
		labelSizeNotCustomizedY = not axisLabelStyleY._getCustomized('fontSize')
		labelSizeNotCustomizedZ = not axisLabelStyleZ._getCustomized('fontSize')
		axisLabelX = axisStyleX._parameterData('label')
		axisLabelY = axisStyleY._parameterData('label')
		axisLabelZ = axisStyleZ._parameterData('label')
		extraLabelSpace = 3.0
		### Measurement for x
		textDataList = [[axisLabelStyleX, axisLabelX]]
		textDataList.append([axisTickLabelStyleX, '10'])
		for mainTick in mainTicksX:
			textDataList.append([axisTickLabelStyleX, str(tickLabelConverterX(mainTick))])
		fontMeasurementsX = self._getFontMeasurements(textDataList)
		### Measurement for y
		textDataList = [[axisLabelStyleY, axisLabelY]]
		textDataList.append([axisTickLabelStyleY, '10'])
		for mainTick in mainTicksY:
			textDataList.append([axisTickLabelStyleY, str(tickLabelConverterY(mainTick))])
		fontMeasurementsY = self._getFontMeasurements(textDataList)
		### Measurement for z
		textDataList = [[axisLabelStyleZ, axisLabelZ]]
		textDataList.append([axisTickLabelStyleZ, '10'])
		for mainTick in mainTicksZ:
			textDataList.append([axisTickLabelStyleZ, str(tickLabelConverterZ(mainTick))])
		fontMeasurementsZ = self._getFontMeasurements(textDataList)

		### Auto tick label size control for x axis.
		tickLabelSizeX = axisTickLabelStyleX.fontSize()
		canvasTicks = []
		for mainTick in mainTicksX:
			ratioTick = _3DConvertToTickRatio(tickLowerX, tickUpperX, mainTick)
			canvasTickX, canvasTickY = _convertRatioToCanvas(axisX0x, axisX0y, axisX1x, axisX1y, ratioTick)
			canvasTicks.append((canvasTickX, canvasTickY))
		fontResizeFactorW = 1.0
		fontResizeFactorH = 1.0
		for i, fontMeasurement in enumerate(fontMeasurementsX[2:-1]):
			if scalingX in ['lin', 'linear']:
				labelW = fontMeasurement[0]
				labelH = fontMeasurement[1]
			elif scalingX in ['log', 'logarithmic']:
				labelW = fontMeasurementsX[1][0] + fontMeasurement[0] * 0.9
				labelH = fontMeasurementsX[1][1] + fontMeasurement[1] * 0.9 * 0.4
			fontResizeFactorW = min(fontResizeFactorW, fabs(canvasTicks[i + 1][0] - canvasTicks[i][0]) / labelW)
			fontResizeFactorH = min(fontResizeFactorH, fabs(canvasTicks[i + 1][1] - canvasTicks[i][1]) / labelH)
		if scalingX in ['lin', 'linear']:
			labelW = fontMeasurementsX[-1][0]
			lavelH = fontMeasurementsX[-1][1]
		elif scalingX in ['log', 'logarithmic']:
			labelW = fontMeasurementsX[1][0] + fontMeasurementsX[-1][0] * 0.9
			lavelH = fontMeasurementsX[1][1] + fontMeasurementsX[-1][1] * 0.9 * 0.4
		fontResizeFactorW = min(fontResizeFactorW, fabs(canvasTicks[i + 1][0] - self._getRegionRangeX()[0]) / labelW)
		fontResizeFactorW = min(fontResizeFactorW, fabs(canvasTicks[i + 1][0] - self._getRegionRangeX()[1]) / labelW)
		fontResizeFactorH = min(fontResizeFactorH, fabs(canvasTicks[i + 1][1] - self._getRegionRangeY()[0]) / labelH)
		fontResizeFactorH = min(fontResizeFactorH, fabs(canvasTicks[i + 1][1] - self._getRegionRangeY()[1]) / labelH)
		if (fontResizeFactorW < 1.0) and (fontResizeFactorH < 1.0):
			tickLabelSizeX *= max(fontResizeFactorW, fontResizeFactorH)

		### Auto tick label size control for y axis.
		tickLabelSizeY = axisTickLabelStyleY.fontSize()
		canvasTicks = []
		for mainTick in mainTicksY:
			ratioTick = _3DConvertToTickRatio(tickLowerY, tickUpperY, mainTick)
			canvasTickX, canvasTickY = _convertRatioToCanvas(axisY0x, axisY0y, axisY1x, axisY1y, ratioTick)
			canvasTicks.append((canvasTickX, canvasTickY))
		fontResizeFactorW = 1.0
		fontResizeFactorH = 1.0
		for i, fontMeasurement in enumerate(fontMeasurementsY[2:-1]):
			if scalingY in ['lin', 'linear']:
				labelW = fontMeasurement[0]
				labelH = fontMeasurement[1]
			elif scalingY in ['log', 'logarithmic']:
				labelW = fontMeasurementsY[1][0] + fontMeasurement[0] * 0.9
				labelH = fontMeasurementsY[1][1] + fontMeasurement[1] * 0.9 * 0.4
			fontResizeFactorW = min(fontResizeFactorW, fabs(canvasTicks[i + 1][0] - canvasTicks[i][0]) / labelW)
			fontResizeFactorH = min(fontResizeFactorH, fabs(canvasTicks[i + 1][1] - canvasTicks[i][1]) / labelH)
		if scalingY in ['lin', 'linear']:
			labelW = fontMeasurementsY[-1][0]
			lavelH = fontMeasurementsY[-1][1]
		elif scalingY in ['log', 'logarithmic']:
			labelW = fontMeasurementsY[1][0] + fontMeasurementsY[-1][0] * 0.9
			lavelH = fontMeasurementsY[1][1] + fontMeasurementsY[-1][1] * 0.9 * 0.4
		fontResizeFactorW = min(fontResizeFactorW, fabs(canvasTicks[i + 1][0] - self._getRegionRangeX()[0]) / labelW)
		fontResizeFactorW = min(fontResizeFactorW, fabs(canvasTicks[i + 1][0] - self._getRegionRangeX()[1]) / labelW)
		fontResizeFactorH = min(fontResizeFactorH, fabs(canvasTicks[i + 1][1] - self._getRegionRangeY()[0]) / labelH)
		fontResizeFactorH = min(fontResizeFactorH, fabs(canvasTicks[i + 1][1] - self._getRegionRangeY()[1]) / labelH)
		if (fontResizeFactorW < 1.0) and (fontResizeFactorH < 1.0):
			tickLabelSizeY *= max(fontResizeFactorW, fontResizeFactorH)

		### Auto tick label size control for z axis.
		tickLabelSizeZ = axisTickLabelStyleZ.fontSize()
		canvasTicks = []
		for mainTick in mainTicksZ:
			ratioTick = _3DConvertToTickRatio(tickLowerZ, tickUpperZ, mainTick)
			canvasTickX, canvasTickY = _convertRatioToCanvas(axisZ0x, axisZ0y, axisZ1x, axisZ1y, ratioTick)
			canvasTicks.append((canvasTickX, canvasTickY))
		fontResizeFactorW = 1.0
		fontResizeFactorH = 1.0
		for i, fontMeasurement in enumerate(fontMeasurementsZ[2:-1]):
			if scalingZ in ['lin', 'linear']:
				labelW = fontMeasurement[0]
				labelH = fontMeasurement[1]
			elif scalingZ in ['log', 'logarithmic']:
				labelW = fontMeasurementsZ[1][0] + fontMeasurement[0] * 0.9
				labelH = fontMeasurementsZ[1][1] + fontMeasurement[1] * 0.9 * 0.4
			fontResizeFactorW = min(fontResizeFactorW, fabs(canvasTicks[i + 1][0] - canvasTicks[i][0]) / labelW)
			fontResizeFactorH = min(fontResizeFactorH, fabs(canvasTicks[i + 1][1] - canvasTicks[i][1]) / labelH)
		if scalingZ in ['lin', 'linear']:
			labelW = fontMeasurementsZ[-1][0]
			lavelH = fontMeasurementsZ[-1][1]
		elif scalingZ in ['log', 'logarithmic']:
			labelW = fontMeasurementsZ[1][0] + fontMeasurementsZ[-1][0] * 0.9
			lavelH = fontMeasurementsZ[1][1] + fontMeasurementsZ[-1][1] * 0.9 * 0.4
		fontResizeFactorW = min(fontResizeFactorW, fabs(canvasTicks[i + 1][0] - self._getRegionRangeX()[0]) / labelW)
		fontResizeFactorW = min(fontResizeFactorW, fabs(canvasTicks[i + 1][0] - self._getRegionRangeX()[1]) / labelW)
		fontResizeFactorH = min(fontResizeFactorH, fabs(canvasTicks[i + 1][1] - self._getRegionRangeY()[0]) / labelH)
		fontResizeFactorH = min(fontResizeFactorH, fabs(canvasTicks[i + 1][1] - self._getRegionRangeY()[1]) / labelH)
		if (fontResizeFactorW < 1.0) and (fontResizeFactorH < 1.0):
			tickLabelSizeZ *= max(fontResizeFactorW, fontResizeFactorH)

		if tickLabelSizeNotCustomizedX and tickLabelSizeNotCustomizedY and tickLabelSizeNotCustomizedZ:
			minFontSize = min(tickLabelSizeX, tickLabelSizeY, tickLabelSizeZ)
			axisTickLabelStyleX.setFontSize(minFontSize)
			axisTickLabelStyleY.setFontSize(minFontSize)
			axisTickLabelStyleZ.setFontSize(minFontSize)
		elif tickLabelSizeNotCustomizedX and tickLabelSizeNotCustomizedY:
			minFontSize = min(tickLabelSizeX, tickLabelSizeY)
			axisTickLabelStyleX.setFontSize(minFontSize)
			axisTickLabelStyleY.setFontSize(minFontSize)
		elif tickLabelSizeNotCustomizedY and tickLabelSizeNotCustomizedZ:
			minFontSize = min(tickLabelSizeY, tickLabelSizeZ)
			axisTickLabelStyleY.setFontSize(minFontSize)
			axisTickLabelStyleZ.setFontSize(minFontSize)
		elif tickLabelSizeNotCustomizedZ and tickLabelSizeNotCustomizedX:
			minFontSize = min(tickLabelSizeZ, tickLabelSizeX)
			axisTickLabelStyleZ.setFontSize(minFontSize)
			axisTickLabelStyleX.setFontSize(minFontSize)
		elif tickLabelSizeNotCustomizedX:
			axisTickLabelStyleX.setFontSize(tickLabelSizeX)
		elif tickLabelSizeNotCustomizedY:
			axisTickLabelStyleY.setFontSize(tickLabelSizeY)
		elif tickLabelSizeNotCustomizedZ:
			axisTickLabelStyleZ.setFontSize(tickLabelSizeZ)

		if labelSizeNotCustomizedX and labelSizeNotCustomizedY and labelSizeNotCustomizedZ:
			minFontSize = min(tickLabelSizeX, tickLabelSizeY, tickLabelSizeZ)
			axisLabelStyleX.setFontSize(minFontSize)
			axisLabelStyleY.setFontSize(minFontSize)
			axisLabelStyleZ.setFontSize(minFontSize)
		elif labelSizeNotCustomizedX and labelSizeNotCustomizedY:
			minFontSize = min(tickLabelSizeX, tickLabelSizeY)
			axisLabelStyleX.setFontSize(minFontSize)
			axisLabelStyleY.setFontSize(minFontSize)
		elif labelSizeNotCustomizedY and labelSizeNotCustomizedZ:
			minFontSize = min(tickLabelSizeY, tickLabelSizeZ)
			axisLabelStyleY.setFontSize(minFontSize)
			axisLabelStyleZ.setFontSize(minFontSize)
		elif labelSizeNotCustomizedZ and labelSizeNotCustomizedX:
			minFontSize = min(tickLabelSizeZ, tickLabelSizeX)
			axisLabelStyleZ.setFontSize(minFontSize)
			axisLabelStyleX.setFontSize(minFontSize)
		elif labelSizeNotCustomizedX:
			axisLabelStyleX.setFontSize(tickLabelSizeX)
		elif labelSizeNotCustomizedY:
			axisLabelStyleY.setFontSize(tickLabelSizeY)
		elif labelSizeNotCustomizedZ:
			axisLabelStyleZ.setFontSize(tickLabelSizeZ)

		gridLineStyleX = axisLineStyleX._createCopy()
		gridLineStyleX.setLineType('dot')
		gridX0x, gridX0y, gridX1x, gridX1y, gridX2x, gridX2y, gridX3x, gridX3y = gridXYx
		gridX4x, gridX4y, gridX5x, gridX5y, gridX6x, gridX6y, gridX7x, gridX7y = gridZXx
		tickLineStyle = axisStyleX._parameterData('tickLine')
		for tickX in mainTicksX:
			### Get positions
			ratioTickX = _3DConvertToTickRatio(tickLowerX, tickUpperX, tickX)
			tickCanvasX, tickCanvasY = _convertRatioToCanvas(axisX0x, axisX0y, axisX1x, axisX1y, ratioTickX)
			### Draw tick lines
			deltaX = tickLengthMainX * tickLineVectors[0][0]
			deltaY = tickLengthMainX * tickLineVectors[0][1]
			if tickLineStyle in ['in', 'both']:
				_create_styledLine(axisLineStyleX, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX + deltaX, tickCanvasY + deltaY)
			if tickLineStyle in ['out', 'both']:
				_create_styledLine(axisLineStyleX, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX - deltaX, tickCanvasY - deltaY)
			### Draw labels
			deltaX = (tickLengthMainX + tickLabelMarginX) * tickVectors[0][0]
			deltaY = (tickLengthMainX + tickLabelMarginX) * tickVectors[0][1]
			if scalingX in ['log', 'logarithmic']:
				_create_styledExponent(axisTickLabelStyleX, tagsAxes, tickCanvasX - deltaX, tickCanvasY - deltaY, '10', '%s' % tickLabelConverterX(tickX), anchors[0], fontRatio = 0.9, overOffsetRatio = 0.4)
			elif scalingX in ['lin', 'linear']:
				_create_styledText(axisTickLabelStyleX, tagsAxes, tickCanvasX - deltaX, tickCanvasY - deltaY, '%s' % tickLabelConverterX(tickX), anchors[0])
			### Grid lines
			if (axisStyleGridMainX == True) and (tickX != tickLowerX) and (tickX != tickUpperX):
				gridX1, gridY1 = _convertRatioToCanvas(gridX0x, gridX0y, gridX1x, gridX1y, ratioTickX)
				gridX2, gridY2 = _convertRatioToCanvas(gridX2x, gridX2y, gridX3x, gridX3y, ratioTickX)
				self._create_styledLine(gridLineStyleX, tagsAxes, gridX1, gridY1, gridX2, gridY2)
				gridX1, gridY1 = _convertRatioToCanvas(gridX4x, gridX4y, gridX5x, gridX5y, ratioTickX)
				gridX2, gridY2 = _convertRatioToCanvas(gridX6x, gridX6y, gridX7x, gridX7y, ratioTickX)
				self._create_styledLine(gridLineStyleX, tagsAxes, gridX1, gridY1, gridX2, gridY2)
		for tickX in subTicksX:
			### Get positions
			ratioTickX = _3DConvertToTickRatio(tickLowerX, tickUpperX, tickX)
			tickCanvasX, tickCanvasY = _convertRatioToCanvas(axisX0x, axisX0y, axisX1x, axisX1y, ratioTickX)
			### Draw tick lines
			deltaX = tickLengthSubX * tickLineVectors[0][0]
			deltaY = tickLengthSubX * tickLineVectors[0][1]
			if tickLineStyle in ['in', 'both']:
				_create_styledLine(axisLineStyleX, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX + deltaX, tickCanvasY + deltaY)
			if tickLineStyle in ['out', 'both']:
				_create_styledLine(axisLineStyleX, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX - deltaX, tickCanvasY - deltaY)
			### Grid lines
			if (axisStyleGridSubX == True) and (tickX != tickLowerX) and (tickX != tickUpperX):
				gridX1, gridY1 = _convertRatioToCanvas(gridX0x, gridX0y, gridX1x, gridX1y, ratioTickX)
				gridX2, gridY2 = _convertRatioToCanvas(gridX2x, gridX2y, gridX3x, gridX3y, ratioTickX)
				self._create_styledLine(gridLineStyleX, tagsAxes, gridX1, gridY1, gridX2, gridY2)
				gridX1, gridY1 = _convertRatioToCanvas(gridX4x, gridX4y, gridX5x, gridX5y, ratioTickX)
				gridX2, gridY2 = _convertRatioToCanvas(gridX6x, gridX6y, gridX7x, gridX7y, ratioTickX)
				self._create_styledLine(gridLineStyleX, tagsAxes, gridX1, gridY1, gridX2, gridY2)
		axisLabelX = axisStyleX._parameterData('label')
		if axisLabelX != '':
			tickCanvasX, tickCanvasY = _convertRatioToCanvas(axisX0x, axisX0y, axisX1x, axisX1y, 0.5)
			deltaX = (tickLengthMainX + tickLabelMarginX) * labelVectors[0][0] * 2.5
			deltaY = (tickLengthMainX + tickLabelMarginX) * labelVectors[0][1] * 2.5
			_create_styledText(axisLabelStyleX, tagsAxes, tickCanvasX - deltaX, tickCanvasY - deltaY, axisLabelX, anchors[0])

		gridLineStyleY = axisLineStyleY._createCopy()
		gridLineStyleY.setLineType('dot')
		gridY0x, gridY0y, gridY1x, gridY1y, gridY2x, gridY2y, gridY3x, gridY3y = gridXYy
		gridY4x, gridY4y, gridY5x, gridY5y, gridY6x, gridY6y, gridY7x, gridY7y = gridYZy
		tickLineStyle = axisStyleY._parameterData('tickLine')
		for tickY in mainTicksY:
			### Get positions
			ratioTickY = _3DConvertToTickRatio(tickLowerY, tickUpperY, tickY)
			tickCanvasX, tickCanvasY = _convertRatioToCanvas(axisY0x, axisY0y, axisY1x, axisY1y, ratioTickY)
			### Draw tick lines
			deltaX = tickLengthMainY * tickLineVectors[1][0]
			deltaY = tickLengthMainY * tickLineVectors[1][1]
			if tickLineStyle in ['in', 'both']:
				_create_styledLine(axisLineStyleY, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX + deltaX, tickCanvasY + deltaY)
			if tickLineStyle in ['out', 'both']:
				_create_styledLine(axisLineStyleY, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX - deltaX, tickCanvasY - deltaY)
			### Draw labels
			deltaX = (tickLengthMainY + tickLabelMarginY) * tickVectors[1][0]
			deltaY = (tickLengthMainY + tickLabelMarginY) * tickVectors[1][1]
			if scalingY in ['log', 'logarithmic']:
				_create_styledExponent(axisTickLabelStyleY, tagsAxes, tickCanvasX - deltaX, tickCanvasY - deltaY, '10', '%s' % tickLabelConverterY(tickY), anchors[1], fontRatio = 0.9, overOffsetRatio = 0.4)
			elif scalingY in ['lin', 'linear']:
				_create_styledText(axisTickLabelStyleY, tagsAxes, tickCanvasX - deltaX, tickCanvasY - deltaY, '%s' % tickLabelConverterY(tickY), anchors[1])
			### Grid lines
			if (axisStyleGridMainY == True) and (tickY != tickLowerY) and (tickY != tickUpperY):
				gridX1, gridY1 = _convertRatioToCanvas(gridY0x, gridY0y, gridY1x, gridY1y, ratioTickY)
				gridX2, gridY2 = _convertRatioToCanvas(gridY2x, gridY2y, gridY3x, gridY3y, ratioTickY)
				self._create_styledLine(gridLineStyleY, tagsAxes, gridX1, gridY1, gridX2, gridY2)
				gridX1, gridY1 = _convertRatioToCanvas(gridY4x, gridY4y, gridY5x, gridY5y, ratioTickY)
				gridX2, gridY2 = _convertRatioToCanvas(gridY6x, gridY6y, gridY7x, gridY7y, ratioTickY)
				self._create_styledLine(gridLineStyleX, tagsAxes, gridX1, gridY1, gridX2, gridY2)
		for tickY in subTicksY:
			### Get positions
			ratioTickY = _3DConvertToTickRatio(tickLowerY, tickUpperY, tickY)
			tickCanvasX, tickCanvasY = _convertRatioToCanvas(axisY0x, axisY0y, axisY1x, axisY1y, ratioTickY)
			### Draw tick lines
			deltaX = tickLengthSubY * tickLineVectors[1][0]
			deltaY = tickLengthSubY * tickLineVectors[1][1]
			if tickLineStyle in ['in', 'both']:
				_create_styledLine(axisLineStyleY, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX + deltaX, tickCanvasY + deltaY)
			if tickLineStyle in ['out', 'both']:
				_create_styledLine(axisLineStyleY, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX - deltaX, tickCanvasY - deltaY)
			### Grid lines
			if (axisStyleGridSubY == True) and (tickY != tickLowerY) and (tickY != tickUpperY):
				gridX1, gridY1 = _convertRatioToCanvas(gridY0x, gridY0y, gridY1x, gridY1y, ratioTickY)
				gridX2, gridY2 = _convertRatioToCanvas(gridY2x, gridY2y, gridY3x, gridY3y, ratioTickY)
				self._create_styledLine(gridLineStyleY, tagsAxes, gridX1, gridY1, gridX2, gridY2)
				gridX1, gridY1 = _convertRatioToCanvas(gridY4x, gridY4y, gridY5x, gridY5y, ratioTickY)
				gridX2, gridY2 = _convertRatioToCanvas(gridY6x, gridY6y, gridY7x, gridY7y, ratioTickY)
				self._create_styledLine(gridLineStyleX, tagsAxes, gridX1, gridY1, gridX2, gridY2)
		axisLabelY = axisStyleY._parameterData('label')
		if axisLabelY != '':
			tickCanvasX, tickCanvasY = _convertRatioToCanvas(axisY0x, axisY0y, axisY1x, axisY1y, 0.5)
			deltaX = (tickLengthMainY + tickLabelMarginY) * labelVectors[1][0] * 2.5
			deltaY = (tickLengthMainY + tickLabelMarginY) * labelVectors[1][1] * 2.5
			_create_styledText(axisLabelStyleY, tagsAxes, tickCanvasX - deltaX, tickCanvasY - deltaY, axisLabelY, anchors[1])

		gridLineStyleZ = axisLineStyleZ._createCopy()
		gridLineStyleZ.setLineType('dot')
		gridZ0x, gridZ0y, gridZ1x, gridZ1y, gridZ2x, gridZ2y, gridZ3x, gridZ3y = gridYZz
		gridZ4x, gridZ4y, gridZ5x, gridZ5y, gridZ6x, gridZ6y, gridZ7x, gridZ7y = gridZXz
		tickLineStyle = axisStyleZ._parameterData('tickLine')
		for tickZ in mainTicksZ:
			### Get positions
			ratioTickZ = _3DConvertToTickRatio(tickLowerZ, tickUpperZ, tickZ)
			tickCanvasX, tickCanvasY = _convertRatioToCanvas(axisZ0x, axisZ0y, axisZ1x, axisZ1y, ratioTickZ)
			### Draw tick lines
			deltaX = tickLengthMainZ * tickLineVectors[2][0]
			deltaY = tickLengthMainZ * tickLineVectors[2][1]
			if tickLineStyle in ['in', 'both']:
				_create_styledLine(axisLineStyleZ, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX + deltaX, tickCanvasY + deltaY)
			if tickLineStyle in ['out', 'both']:
				_create_styledLine(axisLineStyleZ, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX - deltaX, tickCanvasY - deltaY)
			### Draw labels
			deltaX = (tickLengthMainZ + tickLabelMarginZ) * tickVectors[2][0]
			deltaY = (tickLengthMainZ + tickLabelMarginZ) * tickVectors[2][1]
			if scalingZ in ['log', 'logarithmic']:
				_create_styledExponent(axisTickLabelStyleZ, tagsAxes, tickCanvasX - deltaX, tickCanvasY - deltaY, '10', '%s' % tickLabelConverterZ(tickZ), anchors[2], fontRatio = 0.9, overOffsetRatio = 0.4)
			elif scalingZ in ['lin', 'linear']:
				_create_styledText(axisTickLabelStyleZ, tagsAxes, tickCanvasX - deltaX, tickCanvasY - deltaY, '%s' % tickLabelConverterZ(tickZ), anchors[2])
			### Grid lines
			if (axisStyleGridMainZ == True) and (tickZ != tickLowerZ) and (tickZ != tickUpperZ):
				gridX1, gridY1 = _convertRatioToCanvas(gridZ0x, gridZ0y, gridZ1x, gridZ1y, ratioTickZ)
				gridX2, gridY2 = _convertRatioToCanvas(gridZ2x, gridZ2y, gridZ3x, gridZ3y, ratioTickZ)
				self._create_styledLine(gridLineStyleZ, tagsAxes, gridX1, gridY1, gridX2, gridY2)
				gridX1, gridY1 = _convertRatioToCanvas(gridZ4x, gridZ4y, gridZ5x, gridZ5y, ratioTickZ)
				gridX2, gridY2 = _convertRatioToCanvas(gridZ6x, gridZ6y, gridZ7x, gridZ7y, ratioTickZ)
				self._create_styledLine(gridLineStyleZ, tagsAxes, gridX1, gridY1, gridX2, gridY2)
		for tickZ in subTicksZ:
			### Get positions
			ratioTickZ = _3DConvertToTickRatio(tickLowerZ, tickUpperZ, tickZ)
			tickCanvasX, tickCanvasY = _convertRatioToCanvas(axisZ0x, axisZ0y, axisZ1x, axisZ1y, ratioTickZ)
			### Draw tick lines
			deltaX = tickLengthSubZ * tickLineVectors[2][0]
			deltaY = tickLengthSubZ * tickLineVectors[2][1]
			if tickLineStyle in ['in', 'both']:
				_create_styledLine(axisLineStyleZ, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX + deltaX, tickCanvasY + deltaY)
			if tickLineStyle in ['out', 'both']:
				_create_styledLine(axisLineStyleZ, tagsAxes, tickCanvasX, tickCanvasY, tickCanvasX - deltaX, tickCanvasY - deltaY)
			### Grid lines.
			if (axisStyleGridSubZ == True) and (tickZ != tickLowerZ) and (tickZ != tickUpperZ):
				gridX1, gridY1 = _convertRatioToCanvas(gridZ0x, gridZ0y, gridZ1x, gridZ1y, ratioTickZ)
				gridX2, gridY2 = _convertRatioToCanvas(gridZ2x, gridZ2y, gridZ3x, gridZ3y, ratioTickZ)
				self._create_styledLine(gridLineStyleZ, tagsAxes, gridX1, gridY1, gridX2, gridY2)
				gridX1, gridY1 = _convertRatioToCanvas(gridZ4x, gridZ4y, gridZ5x, gridZ5y, ratioTickZ)
				gridX2, gridY2 = _convertRatioToCanvas(gridZ6x, gridZ6y, gridZ7x, gridZ7y, ratioTickZ)
				self._create_styledLine(gridLineStyleZ, tagsAxes, gridX1, gridY1, gridX2, gridY2)
		axisLabelZ = axisStyleZ._parameterData('label')
		if axisLabelZ != '':
			tickCanvasX, tickCanvasY = _convertRatioToCanvas(axisZ0x, axisZ0y, axisZ1x, axisZ1y, 0.5)
			deltaX = (tickLengthMainZ + tickLabelMarginZ) * labelVectors[2][0] * 2.5
			deltaY = (tickLengthMainZ + tickLabelMarginZ) * labelVectors[2][1] * 2.5
			_create_styledText(axisLabelStyleZ, tagsAxes, tickCanvasX - deltaX, tickCanvasY - deltaY, axisLabelZ, anchors[2])

		self._setTickSettingsX(tickLowerX, tickUpperX, mainTicksX, subTicksX)
		self._setTickSettingsY(tickLowerY, tickUpperY, mainTicksY, subTicksY)
		self._setTickSettingsZ(tickLowerZ, tickUpperZ, mainTicksZ, subTicksZ)
		self._set3DLayoutParameters(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy)

	def _drawColorZAxis(self):
		(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy) = self._get3DLayoutParameters()
		surfaceXYz = cXx * cYy - cYx * cXy
		surfaceYZz = cYx * cZy - cZx * cYy
		surfaceZXz = cZx * cXy - cXx * cZy

		tagsPlot = self._createTags(['plot'])
		_convertRatioToColor = self._convertRatioToColor
		_3DConvertToCanvas = self._3DConvertToCanvas
		_create_styledLine = self._create_styledLine
		nPoints = floor(sqrt(cZx**2 + cZy**2) * 2)
		for i in range(int(nPoints)):
			ratioZ = i / nPoints
			ratioZP1 = (i + 1) / nPoints
			tempIndexLineStyle = ILineStyle()
			tempIndexLineStyle.setColor(_convertRatioToColor(ratioZ))
			if surfaceYZz < 0.0 and surfaceZXz < 0.0:
				#exclude 0
				axisZX00, axisZY00 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 1.0, ratioZ)
				axisZX01, axisZY01 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 1.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX01, axisZY01, axisZX00, axisZY00)
				axisZX10, axisZY10 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 1.0, ratioZ)
				axisZX11, axisZY11 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 1.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX11, axisZY11, axisZX10, axisZY10)
				axisZX20, axisZY20 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 0.0, ratioZ)
				axisZX21, axisZY21 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 0.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX21, axisZY21, axisZX20, axisZY20)
			elif surfaceYZz < 0.0 and surfaceZXz >= 0.0:
				#exclude 3
				axisZX10, axisZY10 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 1.0, ratioZ)
				axisZX11, axisZY11 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 1.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX11, axisZY11, axisZX10, axisZY10)
				axisZX20, axisZY20 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 0.0, ratioZ)
				axisZX21, axisZY21 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 0.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX21, axisZY21, axisZX20, axisZY20)
				axisZX00, axisZY00 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 0.0, ratioZ)
				axisZX01, axisZY01 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 0.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX01, axisZY01, axisZX00, axisZY00)
			elif surfaceYZz >= 0.0 and surfaceZXz < 0.0:
				#exclude 1
				axisZX00, axisZY00 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 0.0, ratioZ)
				axisZX01, axisZY01 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 0.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX01, axisZY01, axisZX00, axisZY00)
				axisZX10, axisZY10 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 1.0, ratioZ)
				axisZX11, axisZY11 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 1.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX11, axisZY11, axisZX10, axisZY10)
				axisZX20, axisZY20 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 1.0, ratioZ)
				axisZX21, axisZY21 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 1.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX21, axisZY21, axisZX20, axisZY20)
			elif surfaceYZz >= 0.0 and surfaceZXz >= 0.0:
				#exclude 2
				axisZX20, axisZY20 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 0.0, ratioZ)
				axisZX21, axisZY21 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 1.0, 0.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX21, axisZY21, axisZX20, axisZY20)
				axisZX00, axisZY00 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 0.0, ratioZ)
				axisZX01, axisZY01 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 0.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX01, axisZY01, axisZX00, axisZY00)
				axisZX10, axisZY10 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 1.0, ratioZ)
				axisZX11, axisZY11 = _3DConvertToCanvas(p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy, 0.0, 1.0, ratioZP1)
				_create_styledLine(tempIndexLineStyle, tagsPlot, axisZX11, axisZY11, axisZX10, axisZY10)

	def _set3DLayoutParameters(self, p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy):
		self._3DLayoutParameters = (p0x, p0y, cXx, cXy, cYx, cYy, cZx, cZy)

	def _get3DLayoutParameters(self):
		return self._3DLayoutParameters

	def _setAxisBox3DLayoutByRatio(self, ratioXyYy, ratioXyZy):
		x0, x1 = self._getAxisRangeX()
		y0, y1 = self._getAxisRangeY()
		X = float(x1 - x0)
		Y = float(y1 - y0)

		if (ratioXyYy < 0.0) or (ratioXyZy < 0.0):
			raise IllegalArgumentException('ratioXy and ratioXz must be positive.')

		alpha = ratioXyYy - sqrt(ratioXyYy**2 + 1.0)
		alpha2 = alpha**2
		alpha2p1 = alpha2 + 1.0
		beta = (alpha2p1 + sqrt(alpha2p1**2 + 4.0 * alpha2 * ratioXyZy**2)) / (2.0 * ratioXyZy)
		x = sqrt(1.0 / (1.0 + alpha2 + beta**2))
		y = alpha * x
		z = beta * x
		self._set3DRotationVector([x, y, z])

	def _set3DRotationVector(self, vector):
		self._3DRotationVector = vector

	def _get3DRotationVector(self):
		return self._3DRotationVector

	def _tickLabelConverterDouble(self, data):
		### Jython2.1 does not understand rstrip(char).
		#result = ('%0.11f' % (data)).rstrip('0')
		result = '%0.11f' % (data)
		while result[-1] == '0':
			result = result[:-1]

		if result[-1] == '.':
			return result + '0'
		else:
			return result

	def _tickLabelConverterInt(self, data):
		intData = int(data)
		if intData == data:
			return intData
		else:
			return ''

	def _tickLabelConverterMinute(self, data):
		timeTuple = time.localtime(data)
		return '%02m%02s' % (timeTuple[4], timeTuple[5])

	def _tickLabelConverterHour(self, data):
		timeTuple = time.localtime(data)
		return '%02d:%02d:%02d' % (timeTuple[3], timeTuple[4], timeTuple[5])

	def _tickLabelConverterDay(self, data):
		timeTuple = time.localtime(data)
		return '%02d.%02d' % (timeTuple[1], timeTuple[2])

	def _tickLabelConverterMonth(self, data):
		timeTuple = time.localtime(data)
		return '%04d.%02d' % (timeTuple[0], timeTuple[1])

	def _getTickLabelConverter(self, axisType, lower, upper):
		if axisType == 'double':
			axisTypeString = 'double'
			tickLabelConverter = self._tickLabelConverterDouble
		elif axisType == 'int':
			axisTypeString = 'int'
			tickLabelConverter = self._tickLabelConverterInt
		elif axisType == 'time':
			span = upper - lower
			if span >= 2592000:
				axisTypeString = 'timeMonth'
				tickLabelConverter = self._tickLabelConverterMonth
			elif span >= 86400:
				axisTypeString = 'timeDay'
				tickLabelConverter = self._tickLabelConverterDay
			elif span >= 3600:
				axisTypeString = 'timeHour'
				tickLabelConverter = self._tickLabelConverterHour
			else:
				axisTypeString = 'timeMinute'
				tickLabelConverter = self._tickLabelConverterMinute
		else:
			raise IllegalArgumentException('Invalid axis type "%s".' % axisType)
		return axisTypeString, tickLabelConverter

	def _getTicks(self, rangeMin, rangeMax, scaling, axisType):
		ticksMain = []
		ticksSub = []
		if axisType == 'timeMonth':
			### Scaling check.
			if scaling in ['log', 'logarithmic']:
				raise IllegalArgumentException('Time(month) axis type does not support log scaling.')

			### Minimum month.
			timeTupleMin = time.localtime(rangeMin)
			tickMin = _mktime((timeTupleMin[0], timeTupleMin[1], 1, 0, 0, 0, 0, 0, 0))
			if tickMin < rangeMin:
				tickMin = _mktime((timeTupleMin[0], timeTupleMin[1] + 1, 1, 0, 0, 0, 0, 0, 0))

			### Maximum month.
			timeTupleMax = time.localtime(rangeMax)
			tickMax = _mktime((timeTupleMax[0], timeTupleMax[1], 1, 0, 0, 0, 0, 0, 0))

			### Main ticks.
			currentTick = tickMin
			while currentTick <= tickMax:
				ticksMain.append(currentTick)
				currentTuple = time.localtime(currentTick)
				currentTick = _mktime((currentTuple[0], currentTuple[1] + 1, 1, 0, 0, 0, 0, 0, 0))

			### Sub ticks are left blank.
			pass

			tickLower = rangeMin
			tickUpper = rangeMax

		elif axisType == 'timeDay':
			### Scaling check.
			if scaling in ['log', 'logarithmic']:
				raise IllegalArgumentException('Time(day) axis type does not support log scaling.')

			### Minimum day.
			timeTupleMin = time.localtime(rangeMin)
			tickMin = _mktime((timeTupleMin[0], timeTupleMin[1], timeTupleMin[2], 0, 0, 0, 0, 0, 0))
			if tickMin < rangeMin:
				tickMin = _mktime((timeTupleMin[0], timeTupleMin[1], timeTupleMin[2] + 1, 0, 0, 0, 0, 0, 0))

			### Maximum day.
			timeTupleMax = time.localtime(rangeMax)
			tickMax = _mktime((timeTupleMax[0], timeTupleMax[1], timeTupleMax[2], 0, 0, 0, 0, 0, 0))

			### Check the span.
			span = int((tickMax - tickMin) / 86400.0)
			if span <= 5:
				lengthMain = 86400.0
				lengthSub = None
			elif 5 < span <= 10:
				lengthMain = 86400.0 * 2
				lengthSub = 86400.0
			else:
				lengthMain = 86400.0 * 5
				lengthSub = 86400.0

			### Main ticks.
			currentTick = tickMin
			while currentTick <= tickMax:
				ticksMain.append(currentTick)
				currentTick += lengthMain

			### Sub ticks are left blank.
			if lengthSub != None:
				currentTick = tickMin - 86400.0
				while currentTick <= rangeMax:
					if (rangeMin <= currentTick) and (not currentTick in ticksMain):
						ticksSub.append(currentTick)
					currentTick += lengthSub

			tickLower = rangeMin
			tickUpper = rangeMax

		elif axisType == 'timeHour':
			### Scaling check.
			if scaling in ['log', 'logarithmic']:
				raise IllegalArgumentException('Time(time) axis type does not support log scaling.')

			### Minimum Hour.
			timeTupleMin = time.localtime(rangeMin)
			tickMin = _mktime((timeTupleMin[0], timeTupleMin[1], timeTupleMin[2], timeTupleMin[3], 0, 0, 0, 0, 0))
			if tickMin < rangeMin:
				tickMin = _mktime((timeTupleMin[0], timeTupleMin[1], timeTupleMin[2], timeTupleMin[3] + 1, 0, 0, 0, 0, 0))

			### Maximum day.
			timeTupleMax = time.localtime(rangeMax)
			tickMax = _mktime((timeTupleMax[0], timeTupleMax[1], timeTupleMax[2], timeTupleMax[3], 0, 0, 0, 0, 0))

			### Check the span.
			span = int((tickMax - tickMin) / 3600.0)
			if span <= 5:
				lengthMain = 3600.0
				lengthSub = None
			elif 5 < span <= 10:
				lengthMain = 3600.0 * 2
				lengthSub = 3600.0
			else:
				lengthMain = 3600.0 * 5
				lengthSub = 3600.0

			### Main ticks.
			currentTick = tickMin
			while currentTick <= tickMax:
				ticksMain.append(currentTick)
				currentTick += lengthMain

			### Sub ticks are left blank.
			if lengthSub != None:
				currentTick = tickMin - 3600.0
				while currentTick <= rangeMax:
					if (rangeMin <= currentTick) and (not currentTick in ticksMain):
						ticksSub.append(currentTick)
					currentTick += lengthSub

			tickLower = rangeMin
			tickUpper = rangeMax

		elif axisType == 'timeMinute':
			### Scaling check.
			if scaling in ['log', 'logarithmic']:
				raise IllegalArgumentException('Time(time) axis type does not support log scaling.')

			### Minimum Hour.
			timeTupleMin = time.localtime(rangeMin)
			tickMin = _mktime((timeTupleMin[0], timeTupleMin[1], timeTupleMin[2], timeTupleMin[3], timeTupleMin[4], 0, 0, 0, 0))
			if tickMin < rangeMin:
				tickMin = _mktime((timeTupleMin[0], timeTupleMin[1], timeTupleMin[2], timeTupleMin[3], timeTupleMin[4] + 1, 0, 0, 0, 0))

			### Maximum day.
			timeTupleMax = time.localtime(rangeMax)
			tickMax = _mktime((timeTupleMax[0], timeTupleMax[1], timeTupleMax[2], timeTupleMax[3], timeTupleMax[4], 0, 0, 0, 0))

			### Check the span.
			span = int((tickMax - tickMin) / 60.0)
			if span <= 5:
				lengthMain = 60.0
				lengthSub = None
			elif 5 < span <= 10:
				lengthMain = 60.0 * 2
				lengthSub = 60.0
			else:
				lengthMain = 60.0 * 5
				lengthSub = 60.0

			### Main ticks.
			currentTick = tickMin
			while currentTick <= tickMax:
				ticksMain.append(currentTick)
				currentTick += lengthMain

			### Sub ticks are left blank.
			if lengthSub != None:
				currentTick = tickMin - 60.0
				while currentTick <= rangeMax:
					if (rangeMin <= currentTick) and (not currentTick in ticksMain):
						ticksSub.append(currentTick)
					currentTick += lengthSub

			tickLower = rangeMin
			tickUpper = rangeMax

		else:
			### For rounding error.
			pat = 1.0e-08

			if scaling in ['lin', 'linear']:
				length = rangeMax - rangeMin
				logFactor = log10(length)
				### 10**(negative int) causes an exception in Jython.
				factor = 10**floor(logFactor)
				lengthT = int(length / factor)
				tickLower = rangeMin
				tickUpper = rangeMax

				if lengthT == 1:
					spanT = 0.2 * factor
					subDivider = 4.0
				elif lengthT == 2:
					spanT = 0.5 * factor
					subDivider = 5.0
				elif lengthT == 3:
					spanT = 1.0 * factor
					subDivider = 5.0
				elif lengthT == 4:
					spanT = 1.0 * factor
					subDivider = 5.0
				elif lengthT == 5:
					spanT = 1.0 * factor
					subDivider = 5.0
				elif lengthT == 6:
					spanT = 2.0 * factor
					subDivider = 4.0
				elif lengthT == 7:
					spanT = 2.0 * factor
					subDivider = 4.0
				elif lengthT == 8:
					spanT = 2.0 * factor
					subDivider = 4.0
				elif lengthT == 9:
					spanT = 2.0 * factor
					subDivider = 4.0
				else:
					raise RuntimeError, '%s:%s:%s:%s' % (rangeMin, rangeMax, scaling, axisType)

				minI = int(floor(rangeMin / spanT))
				maxI = int(rangeMax / spanT)
				for i in range(minI, maxI + 1):
					tickMain = i * spanT
					if rangeMin - pat <= tickMain <= rangeMax + pat:
						ticksMain.append(tickMain)

				spanTSub = spanT / subDivider
				minISub = int(floor(rangeMin / spanTSub))
				maxISub = int(rangeMax / spanTSub)
				for i in range(minISub, maxISub + 1):
					tickSub = i * spanTSub
					if (tickSub not in ticksMain) and (rangeMin - pat <= tickSub <= rangeMax + pat):
						ticksSub.append(tickSub)

			elif scaling in ['log', 'logarithmic']:
				logMin = log10(rangeMin)
				logMax = log10(rangeMax)
				tickLower = logMin
				tickUpper = logMax
				if floor(logMin) + 1.0 <= logMax:
					logMinI = floor(logMin)
					logMaxI = floor(logMax)
					logLength = logMaxI - logMinI
					logLogLength = log10(logLength)
					logFactor = 10**float(floor(logLogLength))
					logMinS = int(floor(logMinI / logFactor))
					logMaxS = int(floor(logMaxI / logFactor))
				else:
					logLength = logMax - logMin
					logLogLength = log10(logLength)
					logFactor = 10**float(floor(logLogLength))
					logMinS = int(floor(logMin / logFactor))
					logMaxS = int(floor(logMax / logFactor))
				logMinF = logMinS * logFactor
				logMaxF = logMaxS * logFactor
				logLengthS = logMaxS - logMinS
				if logLengthS == 0:
					logSpan = 1 * logFactor
				elif logLengthS == 1:
					logSpan = 1 * logFactor
				elif logLengthS == 2:
					logSpan = 1 * logFactor
				elif logLengthS == 3:
					logSpan = 1 * logFactor
				elif logLengthS == 4:
					logSpan = 1 * logFactor
				elif logLengthS == 5:
					logSpan = 1 * logFactor
				elif logLengthS == 6:
					logSpan = 2 * logFactor
				elif logLengthS == 7:
					logSpan = 2 * logFactor
				elif logLengthS == 8:
					logSpan = 2 * logFactor
				elif logLengthS == 9:
					logSpan = 2 * logFactor
				else:
					raise RuntimeError, '%s:%s:%s:%s' % (rangeMin, rangeMax, scaling, axisType)

				current = logMinF
				while (current <= logMax + pat):
					if logMin - pat <= current:
						ticksMain.append(current)
					current += logSpan

				if logSpan == 1:
					for mainS in range(logMinS, logMaxS + 2):
						for subS in range(2, 10):
							tickValue = mainS + log10(subS)
							if logMin - pat < tickValue < logMax + pat:
								ticksSub.append(tickValue)

			else:
				raise RuntimeError, '%s:%s:%s:%s' % (rangeMin, rangeMax, scaling, axisType)

		return tickLower, tickUpper, ticksMain, ticksSub

	def _createRegionBox(self):
		x0, x1 = self._getRegionRangeX()
		y0, y1 = self._getRegionRangeY()
		fillColor = self.style()._parameterData('regionFillColor')
		lineColor = self.style()._parameterData('regionLineColor')
		fillStyle = IFillStyle()
		fillStyle.setColor(fillColor)
		lineStyle = ILineStyle()
		lineStyle.setColor(lineColor)
		self._getGuiPlotter().create_styledRectangle(lineStyle, fillStyle, self._createTags(['regionBox']), x0, y0, x1, y1)

	def remove(self, data):
		if data in self._getItemDataKeys():
			self._removeItemData(data)
		else:
			raise IllegalArgumentException()

	def _refreshClear(self):
		self.info()._clear()
		self._clearItemData()
		self._clearRegion()
		if not self._getTitleCustomized():
			self._clearTitleData()

	def clear(self):
		self.info().clear()
		self._clearItemData()
		self._clearRegion()
		if not self._getTitleCustomized():
			self._clearTitleData()

	def _destroyRegion(self):
		self.info().clear()
		self._clearRegion()
		self._deleteRegionBox()

	def _clearRegion(self):
		self._clearTitle()
		guiPlotter = self._getGuiPlotter()
		if self._isMatplotlib:
			guiPlotter.delete(self._serialNumber)
		else:
			guiPlotter.delete(self._createTags(['axes']))
			guiPlotter.delete(self._createTags(['plot']))

	def _deleteRegionBox(self):
		self._getGuiPlotter().delete(self._createTags(['regionBox']))

	def _refreshAll(self):
		self._deleteRegionBox()
		self._initializeValues()
		self._refresh()

	def _setTitleCustomized(self, boolean):
		self._titleCustomized = boolean

	def _getTitleCustomized(self):
		return self._titleCustomized

	def _createTitle(self, titleStyle, x, y):
		if self._titleShown:
			self._clearTitle()

		textStyle = titleStyle.textStyle()._createCopy()
		if not textStyle._getCustomized('fontSize'):
			fontSize = textStyle.fontSize()
			textDataList = [[textStyle, self._getTitle()]]
			fontMeasurements = self._getFontMeasurements(textDataList)
			titleLength = fontMeasurements[0][0]
			titleHeight = fontMeasurements[0][1]
			x0, x1 = self._getAxisRangeX()
			axisLength = x1 - x0
			sizeFactor = axisLength * 0.8 / titleLength
			if sizeFactor < 1.0:
				fontSize *= sizeFactor
				titleHeight *= sizeFactor
				textStyle.setFontSize(fontSize)
			y0, y1 = self._getRegionRangeY()
			sizeFactor = float(y - y0) / (titleHeight + 2.0)
			if sizeFactor < 1.0:
				textStyle.setFontSize(fontSize * sizeFactor)

		self._create_styledText(textStyle, self._createTags(['title']), x, y, self._getTitle(), S)
		self._titleShown = True

	def _clearTitle(self):
		if self._titleShown == True:
			self._getGuiPlotter().delete(self._createTags(['title']))
		self._titleShown = False

	def setTitle(self, title):
		self._setTitle(title)
		if title == '':
			self._setTitleCustomized(False)
		else:
			self._setTitleCustomized(True)

	def _setTitle(self, title):
		self._title = title

	def _getTitle(self):
		return self._title

	def _clearTitleData(self):
		self._title = ''
		self._setTitleCustomized(False)

	def _appendTitle(self, title):
		if self._getTitleCustomized():
			pass
		elif self._getTitle() == '':
			self._setTitle(title)
		else:
			self._setTitle('%s & %s' % (self._getTitle(), title))
		return self._getTitle()

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
			return self._getType(parameterName).getValue()
		else:
			raise IllegalArgumentException('Parameter %s is not in %s.' % (parameterName, availables))

	def setParameter(self, parameterName, options = None):
		if not parameterName in self.availableParameters():
			return False
		else:
			if options == None:
				self._getType(parameterName).reset()
			else:
				try:
					self._getType(parameterName).setValue(options)
				except _convertException:
					return False
		return True

	def style(self):
		return self._plotterStyle

	def setStyle(self, style):
		self._plotterStyle = style

	def applyStyle(self, style):
		self.setStyle(style)
		self.clear()
		self._refresh()

	def setXLimits(self, minX = None, maxX = None):
		if minX == None:
			self._minX = None
		else:
			self._minX = float(minX)
		if maxX == None:
			self._maxX = None
		else:
			self._maxX = float(maxX)

	def _getXLimits(self):
		return self._minX, self._maxX

	def setYLimits(self, minY = None, maxY = None):
		if minY == None:
			self._minY = None
		else:
			self._minY = float(minY)
		if maxY == None:
			self._maxY = None
		else:
			self._maxY = float(maxY)

	def _getYLimits(self):
		return self._minY, self._maxY

	def setZLimits(self, minZ = None, maxZ = None):
		if minZ == None:
			self._minZ = None
		else:
			self._minZ = float(minZ)
		if maxZ == None:
			self._maxZ = None
		else:
			self._maxZ = float(maxZ)

	def _getZLimits(self):
		return self._minZ, self._maxZ

	def layout(self):
		return self._plotterLayout

	def setLayout(self, layout):
		self._plotterLayout = layout

	def info(self):
		return self._plotterInfo
