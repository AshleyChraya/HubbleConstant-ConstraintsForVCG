from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import *

class IInfo:
	def __init__(self, parent):
		self._setParent(parent)
		self._legend = []
		self._text = []
		self._statisticsBoxShown = False
		self._legendsBoxShown = False
		self._textsBoxShown = False

		self._setLegendCustomized(False)
		self._setLegendVeto(False)

	def _setParent(self, parent):
		self._parent = parent

	def _getParent(self):
		return self._parent

	def _setLegendCustomized(self, boolean):
		self._legendCustomized = boolean

	def _getLegendCustomized(self):
		return self._legendCustomized

	def _setLegendVeto(self, boolean):
		self._legendVeto = boolean

	def _getLegendVeto(self):
		return self._legendVeto

	def addLegend(self, style, description):
		if not self._getLegendVeto():
			self._addLegend(style, description)
			self._setLegendCustomized(True)

	def _addLegend(self, style, description):
		if not self._getLegendVeto():
			if style.__class__.__name__ in ['IFillStyle', 'ILineStyle', 'IMarkerStyle']:
				self._legend.append([style._createCopy(), description])
			else:
				raise IllegalArgumentException()

	def addText(self, text):
		self._text.append(text)

	def _clear(self):
		self._clear_styledStatisticsBox()
		self._clear_styledLegendsBox()
		self._clear_styledTextsBox()

	def clear(self):
		self._clear()
		self._legend = []
		self._text = []
		self._setLegendCustomized(False)
		self._setLegendVeto(False)

	def _clear_styledStatisticsBox(self):
		if self._statisticsBoxShown == True:
			tags = [self._getParent()._getPrefix() + '_statisticsBox']
			self._getParent()._getGuiPlotter().delete(tags)
			self._statisticsBoxShown = False

	def _clear_styledLegendsBox(self):
		if self._legendsBoxShown == True:
			tags = [self._getParent()._getPrefix() + '_legendsBox']
			self._getParent()._getGuiPlotter().delete(tags)
			self._legendsBoxShown = False

	def _clear_styledTextsBox(self):
		if self._textsBoxShown == True:
			tags = [self._getParent()._getPrefix() + '_textsBox']
			self._getParent()._getGuiPlotter().delete(tags)
			self._textsBoxShown = False

	def _create_styledTextsBox(self, infoStyle):
		if self._text == []:
			return

		if not infoStyle.textStyle()._getCustomized('fontSize'):
			### Auto font scaling.
			infoStyle = infoStyle._createCopy()
			infoTextStyle = infoStyle.textStyle()
			plotter = self._getParent()
			fontSize = infoTextStyle.fontSize()
			textDataList = []
			for text in self._text:
				textDataList.append([infoTextStyle, text])
			fontMeasurements = plotter._getFontMeasurements(textDataList)
			maxLegendLength = 0
			for fontMeasurement in fontMeasurements:
				maxLegendLength = max(maxLegendLength, fontMeasurement[0])
			maxLegendHeight = fontMeasurements[0][1]
			x0, x1 = plotter._getAxisRangeX()
			y0, y1 = plotter._getAxisRangeY()
			width = (x1 - x0) / 2.0
			height = (y1 - y0) / 2.0
			### Width check.
			sizeFactor = width / (10.0 + fontSize + maxLegendLength)
			if sizeFactor < 1.0:
				fontSize *= sizeFactor
				maxLegendHeight *= sizeFactor
				infoTextStyle.setFontSize(fontSize)
			### Height check.
			sizeFactor = height / (10.0 + (maxLegendHeight + 2.0) * len(textDataList))
			if sizeFactor < 1.0:
				infoTextStyle.setFontSize(fontSize * sizeFactor)

		newTexts = self._text[:]
		region = self._getParent()
		tags = [region._getPrefix() + '_textsBox']
		self._getParent()._getGuiPlotter().create_styledTextsBox(infoStyle, region, region.layout(), newTexts, tags)
		self._textsBoxShown = True

	def _create_styledLegendsBox(self, infoStyle):
		if self._legend == []:
			return

		newLegens = []
		for [style, description] in self._legend:
			newLegens.append([style._createCopy(), description])

		if not infoStyle.textStyle()._getCustomized('fontSize'):
			### Auto font scaling.
			infoStyle = infoStyle._createCopy()
			infoTextStyle = infoStyle.textStyle()
			plotter = self._getParent()
			fontSize = infoTextStyle.fontSize()
			textDataList = []
			for [style, description] in newLegens:
				textDataList.append([infoTextStyle, description])
			fontMeasurements = plotter._getFontMeasurements(textDataList)
			maxLegendLength = 0
			for fontMeasurement in fontMeasurements:
				maxLegendLength = max(maxLegendLength, fontMeasurement[0])
			maxLegendHeight = fontMeasurements[0][1]
			x0, x1 = plotter._getAxisRangeX()
			y0, y1 = plotter._getAxisRangeY()
			width = (x1 - x0) / 2.0
			height = (y1 - y0) / 2.0
			### Width check.
			sizeFactor = width / (12.0 + fontSize + maxLegendLength)
			if sizeFactor < 1.0:
				fontSize *= sizeFactor
				maxLegendHeight *= sizeFactor
				infoTextStyle.setFontSize(fontSize)
			### Height check.
			sizeFactor = height / (10.0 + (maxLegendHeight + 2.0) * len(textDataList))
			if sizeFactor < 1.0:
				infoTextStyle.setFontSize(fontSize * sizeFactor)

		region = self._getParent()
		tags = [region._getPrefix() + '_legendsBox']
		self._getParent()._getGuiPlotter().create_styledLegendsBox(infoStyle, region, region.layout(), newLegens, tags)
		self._legendsBoxShown = True

	def _create_styledStatisticsBox(self, infoStyle, statisticsData):
		if statisticsData == []:
			return

		if not infoStyle.textStyle()._getCustomized('fontSize'):
			### Auto font scaling.
			infoStyle = infoStyle._createCopy()
			infoTextStyle = infoStyle.textStyle()
			plotter = self._getParent()
			fontSize = infoTextStyle.fontSize()
			textDataList = []
			for statistic in statisticsData:
				textDataList.append([infoTextStyle, statistic[0]])
				textDataList.append([infoTextStyle, statistic[1]])
			fontMeasurements = plotter._getFontMeasurements(textDataList)
			maxNameLength = 0
			maxDataLength = 0
			for i, fontMeasurement in enumerate(fontMeasurements):
				if i % 2:
					maxDataLength = max(maxDataLength, fontMeasurement[0])
				else:
					maxNameLength = max(maxNameLength, fontMeasurement[0])
			maxNameHeight = fontMeasurements[0][1]
			x0, x1 = plotter._getAxisRangeX()
			y0, y1 = plotter._getAxisRangeY()
			width = (x1 - x0) / 2.0
			height = (y1 - y0) / 2.0
			### Width check.
			sizeFactor = width / (15.0 + maxNameLength + maxDataLength)
			if sizeFactor < 1.0:
				fontSize *= sizeFactor
				maxNameHeight *= sizeFactor
				infoTextStyle.setFontSize(fontSize)
			### Height check.
			sizeFactor = height / (10.0 + (maxNameHeight + 2.0) * len(statisticsData))
			if sizeFactor < 1.0:
				infoTextStyle.setFontSize(fontSize * sizeFactor)

		newStatisticsData = statisticsData[:]
		region = self._getParent()
		tags = [region._getPrefix() + '_statisticsBox']
		self._getParent()._getGuiPlotter().create_styledStatisticsBox(infoStyle, region, region.layout(), newStatisticsData, tags)
		self._statisticsBoxShown = True
