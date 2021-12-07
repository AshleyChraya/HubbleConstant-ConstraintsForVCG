from paida.paida_core.PAbsorber import *
from paida.paida_core.IManagedObject import *
from paida.paida_core.IAxis import *
from paida.paida_core.IProfile1D import *
from paida.paida_core.IProfile2D import *
from paida.paida_core.IHistogram1D import *
from paida.paida_core.IHistogram2D import *
from paida.paida_core.IHistogram3D import *
from paida.paida_core.ICloud1D import *
from paida.paida_core.ICloud2D import *
from paida.paida_core.ICloud3D import *
from paida.paida_core.ITuple import *
from paida.paida_core.ITupleFactory import *
from paida.paida_core.IDataPointSet import *
from paida.paida_core.IFunctionFactory import *
from paida.paida_core.PExceptions import *
from paida.paida_core.PUtilities import *
from paida.paida_core.IConstants import *
from paida.paida_core.IHistogramFactory import *
from paida.paida_core.IFunctionFactory import *
from paida.paida_core.IDataPointSetFactory import *
import paida.paida_gui.PRoot as PRoot
import paida.paida_core.PTypes as PTypes

import sys
import os
import xml.sax
import xml.sax.saxutils
import StringIO
from math import sqrt

encoding = 'ISO-8859-1'

class _handler_initial(xml.sax.handler.ContentHandler):
	def __init__(self, parser, tree):
		xml.sax.handler.ContentHandler.__init__(self)
		self.parser = parser
		self.tree = tree

	def setHandler(self, handler):
		self.parser.setContentHandler(handler)

	def startDocument(self):
		self.setHandler(_handler_aida(self))

class _handler_EntityResolver(xml.sax.handler.EntityResolver):
	def resolveEntity(self, publicId, systemId):
		return StringIO.StringIO()

class _handler_base(xml.sax.handler.ContentHandler):
	def __init__(self, parent):
		xml.sax.handler.ContentHandler.__init__(self)
		self.parent = parent
		self.parser = parent.parser

	def evaluator(self, data):
		if data == u'OVERFLOW':
			return IAxis.OVERFLOW_BIN
		elif data == u'UNDERFLOW':
			return IAxis.UNDERFLOW_BIN
		elif data == 'NaN':
			return 0.0
		elif data == 'null':
			return None
		else:
			raise IOException('"%s" of "%s" is invalid.' % (data, type(data)))

	def setHandler(self, handler):
		self.parser.setContentHandler(handler)

	def endElement(self, name):
		pass

	def characters(self, content):
		return

class _handler_aida(_handler_base):
	def startElement(self, name, attributes):
		if name == 'aida':
			self.version = str(attributes['version'])

		elif name == 'implementation':
			self.implementation = _handler_implementation(self)
			self.setHandler(self.implementation)
			self.implementation.startElement(name, attributes)

		elif name == 'histogram1d':
			self.histogram1d = _handler_histogram1d(self)
			self.setHandler(self.histogram1d)
			self.histogram1d.startElement(name, attributes)

		elif name == 'histogram2d':
			self.histogram2d = _handler_histogram2d(self)
			self.setHandler(self.histogram2d)
			self.histogram2d.startElement(name, attributes)

		elif name == 'histogram3d':
			self.histogram3d = _handler_histogram3d(self)
			self.setHandler(self.histogram3d)
			self.histogram3d.startElement(name, attributes)

		elif name == 'tuple':
			self.ituple = _handler_tuple(self)
			self.setHandler(self.ituple)
			self.ituple.startElement(name, attributes)

		elif name == 'cloud1d':
			self.cloud1d = _handler_cloud1d(self)
			self.setHandler(self.cloud1d)
			self.cloud1d.startElement(name, attributes)

		elif name == 'cloud2d':
			self.cloud2d = _handler_cloud2d(self)
			self.setHandler(self.cloud2d)
			self.cloud2d.startElement(name, attributes)

		elif name == 'cloud3d':
			self.cloud3d = _handler_cloud3d(self)
			self.setHandler(self.cloud3d)
			self.cloud3d.startElement(name, attributes)

		elif name == 'profile1d':
			self.profile1d = _handler_profile1d(self)
			self.setHandler(self.profile1d)
			self.profile1d.startElement(name, attributes)

		elif name == 'profile2d':
			self.profile2d = _handler_profile2d(self)
			self.setHandler(self.profile2d)
			self.profile2d.startElement(name, attributes)

		elif name == 'dataPointSet':
			self.dataPointSet = _handler_dataPointSet(self)
			self.setHandler(self.dataPointSet)
			self.dataPointSet.startElement(name, attributes)

		elif name == 'function':
			self.function = _handler_function(self)
			try:
				self.function.functionFactory = self.functionFactory
			except AttributeError:
				self.functionFactory = IFunctionFactory(self.parent.tree)
				self.function.functionFactory = self.functionFactory
			self.setHandler(self.function)
			self.function.startElement(name, attributes)

		else:
			raise IOException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		tree = self.parent.tree
		if name == 'aida':
			tree.cd('/', update = True, block = True)

		elif name == 'implementation':
			pass

		elif name == 'histogram1d':
			tree.mkdirs(self.histogram1d.path, update = False)
			tree.cd(self.histogram1d.path, update = False)
			tree._mkObject(self.histogram1d.name, self.histogram1d.histogram1d, update = True, block = False)

		elif name == 'histogram2d':
			tree.mkdirs(self.histogram2d.path, update = False)
			tree.cd(self.histogram2d.path, update = False)
			tree._mkObject(self.histogram2d.name, self.histogram2d.histogram2d, update = True, block = False)

		elif name == 'histogram3d':
			tree.mkdirs(self.histogram3d.path, update = False)
			tree.cd(self.histogram3d.path, update = False)
			tree._mkObject(self.histogram3d.name, self.histogram3d.histogram3d, update = True, block = False)

		elif name == 'tuple':
			tree.mkdirs(self.ituple.path, update = False)
			tree.cd(self.ituple.path, update = False)
			tree._mkObject(self.ituple.name, self.ituple.ituple, update = True, block = False)

		elif name == 'cloud1d':
			tree.mkdirs(self.cloud1d.path, update = False)
			tree.cd(self.cloud1d.path, update = False)
			tree._mkObject(self.cloud1d.name, self.cloud1d.cloud1d, update = True, block = False)

		elif name == 'cloud2d':
			tree.mkdirs(self.cloud2d.path, update = False)
			tree.cd(self.cloud2d.path, update = False)
			tree._mkObject(self.cloud2d.name, self.cloud2d.cloud2d, update = True, block = False)

		elif name == 'cloud3d':
			tree.mkdirs(self.cloud3d.path, update = False)
			tree.cd(self.cloud3d.path, update = False)
			tree._mkObject(self.cloud3d.name, self.cloud3d.cloud3d, update = True, block = False)

		elif name == 'profile1d':
			tree.mkdirs(self.profile1d.path, update = False)
			tree.cd(self.profile1d.path, update = False)
			tree._mkObject(self.profile1d.name, self.profile1d.profile1d, update = True, block = False)

		elif name == 'profile2d':
			tree.mkdirs(self.profile2d.path, update = False)
			tree.cd(self.profile2d.path, update = False)
			tree._mkObject(self.profile2d.name, self.profile2d.profile2d, update = True, block = False)

		elif name == 'dataPointSet':
			tree.mkdirs(self.dataPointSet.path, update = False)
			tree.cd(self.dataPointSet.path, update = False)
			tree._mkObject(self.dataPointSet.name, self.dataPointSet.dataPointSet, update = True, block = False)

		elif name == 'function':
			tree.mkdirs(self.function.path, update = False)
			tree.cd(self.function.path, update = False)
			tree._mkObject(self.function.name, self.function.function, update = True, block = False)

		else:
			raise IOException('Unexpected element name "%s"' % name)

class _handler_implementation(_handler_base):
	def startElement(self, name, attributes):
		if name == 'aida':
			self.package = str(attributes['package'])
			self.version = str(attributes['version'])

	def endElement(self, name):
		self.setHandler(self.parent)

class _handler_annotation(_handler_base):
	def __init__(self, parent):
		_handler_base.__init__(self, parent)
		self.annotation = IAnnotation()

	def startElement(self, name, attributes):
		self.setHandler(_handler_item(self))

	def endElement(self, name):
		self.setHandler(self.parent)
		self.parent.endElement(name)

class _handler_item(_handler_base):
	def startElement(self, name, attributes):
		try:
			if attributes['sticky'] == u'true':
				self.parent.annotation._addItem(str(attributes['key']), str(attributes['value']), True)
			else:
				self.parent.annotation._addItem(str(attributes['key']), str(attributes['value']), False)
		except KeyError:
			self.parent.annotation._addItem(str(attributes['key']), str(attributes['value']), False)

	def endElement(self, name):
		if name == 'annotation':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_axis(_handler_base):
	def startElement(self, name, attributes):
		if name == 'axis':
			### Direction.
			try:
				self.direction = str(attributes['direction'])
			except KeyError:
				self.direction = 'x'

			### Minimum edge.
			try:
				self.minimum = float(attributes['min'])
			except ValueError:
				self.minimum = self.evaluator(attributes['min'])

			### Maximum edge.
			try:
				self.maximum = float(attributes['max'])
			except ValueError:
				self.maximum = self.evaluator(attributes['max'])

			### Number of bins.
			try:
				self.numberOfBins = int(attributes['numberOfBins'])
			except ValueError:
				self.numberOfBins = self.evaluator(attributes['numberOfBins'])

			### Default isFixedBinning.
			self.isFixedBinning = True

		elif name == 'binBorder':
			### Variable width binning.
			self.isFixedBinning = False

			self.binBorders = []
			self.binBorder = _handler_binBorder(self)
			self.setHandler(self.binBorder)
			self.binBorder.startElement(name, attributes)

	def endElement(self, name):
		if self.isFixedBinning:
			tempEdge = [self.minimum]
			tempMinimum = self.minimum
			unit = (self.maximum - tempMinimum) / self.numberOfBins
			for i in range(1, self.numberOfBins):
				tempEdge.append(tempMinimum + i * unit)
			tempEdge.append(self.maximum)
			self.edge = tempEdge
		else:
			tempEdge = [self.minimum]
			tempEdge.extend(self.binBorders)
			tempEdge.append(self.maximum)
			self.edge = tempEdge

		self.setHandler(self.parent)
		self.parent.endElement(name)

class _handler_binBorder(_handler_base):
	def startElement(self, name, attributes):
		self.parent.binBorders.append(float(attributes['value']))

	def endElement(self, name):
		if name == 'axis':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_statistics(_handler_base):
	def startElement(self, name, attributes):
		if name == 'statistics':
			try:
				self.entries = int(attributes['entries'])
			except ValueError:
				self.entries = self.evaluator(attributes['entries'])

			self.statistic = _handler_statistic(self)
			self.mean = [0.0, 0.0, 0.0]
			self.rms = [0.0, 0.0, 0.0]

		elif name == 'statistic':
			self.setHandler(self.statistic)
			self.statistic.startElement(name, attributes)

	def endElement(self, name):
		if name == 'statistics':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_statistic(_handler_base):
	### Currently no need for checking statistc nodes.
	def startElement(self, name, attributes):
		if name == 'statistic':
			direction = str(attributes['direction'])
			if direction == 'x':
				i = 0
			elif direction == 'y':
				i = 1
			elif direction == 'z':
				i = 2
			else:
				IOException()

			try:
				self.parent.mean[i] = float(attributes['mean'])
			except ValueError:
				self.parent.mean[i] = self.evaluator(attributes['mean'])
			try:
				self.parent.rms[i] = float(attributes['rms'])
			except ValueError:
				self.parent.rms[i] = self.evaluator(attributes['rms'])

	def endElement(self, name):
		if name == 'statistics':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_histogram1d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'histogram1d':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			try:
				self.options = optionAnalyzer(str(attributes['options']))
			except KeyError:
				self.options = optionAnalyzer(None)

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.axis = _handler_axis(self)
			self.edges = [[], [], []]
			self.statistics = _handler_statistics(self)
			self.data1d = _handler_data1d_histogram1d(self)

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'axis':
			self.setHandler(self.axis)
			self.axis.startElement(name, attributes)

		elif name == 'statistics':
			### Creation.
			self.histogram1d = IHistogram1D(self.name, self.title, self.edges, self.axis.isFixedBinning, self.options)
			self.histogram1d._annotation = self.annotation.annotation

			self.setHandler(self.statistics)
			self.statistics.startElement(name, attributes)

		elif name == 'data1d':
			self.setHandler(self.data1d)
			self.data1d.startElement(name, attributes)

	def endElement(self, name):
		if name == 'axis':
			if self.axis.direction == 'x':
				self.edges[0] = self.axis.edge
			elif self.axis.direction == 'y':
				self.edges[1] = self.axis.edge
			elif self.axis.direction == 'z':
				self.edges[2] = self.axis.edge
			else:
				raise IOException('Unexpected axis direction.')

		elif name == 'histogram1d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_data1d_histogram1d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'bin1d':
			self.bin1d = _handler_bin1d_histogram1d(self)
			self.setHandler(self.bin1d)
			self.bin1d.startElement(name, attributes)

	def endElement(self, name):
		self.setHandler(self.parent)
		self.parent.endElement(name)

class _handler_bin1d_histogram1d(_handler_base):
	def startElement(self, name, attributes):
		histogram = self.parent.parent.histogram1d

		### Pick up.
		try:
			entries = int(attributes['entries'])
		except ValueError:
			entries = self.evaluator(attributes['entries'])
		try:
			height = float(attributes['height'])
		except ValueError:
			height = self.evaluator(attributes['height'])
		except KeyError:
			height = entries
		try:
			error = float(attributes['error'])
		except ValueError:
			error = self.evaluator(attributes['error'])
		except KeyError:
			error = sqrt(entries)
		if attributes.has_key('error2'):
			raise RuntimeError('error2 is not supported in histograms.')

		try:
			binNum = int(attributes['binNum'])
		except ValueError:
			binNum = self.evaluator(attributes['binNum'])

		try:
			weightedMean = float(attributes['weightedMean'])
		except ValueError:
			weightedMean = self.evaluator(attributes['weightedMean'])
		except KeyError:
			axis = histogram.axis()
			if binNum == IAxis.OVERFLOW_BIN:
				weightedMean = axis.binLowerEdge(binNum)
			elif binNum == IAxis.UNDERFLOW_BIN:
				weightedMean = axis.binUpperEdge(binNum)
			else:
				weightedMean = (axis.binUpperEdge(binNum) - axis.binLowerEdge(binNum)) / 2.0

		try:
			weightedRms = float(attributes['weightedRms'])
		except ValueError:
			weightedRms = self.evaluator(attributes['weightedRms'])
		except KeyError:
			if binNum in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
				weightedRms = 0.0
			else:
				axis = histogram.axis()
				weightedRms = self.parent.parent.statistics.rms[0] * axis.binWidth(binNum) / (axis.upperEdge() - axis.lowerEdge())

		### Fill.
		innerIndex = histogram._binEntries.getIndex(binNum + 2, 0, 0)
		histogram._binEntries.data[innerIndex] = entries
		histogram._binSumOfWeights.data[innerIndex] = height
		histogram._binSumOfErrors.data[innerIndex] = error**2
		histogram._binSumOfTorquesX.data[innerIndex] = weightedMean * height
		histogram._binSumOfInertialsX.data[innerIndex] = (weightedRms**2 + weightedMean**2) * height

	def endElement(self, name):
		if name == 'data1d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_histogram2d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'histogram2d':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			try:
				self.options = optionAnalyzer(str(attributes['options']))
			except KeyError:
				self.options = optionAnalyzer(None)

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.axis = _handler_axis(self)
			self.edges = [[], [], []]
			self.statistics = _handler_statistics(self)
			self.data2d = _handler_data2d_histogram2d(self)

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'axis':
			self.setHandler(self.axis)
			self.axis.startElement(name, attributes)

		elif name == 'statistics':
			### Creation.
			self.histogram2d = IHistogram2D(self.name, self.title, self.edges, self.axis.isFixedBinning, self.options)
			self.histogram2d._annotation = self.annotation.annotation

			self.setHandler(self.statistics)
			self.statistics.startElement(name, attributes)

		elif name == 'data2d':
			self.setHandler(self.data2d)
			self.data2d.startElement(name, attributes)

	def endElement(self, name):
		if name == 'axis':
			if self.axis.direction == 'x':
				self.edges[0] = self.axis.edge
			elif self.axis.direction == 'y':
				self.edges[1] = self.axis.edge
			elif self.axis.direction == 'z':
				self.edges[2] = self.axis.edge
			else:
				raise IOException('Unexpected axis direction.')

		elif name == 'histogram2d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_data2d_histogram2d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'bin2d':
			self.bin2d = _handler_bin2d_histogram2d(self)
			self.setHandler(self.bin2d)
			self.bin2d.startElement(name, attributes)

	def endElement(self, name):
		self.setHandler(self.parent)
		self.parent.endElement(name)

class _handler_bin2d_histogram2d(_handler_base):
	def startElement(self, name, attributes):
		histogram = self.parent.parent.histogram2d

		### Pick up.
		try:
			entries = int(attributes['entries'])
		except ValueError:
			entries = self.evaluator(attributes['entries'])
		try:
			height = float(attributes['height'])
		except ValueError:
			height = self.evaluator(attributes['height'])
		except KeyError:
			height = entries
		try:
			error = float(attributes['error'])
		except ValueError:
			error = self.evaluator(attributes['error'])
		except KeyError:
			error = sqrt(entries)
		if attributes.has_key('error2'):
			raise RuntimeError('error2 is not supported in histograms.')

		try:
			binNumX = int(attributes['binNumX'])
		except ValueError:
			binNumX = self.evaluator(attributes['binNumX'])
		try:
			binNumY = int(attributes['binNumY'])
		except ValueError:
			binNumY = self.evaluator(attributes['binNumY'])

		try:
			weightedMeanX = float(attributes['weightedMeanX'])
		except ValueError:
			weightedMeanX = self.evaluator(attributes['weightedMeanX'])
		except KeyError:
			axis = histogram.xAxis()
			if binNumX == IAxis.OVERFLOW_BIN:
				weightedMeanX = axis.binLowerEdge(binNumX)
			elif binNumX == IAxis.UNDERFLOW_BIN:
				weightedMeanX = axis.binUpperEdge(binNumX)
			else:
				weightedMeanX = (axis.binUpperEdge(binNumX) - axis.binLowerEdge(binNumX)) / 2.0
		try:
			weightedMeanY = float(attributes['weightedMeanY'])
		except ValueError:
			weightedMeanY = self.evaluator(attributes['weightedMeanY'])
		except KeyError:
			axis = histogram.yAxis()
			if binNumY == IAxis.OVERFLOW_BIN:
				weightedMeanY = axis.binLowerEdge(binNumY)
			elif binNumY == IAxis.UNDERFLOW_BIN:
				weightedMeanY = axis.binUpperEdge(binNumY)
			else:
				weightedMeanY = (axis.binUpperEdge(binNumY) - axis.binLowerEdge(binNumY)) / 2.0

		try:
			weightedRmsX = float(attributes['weightedRmsX'])
		except ValueError:
			weightedRmsX = self.evaluator(attributes['weightedRmsX'])
		except KeyError:
			if binNumX in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
				weightedRmsX = 0.0
			else:
				axis = histogram.xAxis()
				weightedRmsX = self.parent.parent.statistics.rms[0] * axis.binWidth(binNumX) / (axis.upperEdge() - axis.lowerEdge())
		try:
			weightedRmsY = float(attributes['weightedRmsY'])
		except ValueError:
			weightedRmsY = self.evaluator(attributes['weightedRmsY'])
		except KeyError:
			if binNumY in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
				weightedRmsY = 0.0
			else:
				axis = histogram.yAxis()
				weightedRmsY = self.parent.parent.statistics.rms[1] * axis.binWidth(binNumY) / (axis.upperEdge() - axis.lowerEdge())

		### Fill.
		innerIndex = histogram._binEntries.getIndex(binNumX + 2, binNumY + 2, 0)
		histogram._binEntries.data[innerIndex] = entries
		histogram._binSumOfWeights.data[innerIndex] = height
		histogram._binSumOfErrors.data[innerIndex] = error**2
		histogram._binSumOfTorquesX.data[innerIndex] = weightedMeanX * height
		histogram._binSumOfTorquesY.data[innerIndex] = weightedMeanY * height
		histogram._binSumOfInertialsX.data[innerIndex] = (weightedRmsX**2 + weightedMeanX**2) * height
		histogram._binSumOfInertialsY.data[innerIndex] = (weightedRmsY**2 + weightedMeanY**2) * height

	def endElement(self, name):
		if name == 'data2d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_histogram3d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'histogram3d':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			try:
				self.options = optionAnalyzer(str(attributes['options']))
			except KeyError:
				self.options = optionAnalyzer(None)

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.axis = _handler_axis(self)
			self.edges = [[], [], []]
			self.statistics = _handler_statistics(self)
			self.data3d = _handler_data3d_histogram3d(self)

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'axis':
			self.setHandler(self.axis)
			self.axis.startElement(name, attributes)

		elif name == 'statistics':
			### Creation.
			self.histogram3d = IHistogram3D(self.name, self.title, self.edges, self.axis.isFixedBinning, self.options)
			self.histogram3d._annotation = self.annotation.annotation

			self.setHandler(self.statistics)
			self.statistics.startElement(name, attributes)

		elif name == 'data3d':
			self.setHandler(self.data3d)
			self.data3d.startElement(name, attributes)

	def endElement(self, name):
		if name == 'axis':
			if self.axis.direction == 'x':
				self.edges[0] = self.axis.edge
			elif self.axis.direction == 'y':
				self.edges[1] = self.axis.edge
			elif self.axis.direction == 'z':
				self.edges[2] = self.axis.edge
			else:
				raise IOException('Unexpected axis direction.')

		elif name == 'histogram3d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_data3d_histogram3d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'bin3d':
			self.bin3d = _handler_bin3d_histogram3d(self)
			self.setHandler(self.bin3d)
			self.bin3d.startElement(name, attributes)

	def endElement(self, name):
		self.setHandler(self.parent)
		self.parent.endElement(name)

class _handler_bin3d_histogram3d(_handler_base):
	def startElement(self, name, attributes):
		histogram = self.parent.parent.histogram3d

		### Pick up.
		try:
			entries = int(attributes['entries'])
		except ValueError:
			entries = self.evaluator(attributes['entries'])
		try:
			height = float(attributes['height'])
		except ValueError:
			height = self.evaluator(attributes['height'])
		except KeyError:
			height = entries
		try:
			error = float(attributes['error'])
		except ValueError:
			error = self.evaluator(attributes['error'])
		except KeyError:
			error = sqrt(entries)
		if attributes.has_key('error2'):
			raise RuntimeError('error2 is not supported in histograms.')

		try:
			binNumX = int(attributes['binNumX'])
		except ValueError:
			binNumX = self.evaluator(attributes['binNumX'])
		try:
			binNumY = int(attributes['binNumY'])
		except ValueError:
			binNumY = self.evaluator(attributes['binNumY'])
		try:
			binNumZ = int(attributes['binNumZ'])
		except ValueError:
			binNumZ = self.evaluator(attributes['binNumZ'])

		try:
			weightedMeanX = float(attributes['weightedMeanX'])
		except ValueError:
			weightedMeanX = self.evaluator(attributes['weightedMeanX'])
		except KeyError:
			axis = histogram.xAxis()
			if binNumX == IAxis.OVERFLOW_BIN:
				weightedMeanX = axis.binLowerEdge(binNumX)
			elif binNumX == IAxis.UNDERFLOW_BIN:
				weightedMeanX = axis.binUpperEdge(binNumX)
			else:
				weightedMeanX = (axis.binUpperEdge(binNumX) - axis.binLowerEdge(binNumX)) / 2.0
		try:
			weightedMeanY = float(attributes['weightedMeanY'])
		except ValueError:
			weightedMeanY = self.evaluator(attributes['weightedMeanY'])
		except KeyError:
			axis = histogram.yAxis()
			if binNumY == IAxis.OVERFLOW_BIN:
				weightedMeanY = axis.binLowerEdge(binNumY)
			elif binNumY == IAxis.UNDERFLOW_BIN:
				weightedMeanY = axis.binUpperEdge(binNumY)
			else:
				weightedMeanY = (axis.binUpperEdge(binNumY) - axis.binLowerEdge(binNumY)) / 2.0
		try:
			weightedMeanZ = float(attributes['weightedMeanZ'])
		except ValueError:
			weightedMeanZ = self.evaluator(attributes['weightedMeanZ'])
		except KeyError:
			axis = histogram.zAxis()
			if binNumZ == IAxis.OVERFLOW_BIN:
				weightedMeanZ = axis.binLowerEdge(binNumZ)
			elif binNumZ == IAxis.UNDERFLOW_BIN:
				weightedMeanZ = axis.binUpperEdge(binNumZ)
			else:
				weightedMeanZ = (axis.binUpperEdge(binNumZ) - axis.binLowerEdge(binNumZ)) / 2.0

		try:
			weightedRmsX = float(attributes['weightedRmsX'])
		except ValueError:
			weightedRmsX = self.evaluator(attributes['weightedRmsX'])
		except KeyError:
			if binNumX in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
				weightedRmsX = 0.0
			else:
				axis = histogram.xAxis()
				weightedRmsX = self.parent.parent.statistics.rms[0] * axis.binWidth(binNumX) / (axis.upperEdge() - axis.lowerEdge())
		try:
			weightedRmsY = float(attributes['weightedRmsY'])
		except ValueError:
			weightedRmsY = self.evaluator(attributes['weightedRmsY'])
		except KeyError:
			if binNumY in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
				weightedRmsY = 0.0
			else:
				axis = histogram.yAxis()
				weightedRmsY = self.parent.parent.statistics.rms[1] * axis.binWidth(binNumY) / (axis.upperEdge() - axis.lowerEdge())
		try:
			weightedRmsZ = float(attributes['weightedRmsZ'])
		except ValueError:
			weightedRmsZ = self.evaluator(attributes['weightedRmsZ'])
		except KeyError:
			if binNumZ in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
				weightedRmsZ = 0.0
			else:
				axis = histogram.zAxis()
				weightedRmsZ = self.parent.parent.statistics.rms[2] * axis.binWidth(binNumZ) / (axis.upperEdge() - axis.lowerEdge())

		### Fill.
		innerIndex = histogram._binEntries.getIndex(binNumX + 2, binNumY + 2, binNumZ + 2)
		histogram._binEntries.data[innerIndex] = entries
		histogram._binSumOfWeights.data[innerIndex] = height
		histogram._binSumOfErrors.data[innerIndex] = error**2
		histogram._binSumOfTorquesX.data[innerIndex] = weightedMeanX * height
		histogram._binSumOfTorquesY.data[innerIndex] = weightedMeanY * height
		histogram._binSumOfTorquesZ.data[innerIndex] = weightedMeanZ * height
		histogram._binSumOfInertialsX.data[innerIndex] = (weightedRmsX**2 + weightedMeanX**2) * height
		histogram._binSumOfInertialsY.data[innerIndex] = (weightedRmsY**2 + weightedMeanY**2) * height
		histogram._binSumOfInertialsZ.data[innerIndex] = (weightedRmsZ**2 + weightedMeanZ**2) * height

	def endElement(self, name):
		if name == 'data3d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_tuple(_handler_base):
	def startElement(self, name, attributes):
		if name == 'tuple':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			try:
				self.options = optionAnalyzer(str(attributes['options']))
			except KeyError:
				self.options = optionAnalyzer(None)

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.columns = _handler_columns(self)
			self.rows = _handler_rows(self)

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'columns':
			self.setHandler(self.columns)
			self.columns.startElement(name, attributes)

		elif name == 'rows':
			self.setHandler(self.rows)
			self.rows.ituple = self.ituple
			self.rows.startElement(name, attributes)

	def endElement(self, name):
		if name == 'columns':
			### Creation.
			tf = ITupleFactory(self.parent.parent.tree)
			self.ituple = tf._create(self.name, self.title, self.columns.expression, optionConstructor(self.options))
			self.ituple._annotation = self.annotation.annotation

		elif name == 'tuple':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_columns(_handler_base):
	def startElement(self, name, attributes):
		if name == 'columns':
			self.expression = ''
			self.columnNamesList = []
			self.columnTypesList = []

		elif name == 'column':
			self.column = _handler_column(self)
			self.setHandler(self.column)
			self.column.startElement(name, attributes)

	def endElement(self, name):
		for i, columnName in enumerate(self.columnNamesList):
			self.expression += '%s %s; ' % (self.columnTypesList[i], columnName)
		self.expression = self.expression[:-2]
		self.setHandler(self.parent)
		self.parent.endElement(name)

class _handler_column(_handler_base):
	def startElement(self, name, attributes):
		### Pick up.
		columnName = str(attributes['name']).strip()
		if columnName[-1] == '=':
			columnName = columnName[:-1]
		try:
			columnType = str(attributes['type'])
		except KeyError:
			columnType = PTypes.Double.TYPE

		### For Java implementation compatibility.
		if columnType == 'java.lang.String':
			columnType = PTypes.String.TYPE
		elif columnType == 'java.lang.Object':
			columnType = PTypes.Object.TYPE

		if columnType == PTypes.Double.TYPE:
			self.parent.columnTypesList.append(PTypes.Double.TYPE)
		elif columnType == PTypes.Float.TYPE:
			self.parent.columnTypesList.append(PTypes.Float.TYPE)
		elif columnType == PTypes.Integer.TYPE:
			self.parent.columnTypesList.append(PTypes.Integer.TYPE)
		elif columnType == PTypes.Short.TYPE:
			self.parent.columnTypesList.append(PTypes.Short.TYPE)
		elif columnType == PTypes.Long.TYPE:
			self.parent.columnTypesList.append(PTypes.Long.TYPE)
		elif columnType == PTypes.Character.TYPE:
			if '=' in columnName:
				columnNameList = columnName.split('=')
				columnNameList[1] = '"%s"' % columnNameList[1]
				columnName = '='.join(columnNameList)
			self.parent.columnTypesList.append(PTypes.Character.TYPE)
		elif columnType == PTypes.Byte.TYPE:
			self.parent.columnTypesList.append(PTypes.Byte.TYPE)
		elif columnType == PTypes.Boolean.TYPE:
			self.parent.columnTypesList.append(PTypes.Boolean.TYPE)
		elif columnType == PTypes.String.TYPE:
			if '=' in columnName:
				columnNameList = columnName.split('=')
				columnNameList[1] = '"%s"' % columnNameList[1]
				columnName = '='.join(columnNameList)
			self.parent.columnTypesList.append(PTypes.String.TYPE)
		elif columnType == PTypes.Object.TYPE:
			self.parent.columnTypesList.append(PTypes.Object.TYPE)
		elif columnType == PTypes.ITuple.TYPE:
			self.parent.columnTypesList.append(PTypes.ITuple.TYPE)
		else:
			raise IOException('Unexpected column type "%s"' % columnType)
		self.parent.columnNamesList.append(columnName)

	def endElement(self, name):
		if name == 'columns':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_rows(_handler_base):
	def startElement(self, name, attributes):
		if name == 'row':
			self.row.column = 0
			self.setHandler(self.row)
			self.row.startElement(name, attributes)

		elif name == 'rows':
			self.row = _handler_row(self)
			self.row.ituple = self.ituple
			self.row.converters = self.ituple._columnConverters

	def endElement(self, name):
		if name == 'rows':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_row(_handler_base):
	def startElement(self, name, attributes):
		if name == 'entry':
			self.ituple._rowBuffer[self.column] = self.converters[self.column](attributes['value'])

		elif name == 'entryITuple':
			self.entry = _handler_entryITuple(self)
			self.entry.ituple = self.ituple.getTuple(self.column)
			self.setHandler(self.entry)
			self.entry.startElement(name, attributes)

	def endElement(self, name):
		if name == 'row':
			self.ituple.addRow()
			self.setHandler(self.parent)
			self.parent.endElement(name)

		else:
			self.column += 1

class _handler_entry(_handler_base):
	"""Currently this class is not used."""
	pass

class _handler_entryITuple(_handler_base):
	def startElement(self, name, attributes):
		if name == 'row':
			self.row.column = 0
			self.setHandler(self.row)
			self.row.startElement(name, attributes)

		elif name == 'entryITuple':
			self.row = _handler_row(self)
			self.row.ituple = self.ituple
			self.row.converters = self.ituple._columnConverters

	def endElement(self, name):
		if name == 'entryITuple':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_cloud1d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'cloud1d':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			try:
				self.options = optionAnalyzer(str(attributes['options']))
			except KeyError:
				self.options = optionAnalyzer(None)

			self.maxEntries = int(attributes['maxEntries'])

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.entries1d = _handler_entries1d(self)
			self.histogram1d = _handler_histogram1d(self)
			self.hasEntries = False

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'entries1d':
			### Create.
			self.cloud1d = ICloud1D(self.name, self.title, self.maxEntries, self.options)
			self.cloud1d._annotation = self.annotation.annotation
			self.setHandler(self.entries1d)
			self.entries1d.startElement(name, attributes)
			self.hasEntries = True

		elif name == 'histogram1d':
			### Create.
			if self.hasEntries == False:
				self.cloud1d = ICloud1D(self.name, self.title, self.maxEntries, self.options)
				self.cloud1d._annotation = self.annotation.annotation
			self.setHandler(self.histogram1d)
			self.histogram1d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'cloud1d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

		elif name == 'annotation':
			pass

		elif name == 'entries1d':
			pass

		elif name == 'histogram1d':
			histogram1d = self.histogram1d.histogram1d
			cloud1d = self.cloud1d
			cloud1d._histogram = histogram1d
			cloud1d._isConverted = True
			if self.hasEntries == False:
				cloud1d._sumOfWeights = histogram1d.sumAllBinHeights()
				cloud1d._lowerEdges[0] = histogram1d.axis().lowerEdge()
				cloud1d._upperEdges[0] = histogram1d.axis().upperEdge()
				sumOfWeights = cloud1d.sumOfWeights()
				cloud1d._sumOfTorques[0] = histogram1d.mean() * sumOfWeights
				cloud1d._sumOfInertials[0] = (histogram1d.rms()**2 + histogram1d.mean()**2) * sumOfWeights

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

class _handler_entries1d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'entries1d':
			pass

		elif name == 'entry1d':
			self.entry1d = _handler_entry1d(self)
			self.setHandler(self.entry1d)
			self.entry1d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'entries1d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_entry1d(_handler_base):
	def startElement(self, name, attributes):
		try:
			weight = float(attributes['weight'])
		except ValueError:
			weight = self.evaluator(attributes['weight'])
		except KeyError:
			weight = 1.0

		try:
			valueX = float(attributes['valueX'])
		except ValueError:
			valueX = self.evaluator(attributes['valueX'])

		### Fill.
		self.parent.parent.cloud1d.fill(valueX, weight)

	def endElement(self, name):
		if name == 'entries1d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_cloud2d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'cloud2d':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			try:
				self.options = optionAnalyzer(str(attributes['options']))
			except KeyError:
				self.options = optionAnalyzer(None)

			self.maxEntries = int(attributes['maxEntries'])

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.entries2d = _handler_entries2d(self)
			self.histogram2d = _handler_histogram2d(self)
			self.hasEntries = False

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'entries2d':
			### Create.
			self.cloud2d = ICloud2D(self.name, self.title, self.maxEntries, self.options)
			self.cloud2d._annotation = self.annotation.annotation
			self.setHandler(self.entries2d)
			self.entries2d.startElement(name, attributes)
			self.hasEntries = True

		elif name == 'histogram2d':
			### Create.
			if self.hasEntries == False:
				self.cloud2d = ICloud2D(self.name, self.title, self.maxEntries, self.options)
				self.cloud2d._annotation = self.annotation.annotation
			self.setHandler(self.histogram2d)
			self.histogram2d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'cloud2d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

		elif name == 'annotation':
			pass

		elif name == 'entries2d':
			pass

		elif name == 'histogram2d':
			histogram2d = self.histogram2d.histogram2d
			cloud2d = self.cloud2d
			cloud2d._histogram = histogram2d
			cloud2d._isConverted = True
			if self.hasEntries == False:
				cloud2d._sumOfWeights = histogram2d.sumAllBinHeights()
				cloud2d._lowerEdges[0] = histogram2d.xAxis().lowerEdge()
				cloud2d._lowerEdges[1] = histogram2d.yAxis().lowerEdge()
				cloud2d._upperEdges[0] = histogram2d.xAxis().upperEdge()
				cloud2d._upperEdges[1] = histogram2d.yAxis().upperEdge()
				sumOfWeights = cloud2d.sumOfWeights()
				cloud2d._sumOfTorques[0] = histogram2d.meanX() * sumOfWeights
				cloud2d._sumOfTorques[1] = histogram2d.meanY() * sumOfWeights
				cloud2d._sumOfInertials[0] = (histogram2d.rmsX()**2 + histogram2d.meanX()**2) * sumOfWeights
				cloud2d._sumOfInertials[1] = (histogram2d.rmsY()**2 + histogram2d.meanY()**2) * sumOfWeights

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

class _handler_entries2d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'entries2d':
			pass

		elif name == 'entry2d':
			self.entry2d = _handler_entry2d(self)
			self.setHandler(self.entry2d)
			self.entry2d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'entries2d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_entry2d(_handler_base):
	def startElement(self, name, attributes):
		try:
			weight = float(attributes['weight'])
		except ValueError:
			weight = self.evaluator(attributes['weight'])
		except KeyError:
			weight = 1.0

		try:
			valueX = float(attributes['valueX'])
		except ValueError:
			valueX = self.evaluator(attributes['valueX'])
		try:
			valueY = float(attributes['valueY'])
		except ValueError:
			valueY = self.evaluator(attributes['valueY'])

		### Fill.
		self.parent.parent.cloud2d.fill(valueX, valueY, weight)

	def endElement(self, name):
		if name == 'entries2d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_cloud3d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'cloud3d':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			try:
				self.options = optionAnalyzer(str(attributes['options']))
			except KeyError:
				self.options = optionAnalyzer(None)

			self.maxEntries = int(attributes['maxEntries'])

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.entries3d = _handler_entries3d(self)
			self.histogram3d = _handler_histogram3d(self)
			self.hasEntries = False

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'entries3d':
			### Create.
			self.cloud3d = ICloud3D(self.name, self.title, self.maxEntries, self.options)
			self.cloud3d._annotation = self.annotation.annotation
			self.setHandler(self.entries3d)
			self.entries3d.startElement(name, attributes)
			self.hasEntries = True

		elif name == 'histogram3d':
			### Create.
			if self.hasEntries == False:
				self.cloud3d = ICloud3D(self.name, self.title, self.maxEntries, self.options)
				self.cloud3d._annotation = self.annotation.annotation
			self.setHandler(self.histogram3d)
			self.histogram3d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'cloud3d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

		elif name == 'annotation':
			pass

		elif name == 'entries3d':
			pass

		elif name == 'histogram3d':
			histogram3d = self.histogram3d.histogram3d
			cloud3d = self.cloud3d
			cloud3d._histogram = histogram3d
			cloud3d._isConverted = True
			if self.hasEntries == False:
				cloud3d._sumOfWeights = histogram3d.sumAllBinHeights()
				cloud3d._lowerEdges[0] = histogram3d.xAxis().lowerEdge()
				cloud3d._lowerEdges[1] = histogram3d.yAxis().lowerEdge()
				cloud3d._lowerEdges[2] = histogram3d.zAxis().lowerEdge()
				cloud3d._upperEdges[0] = histogram3d.xAxis().upperEdge()
				cloud3d._upperEdges[1] = histogram3d.yAxis().upperEdge()
				cloud3d._upperEdges[2] = histogram3d.zAxis().upperEdge()
				sumOfWeights = cloud3d.sumOfWeights()
				cloud3d._sumOfTorques[0] = histogram3d.meanX() * sumOfWeights
				cloud3d._sumOfTorques[1] = histogram3d.meanY() * sumOfWeights
				cloud3d._sumOfTorques[2] = histogram3d.meanZ() * sumOfWeights
				cloud3d._sumOfInertials[0] = (histogram3d.rmsX()**2 + histogram3d.meanX()**2) * sumOfWeights
				cloud3d._sumOfInertials[1] = (histogram3d.rmsY()**2 + histogram3d.meanY()**2) * sumOfWeights
				cloud3d._sumOfInertials[2] = (histogram3d.rmsZ()**2 + histogram3d.meanZ()**2) * sumOfWeights

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

class _handler_entries3d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'entries3d':
			pass

		elif name == 'entry3d':
			self.entry3d = _handler_entry3d(self)
			self.setHandler(self.entry3d)
			self.entry3d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'entries3d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_entry3d(_handler_base):
	def startElement(self, name, attributes):
		try:
			weight = float(attributes['weight'])
		except ValueError:
			weight = self.evaluator(attributes['weight'])
		except KeyError:
			weight = 1.0

		try:
			valueX = float(attributes['valueX'])
		except ValueError:
			valueX = self.evaluator(attributes['valueX'])
		try:
			valueY = float(attributes['valueY'])
		except ValueError:
			valueY = self.evaluator(attributes['valueY'])
		try:
			valueZ = float(attributes['valueZ'])
		except ValueError:
			valueZ = self.evaluator(attributes['valueZ'])

		### Fill.
		self.parent.parent.cloud3d.fill(valueX, valueY, valueZ, weight)

	def endElement(self, name):
		if name == 'entries3d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_profile1d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'profile1d':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			try:
				self.options = optionAnalyzer(str(attributes['options']))
			except KeyError:
				self.options = optionAnalyzer(None)

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.axis = _handler_axis(self)
			self.edges = [[], [], []]
			self.statistics = _handler_statistics(self)
			self.data1d = _handler_data1d_profile1d(self)

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'axis':
			self.setHandler(self.axis)
			self.axis.startElement(name, attributes)

		elif name == 'statistics':
			### Creation.
			self.profile1d = IProfile1D(self.name, self.title, self.edges, self.axis.isFixedBinning, None, None, self.options)
			self.profile1d._annotation = self.annotation.annotation

			self.setHandler(self.statistics)
			self.statistics.startElement(name, attributes)

		elif name == 'data1d':
			self.setHandler(self.data1d)
			self.data1d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'profile1d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

		elif name == 'annotation':
			pass

		elif name == 'axis':
			if self.axis.direction == 'x':
				self.edges[0] = self.axis.edge
			elif self.axis.direction == 'y':
				self.edges[1] = self.axis.edge
			elif self.axis.direction == 'z':
				self.edges[2] = self.axis.edge
			else:
				raise IllegalArgumentException('Unexpected axis direction.')

		elif name == 'statistics':
			pass

		elif name == 'data1d':
			pass

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

class _handler_data1d_profile1d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'data1d':
			pass

		elif name == 'bin1d':
			self.bin1d = _handler_bin1d_profile1d(self)
			self.setHandler(self.bin1d)
			self.bin1d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		self.setHandler(self.parent)
		self.parent.endElement(name)

class _handler_bin1d_profile1d(_handler_base):
	def startElement(self, name, attributes):
		profile = self.parent.parent.profile1d

		### Pick up.
		try:
			entries = int(attributes['entries'])
		except ValueError:
			entries = self.evaluator(attributes['entries'])
		try:
			height = float(attributes['height'])
		except ValueError:
			height = self.evaluator(attributes['height'])
		except KeyError:
			height = entries
		try:
			error = float(attributes['error'])
		except ValueError:
			error = self.evaluator(attributes['error'])
		except KeyError:
			error = sqrt(entries)
		if attributes.has_key('error2'):
			raise RuntimeError('error2 is not supported in histograms.')

		try:
			binNum = int(attributes['binNum'])
		except ValueError:
			binNum = self.evaluator(attributes['binNum'])

		try:
			weightedMean = float(attributes['weightedMean'])
		except ValueError:
			weightedMean = self.evaluator(attributes['weightedMean'])
		except KeyError:
			axis = profile.axis()
			if binNum == IAxis.OVERFLOW_BIN:
				weightedMean = axis.binLowerEdge(binNum)
			elif binNum == IAxis.UNDERFLOW_BIN:
				weightedMean = axis.binUpperEdge(binNum)
			else:
				weightedMean = (axis.binUpperEdge(binNum) - axis.binLowerEdge(binNum)) / 2.0

		try:
			weightedRms = float(attributes['weightedRms'])
		except ValueError:
			weightedRms = self.evaluator(attributes['weightedRms'])
		except KeyError:
			if binNum in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
				weightedRms = 0.0
			else:
				axis = profile.axis()
				weightedRms = self.parent.parent.statistics.rms[0] * axis.binWidth(binNum) / (axis.upperEdge() - axis.lowerEdge())

		try:
			rms = float(attributes['rms'])
		except ValueError:
			rms = self.evaluator(attributes['rms'])
		except KeyError:
			raise IllegalArgumentException('PAIDA needs "rms" in "profile1d.data1d.bin1d".')

		### Fill.
		innerIndex = profile._binEntries.getIndex(binNum + 2, 0)
		profile._binEntries.data[innerIndex] = entries
		if height < 0:
			profile._binSumOfTorquesY.data[innerIndex] = -(height**2 / error**2)
		else:
			profile._binSumOfTorquesY.data[innerIndex] = height**2 / error**2
		binSumOfWeights = profile._binSumOfTorquesY.data[innerIndex] / height
		profile._binSumOfWeights.data[innerIndex] = binSumOfWeights
		profile._binSumOfTorquesX.data[innerIndex] = binSumOfWeights * weightedMean
		profile._binSumOfTorquesY.data[innerIndex] = binSumOfWeights * height
		profile._binSumOfInertialsX.data[innerIndex] = binSumOfWeights * (weightedRms**2 + weightedMean**2)
		profile._binSumOfInertialsY.data[innerIndex] = binSumOfWeights * (rms**2 + height**2)

	def endElement(self, name):
		if name == 'data1d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_profile2d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'profile2d':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			try:
				self.options = optionAnalyzer(str(attributes['options']))
			except KeyError:
				self.options = optionAnalyzer(None)

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.axis = _handler_axis(self)
			self.edges = [[], [], []]
			self.statistics = _handler_statistics(self)
			self.data2d = _handler_data2d_profile2d(self)

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'axis':
			self.setHandler(self.axis)
			self.axis.startElement(name, attributes)

		elif name == 'statistics':
			### Creation.
			self.profile2d = IProfile2D(self.name, self.title, self.edges, self.axis.isFixedBinning, None, None, self.options)
			self.profile2d._annotation = self.annotation.annotation

			self.setHandler(self.statistics)
			self.statistics.startElement(name, attributes)

		elif name == 'data2d':
			self.setHandler(self.data2d)
			self.data2d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'profile2d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

		elif name == 'annotation':
			pass

		elif name == 'axis':
			if self.axis.direction == 'x':
				self.edges[0] = self.axis.edge
			elif self.axis.direction == 'y':
				self.edges[1] = self.axis.edge
			elif self.axis.direction == 'z':
				self.edges[2] = self.axis.edge
			else:
				raise IllegalArgumentException('Unexpected axis direction.')

		elif name == 'statistics':
			pass

		elif name == 'data2d':
			pass

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

class _handler_data2d_profile2d(_handler_base):
	def startElement(self, name, attributes):
		if name == 'data2d':
			pass

		elif name == 'bin2d':
			self.bin2d = _handler_bin2d_profile2d(self)
			self.setHandler(self.bin2d)
			self.bin2d.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		self.setHandler(self.parent)
		self.parent.endElement(name)

class _handler_bin2d_profile2d(_handler_base):
	def startElement(self, name, attributes):
		profile = self.parent.parent.profile2d

		### Pick up.
		try:
			entries = int(attributes['entries'])
		except ValueError:
			entries = self.evaluator(attributes['entries'])
		try:
			height = float(attributes['height'])
		except ValueError:
			height = self.evaluator(attributes['height'])
		except KeyError:
			height = entries
		try:
			error = float(attributes['error'])
		except ValueError:
			error = self.evaluator(attributes['error'])
		except KeyError:
			error = sqrt(entries)
		if attributes.has_key('error2'):
			raise RuntimeError('error2 is not supported in histograms.')

		try:
			binNumX = int(attributes['binNumX'])
		except ValueError:
			binNumX = self.evaluator(attributes['binNumX'])
		try:
			binNumY = int(attributes['binNumY'])
		except ValueError:
			binNumY = self.evaluator(attributes['binNumY'])

		try:
			weightedMeanX = float(attributes['weightedMeanX'])
		except ValueError:
			weightedMeanX = self.evaluator(attributes['weightedMeanX'])
		except KeyError:
			axis = profile.xAxis()
			if binNumX == IAxis.OVERFLOW_BIN:
				weightedMeanX = axis.binLowerEdge(binNumX)
			elif binNumX == IAxis.UNDERFLOW_BIN:
				weightedMeanX = axis.binUpperEdge(binNumX)
			else:
				weightedMeanX = (axis.binUpperEdge(binNumX) - axis.binLowerEdge(binNumX)) / 2.0
		try:
			weightedMeanY = float(attributes['weightedMeanY'])
		except ValueError:
			weightedMeanY = self.evaluator(attributes['weightedMeanY'])
		except KeyError:
			axis = profile.yAxis()
			if binNumY == IAxis.OVERFLOW_BIN:
				weightedMeanY = axis.binLowerEdge(binNumY)
			elif binNumY == IAxis.UNDERFLOW_BIN:
				weightedMeanY = axis.binUpperEdge(binNumY)
			else:
				weightedMeanY = (axis.binUpperEdge(binNumY) - axis.binLowerEdge(binNumY)) / 2.0

		try:
			weightedRmsX = float(attributes['weightedRmsX'])
		except ValueError:
			weightedRmsX = self.evaluator(attributes['weightedRmsX'])
		except KeyError:
			if binNumX in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
				weightedRmsX = 0.0
			else:
				axis = profile.xAxis()
				weightedRmsX = self.parent.parent.statistics.rms[0] * axis.binWidth(binNumX) / (axis.upperEdge() - axis.lowerEdge())
		try:
			weightedRmsY = float(attributes['weightedRmsY'])
		except ValueError:
			weightedRmsY = self.evaluator(attributes['weightedRmsY'])
		except KeyError:
			if binNumY in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
				weightedRmsY = 0.0
			else:
				axis = profile.yAxis()
				weightedRmsY = self.parent.parent.statistics.rms[1] * axis.binWidth(binNumY) / (axis.upperEdge() - axis.lowerEdge())

		try:
			rms = float(attributes['rms'])
		except ValueError:
			rms = self.evaluator(attributes['rms'])
		except KeyError:
			raise IllegalArgumentException('PAIDA needs "rms" in "profile2d.data2d.bin2d".')

		### Fill.
		innerIndex = profile._binEntries.getIndex(binNumX + 2, binNumY + 2)
		profile._binEntries.data[innerIndex] = entries
		if height < 0:
			profile._binSumOfTorquesZ.data[innerIndex] = -(height**2 / error**2)
		else:
			profile._binSumOfTorquesZ.data[innerIndex] = height**2 / error**2
		binSumOfWeights = profile._binSumOfTorquesZ.data[innerIndex] / height
		profile._binSumOfWeights.data[innerIndex] = binSumOfWeights
		profile._binSumOfTorquesX.data[innerIndex] = binSumOfWeights * weightedMeanX
		profile._binSumOfTorquesY.data[innerIndex] = binSumOfWeights * weightedMeanY
		profile._binSumOfTorquesZ.data[innerIndex] = binSumOfWeights * height
		profile._binSumOfInertialsX.data[innerIndex] = binSumOfWeights * (weightedRmsX**2 + weightedMeanX**2)
		profile._binSumOfInertialsY.data[innerIndex] = binSumOfWeights * (weightedRmsY**2 + weightedMeanY**2)
		profile._binSumOfInertialsZ.data[innerIndex] = binSumOfWeights * (rms**2 + height**2)

	def endElement(self, name):
		if name == 'data2d':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_dataPointSet(_handler_base):
	def startElement(self, name, attributes):
		if name == 'dataPointSet':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			self.dimension = int(attributes['dimension'])

			### Create.
			self.dataPointSet = IDataPointSet(self.name, self.title, self.dimension)

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.dataPoint = _handler_dataPoint(self)

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'dataPoint':
			self.setHandler(self.dataPoint)
			self.dataPoint.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'dataPointSet':
			self.setHandler(self.parent)
			self.parent.endElement(name)

		elif name == 'annotation':
			self.dataPointSet._annotation = self.annotation.annotation

		elif name == 'dataPoint':
			pass

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

class _handler_dataPoint(_handler_base):
	def startElement(self, name, attributes):
		if name == 'dataPoint':
			self.dataPoint = self.parent.dataPointSet.addPoint()
			self.currentCoord = 0

		elif name == 'measurement':
			self.measurement = _handler_measurement(self)
			self.setHandler(self.measurement)
			self.measurement.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		self.setHandler(self.parent)
		self.parent.endElement(name)

class _handler_measurement(_handler_base):
	def startElement(self, name, attributes):
		### Pick up.
		value = float(attributes['value'])
		try:
			errorPlus = float(attributes['errorPlus'])
		except ValueError:
			errorPlus = self.evaluator(attributes['errorPlus'])
		except KeyError:
			errorPlus = 0.0

		try:
			errorMinus = float(attributes['errorMinus'])
		except ValueError:
			errorMinus = self.evaluator(attributes['errorMinus'])
		except KeyError:
			errorMinus = errorPlus

		### Fill.
		measurement = self.parent.dataPoint.coordinate(self.parent.currentCoord)
		measurement.setValue(value)
		measurement.setErrorPlus(errorPlus)
		measurement.setErrorMinus(errorMinus)

	def endElement(self, name):
		if name == 'dataPoint':
			self.setHandler(self.parent)
			self.parent.endElement(name)
		elif name == 'measurement':
			self.parent.currentCoord += 1

class _handler_function(_handler_base):
	def startElement(self, name, attributes):
		if name == 'function':
			self.name = str(attributes['name'])

			try:
				self.title = str(attributes['title'])
			except KeyError:
				self.title = self.name

			try:
				self.path = str(attributes['path'])
			except KeyError:
				self.path = '/'

			if attributes.has_key('isNormalized'):
				if attributes['isNormalized'] == u'true':
					self.isNormalized = True
				else:
					self.isNormalized = False
			else:
				self.isNormalized = False

			### Initialization.
			self.annotation = _handler_annotation(self)
			self.annotation.annotation._addItem('Title', self.title, True)
			self.codelet = _handler_codelet(self)
			self.arguments = _handler_arguments(self)
			self.parameters = _handler_parameters(self)

		elif name == 'annotation':
			self.setHandler(self.annotation)
			self.annotation.startElement(name, attributes)

		elif name == 'codelet':
			self.setHandler(self.codelet)
			self.codelet.startElement(name, attributes)

		elif name == 'arguments':
			self.setHandler(self.arguments)
			self.arguments.startElement(name, attributes)

		elif name == 'parameters':
			self.setHandler(self.parameters)
			self.parameters.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'function':
			self.setHandler(self.parent)
			self.parent.endElement(name)

		elif name == 'annotation':
			pass

		elif name == 'codelet':
			### Creation.
			name = self.name
			codelet = self.codelet.codelet
			if codelet.count(':') == 8:
				### Old codelet expression.
				codeletList = codelet.split(':')
				newCodeletList = []
				newCodeletList.append('codelet')
				newCodeletList.append(codeletList[7])
				newCodeletList.append('verbatim')
				newCodeletList.append('py')
				newCodeletList.append(codeletList[4])
				newCodeletList.append(codeletList[5])
				newCodeletList.append(codeletList[6])
				newCodeletList.append(codeletList[8])
				codelet = ':'.join(newCodeletList)
			self.function = self.functionFactory._createCopy(codelet, name, inner = True)

		elif name == 'arguments':
			pass

		elif name == 'parameters':
			pass

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

class _handler_codelet(_handler_base):
	def startElement(self, name, attributes):
		### Pick up.
		self.codelet = ''
		self.start = True

	def endElement(self, name):
		if name == 'codelet':
			self.start = False

			lines = self.codelet.splitlines()
			oneLine = ''
			for line in lines:
				oneLine += str(line)
			self.codelet = oneLine.strip()

			self.setHandler(self.parent)
			self.parent.endElement(name)
		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def characters(self, content):
		if self.start:
			self.codelet += content

class _handler_arguments(_handler_base):
	### Currently PAIDA don't need argument element.
	def startElement(self, name, attributes):
		pass

	def endElement(self, name):
		if name == 'arguments':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class _handler_parameters(_handler_base):
	def startElement(self, name, attributes):
		if name == 'parameters':
			self.parameterNames = []
			self.parameterValues = []

		elif name == 'parameter':
			self.parameter = _handler_parameter(self)
			self.setHandler(self.parameter)
			self.parameter.startElement(name, attributes)

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

	def endElement(self, name):
		if name == 'parameters':
			for i in range(len(self.parameterNames)):
				self.parent.function.setParameter(self.parameterNames[i], self.parameterValues[i])

			self.setHandler(self.parent)
			self.parent.endElement(name)

		elif name == 'parameter':
			pass

		else:
			raise IllegalArgumentException('Unexpected element name "%s"' % name)

class _handler_parameter(_handler_base):
	def startElement(self, name, attributes):
		self.parent.parameterNames.append(str(attributes['name']))
		try:
			self.parent.parameterValues.append(float(attributes['value']))
		except ValueError:
			self.parent.parameterValues.append(self.evaluator(attributes['value']))

	def endElement(self, name):
		if name == 'parameters':
			self.setHandler(self.parent)
			self.parent.endElement(name)

class ITree:
	_entities = {'"': '&quot;'}

	def __init__(self, fileName, storeType, readOnly, options):
		self._fileName = fileName
		self._storeType = storeType
		self._readOnly = readOnly
		self._options = options
		self._root = IManagedObject('', None)
		self._pwd = self._root
		self.setOverwrite(True)

		self._setGuiTree(PRoot.getRoot()._requestTree())

		guiTree = self._getGuiTree()
		if fileName == None:
			### Title.
			guiTree.setTitle('PAIDA tree')
		else:
			### Title.
			guiTree.setTitle(fileName)

			### Check if the file is zipped or normal.
			try:
				import gzip
				### Jython2.1 fails to gzip.open with 'r' argument.
				#fileObj = gzip.open(fileName, 'r')
				fileObj = gzip.open(fileName)
				fileObj.read(1)
				try:
					fileObj.seek(0)
				except AttributeError:
					### Jython2.1 does not have 'seek()'.
					fileObj.close()
					fileObj = gzip.open(fileName)
			except ImportError:
				print 'PAIDA: gzip module is unavailable.'
				print 'PAIDA: all files are treated as unzipped.'
				fileObj = file(fileName, 'r')
			except IOError:
				fileObj = file(fileName, 'r')

			### Read object data from xml file.
			parser = xml.sax.make_parser()

			### Jython2.1 needs this line.
			parser.setFeature(xml.sax.handler.feature_namespaces, 0)

			handler = _handler_initial(parser, self)
			parser.setContentHandler(handler)
			parser.setEntityResolver(_handler_EntityResolver())
			try:
				parser.parse(fileObj)
			except xml.sax._exceptions.SAXParseException:
				errorMessage = 'The file "%s" is broken. Stopped reading.' % fileName
				if readOnly:
					raise IOError, errorMessage
				else:
					print errorMessage
			fileObj.close()

	def _setGuiTree(self, guiTree):
		self._guiTree = guiTree

	def _getGuiTree(self):
		return self._guiTree

	def _treeUpdate(self, block):
		self._getGuiTree().redrawTree(block, self)

	def _show(self):
		self._getGuiTree().setShow(True)

	def _hide(self):
		self._getGuiTree().setShow(False)

	def isReadOnly(self):
		return self._readOnly

	def storeName(self):
		if self._fileName == None:
			return ''
		else:
			return self._fileName

	def _internalFind(self, path, force = False, checkMode = False):
		currentPosition = self._pwd
		pathItems = path.split('/')
		if pathItems[0] == '':
			currentPosition = self._root
		for pathItem in pathItems:
			if pathItem == '':
				pass
			elif pathItem == '..':
				if currentPosition._parent == None:
					###PWD is already root.
					pass
				else:
					currentPosition = currentPosition._parent
			elif pathItem == '.':
				pass
			else:
				for child in currentPosition._children:
					if child._name == pathItem:
						currentPosition = child
						break
				else:
					if force:
						newChild = IManagedObject(pathItem, currentPosition)
						currentPosition._children.append(newChild)
						currentPosition = newChild
					else:
						if checkMode:
							return None
						else:
							raise IllegalArgumentException()
		return currentPosition

	def _getPath(self, position, baseDirectory):
		if position == baseDirectory:
			return ''
		result = ''
		currentPosition = position
		while 1:
			if currentPosition == baseDirectory:
				###Reached to the path-string-starting directory.
				return result[:-1]
			else:
				result = currentPosition._name + '/' + result
				currentPosition = currentPosition._parent

	def cd(self, path, update = True, block = True):
		position = self._internalFind(path)
		if position._instance == None:
			self._pwd = position
			if update:
				self._treeUpdate(block)
		else:
			###Not directory.
			raise IllegalArgumentException()

	def find(self, path):
		position = self._internalFind(path)
		if position._instance == None:
			###Directory.
			return position
		else:
			###Analysis object.
			return position._instance

	def _getPwd(self):
		return self._pwd

	def pwd(self):
		return '/' + self._getPath(self._pwd, self._root)

	def _listObjects(self, path = '.', recursive = False):
		result = []
		position = self._internalFind(path)
		if position._instance != None:
			###Analysis object.
			result.append(position)
		else:
			subDirectories = []
			for child in position._children:
				result.append(child)
				if child._instance == None:
					###Subdirectory.
					subDirectories.append(child)
			if recursive:
				for subDirectory in subDirectories:
					result = self._listObjectsWalker(subDirectory, result)
		return result

	def _listObjectsWalker(self, directory, result):
		subDirectories = []
		for child in directory._children:
			result.append(child)
			if child._instance == None:
				###Subdirectory.
				subDirectories.append(child)
		for subDirectory in subDirectories:
			result = self._listObjectsWalker(subDirectory, result)
		return result

	def ls(self, path = '.', recursive = False, stream = sys.stdout):
		output = ''
		if path == '/':
			objectList = self._listObjects('/', recursive)
			for object in objectList:
				output += self._getPath(object, self._root) + os.linesep
		else:
			basePosition = self._internalFind(path)
			objectList = self._listObjects(path, recursive)
			for object in objectList:
				relative = self._getPath(object, basePosition)
				if object._instance == None:
					output += relative + '/' + os.linesep
				else:
					output += relative + os.linesep
		stream.write(output)

	def listObjectNames(self, path = '.', recursive = False):
		objectList = self._listObjects(path, recursive)
		result = []
		for object in objectList:
			result.append('/' + self._getPath(object, self._root))
		return result

	def listObjectTypes(self, path = '.', recursive = False):
		objectList = self._listObjects(path, recursive)
		result = []
		for object in objectList:
			if object._instance == None:
				result.append('dir')
			else:
				result.append(object._instance.__class__.__name__)
		return result

	def _mkObject(self, name, data, update = True, block = True):
		current = self._internalFind(name, checkMode = True)
		if (current != None) and (self._overwrite == False):
			raise IllegalArgumentException('"%s" already exists in the tree.' % (name))

		if '/' in name:
			directory = name[:name.rfind('/')]
			if directory == '':
				directory = '/'
			directoryPosition = self._internalFind(directory)
			name = name[name.rfind('/') + 1:]
		else:
			directoryPosition = self._internalFind('.')
		newInstance = IManagedObject(name, directoryPosition, data)
		if current == None:
			directoryPosition._children.append(newInstance)
		else:
			currentIndex = directoryPosition._children.index(current)
			directoryPosition._children[currentIndex] = newInstance
		if update:
			self._treeUpdate(block)

	def mkdir(self, path, update = True, block = True):
		name = os.path.basename(path)
		if name == '':
			raise IllegalArgumentException('Name is not specified.')
		directory = os.path.dirname(path)
		if directory == '':
			###Make new directory in current directory.
			directory = '.'
		position = self._internalFind(directory)
		position._children.append(IManagedObject(name, position))
		if update:
			self._treeUpdate(block)

	def mkdirs(self, path, update = True, block = True):
		if path == '/':
			### Root directory always exists.
			return
		if path[-1] == '/':
			path = path[:-1]

		name = os.path.basename(path)
		if name == '':
			raise IllegalArgumentException('Name is not specified.')
		self._internalFind(path, True)
		if update:
			self._treeUpdate(block)

	def rmdir(self, path, update = True, block = True):
		position = self._internalFind(path)
		if position._instance == None:
			###This is a directory.
			position._parent._children.remove(position)
			if update:
				self._treeUpdate(block)
		else:
			###This is not a directory.
			raise IllegalArgumentException()

	def _rmObject(self, instance):
		for object in self._listObjects('/', True):
			if object._instance == instance:
				path = self.findPath(object)
				self.rm(path)

	def rm(self, path, update = True, block = True):
		position = self._internalFind(path)
		if position._parent == None:
			###This is the root directory.
			self.commit()
			self.close()
			self._root._children = []
		else:
			position._parent._children.remove(position)
		if update:
			self._treeUpdate(block)

	def findPath(self, object):
		return '/' + self._getPath(object, self._root)

	def mv(self, oldPath, newPath, update = True, block = True):
		newDirectory = os.path.dirname(newPath)
		if newDirectory == '':
			newDirectory = '.'
		position = self._internalFind(newDirectory)
		oldPosition = self._internalFind(oldPath)
		newName = os.path.basename(newPath)
		if self.setOverwrite() == False:
			for child in position._children:
				if child._name == newName:
					raise IllegalArgumentException()
		if newName == '':
			###Move only.
			position._children.append(oldPosition)
		else:
			###Move and rename.
			oldPosition._name = newName
			position._children.append(oldPosition)
		oldPosition._parent._children.remove(oldPosition)
		if update:
			self._treeUpdate(block)

	def setOverwrite(self, overwrite = True):
		self._overwrite = overwrite

	def cp(self, oldPath, newPath, recursive = False, update = True, block = True):
		object = self._internalFind(oldPath)
		if object._instance == None:
			### Directory.
			self.mkdir(newPath)
			if recursive:
				for child in object._children:
					childName = child.name()
					oldPath2 = oldPath + '/' + childName
					newPath2 = newPath + '/' + childName
					self.cp(oldPath2, newPath2, True)
		else:
			data = object._instance
			className = data.__class__.__name__
			if className == 'IHistogram1D':
				histogramFactory = IHistogramFactory(self)
				newData = histogramFactory.createCopy(newPath, data)
			elif className == 'IHistogram2D':
				histogramFactory = IHistogramFactory(self)
				newData = histogramFactory.createCopy(newPath, data)
			elif className == 'IHistogram3D':
				histogramFactory = IHistogramFactory(self)
				newData = histogramFactory.createCopy(newPath, data)
			elif className == 'ICloud1D':
				histogramFactory = IHistogramFactory(self)
				newData = histogramFactory.createCopy(newPath, data)
			elif className == 'ICloud2D':
				histogramFactory = IHistogramFactory(self)
				newData = histogramFactory.createCopy(newPath, data)
			elif className == 'ICloud3D':
				histogramFactory = IHistogramFactory(self)
				newData = histogramFactory.createCopy(newPath, data)
			elif className == 'IProfile1D':
				histogramFactory = IHistogramFactory(self)
				newData = histogramFactory.createCopy(newPath, data)
			elif className == 'IProfile2D':
				histogramFactory = IHistogramFactory(self)
				newData = histogramFactory.createCopy(newPath, data)
			elif className == 'IFunction':
				functionFactory = IFunctionFactory(self)
				newData = functionFactory.cloneFunction(data, True)
				self._mkObject(newPath, newData)
			elif className == 'IDataPointSet':
				dataPointSetFactory = IDataPointSetFactory(self)
				newData = dataPointSetFactory.createCopy(newPath, data)
			else:
				raise RuntimeException()
		if update:
			self._treeUpdate(block)

	def symlink(self, oldPath, newPath, update = True, block = True):
		newDirectory = os.path.dirname(newPath)
		if newDirectory == '':
			newDirectory = '.'
		position = self._internalFind(newDirectory)
		oldPosition = self._internalFind(oldPath)
		newName = os.path.basename(newPath)
		if self.setOverwrite() == False:
			for child in position._children:
				if child._name == newName:
					raise IllegalArgumentException()
		if newName == '':
			raise IllegalArgumentException()
		else:
			managedObject = IManagedObject(newName, position, oldPosition._instance)
			managedObject._children = oldPosition._children
			position._children.append(managedObject)
		if update:
			self._treeUpdate(block)

	def mount(self, path, tree, treePath, update = True, block = True):
		mountPosition = self._internalFind(path)
		treePosition = tree._internalFind(treePath)
		mountPosition._children.append(treePosition)
		treePosition._tree = tree
		treePosition._parent = mountPosition
		if update:
			self._treeUpdate(block)

	def findTree(self, path):
		position = self._internalFind(path)
		if position._tree == None:
			raise IllegalArgumentException()
		return position._tree

	def unmount(self, path, update = True, block = True):
		unmountPosition = self._internalFind(path)
		if unmountPosition._tree == None:
			raise IllegalArgumentException()
		unmountPosition._parent._children.remove(unmountPosition)
		if update:
			self._treeUpdate(block)

	def close(self):
		self._hide()
		self._getGuiTree().terminate()
		self._setGuiTree(None)

	def _writeProfile1d(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		if object._instance._option == None:
			storeFile.write('%s<profile1d name="%s" title="%s" path="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, footer))
		else:
			storeFile.write('%s<profile1d name="%s" title="%s" path="%s" options="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, xmlEscape(object._getOptionString()), footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		### Axis.
		self._writeAxis(storeFile, object, header + '\t', footer)

		### Statistics.
		entries = self._writeStatistics(storeFile, object, header + '\t', footer)

		### Data1d.
		self._writeData1d_profile1d(storeFile, object, header + '\t', footer, entries)

		### End.
		storeFile.write(header + '</profile1d>' + footer)

	def _writeProfile2d(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		if object._option == None:
			storeFile.write('%s<profile2d name="%s" title="%s" path="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, footer))
		else:
			storeFile.write('%s<profile2d name="%s" title="%s" path="%s" options="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, xmlEscape(object._getOptionString()), footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		### Axis.
		self._writeAxis(storeFile, object, header + '\t', footer)

		### Statistics.
		entries = self._writeStatistics(storeFile, object, header + '\t', footer)

		### Data2d.
		self._writeData2d_profile2d(storeFile, object, header + '\t', footer, entries)

		### End.
		storeFile.write(header + '</profile2d>' + footer)

	def _writeHistogram1d(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		if object._option == None:
			storeFile.write('%s<histogram1d name="%s" title="%s" path="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, footer))
		else:
			storeFile.write('%s<histogram1d name="%s" title="%s" path="%s" options="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, xmlEscape(object._getOptionString()), footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		### Axis.
		self._writeAxis(storeFile, object, header + '\t', footer)

		### Statistics.
		entries = self._writeStatistics(storeFile, object, header + '\t', footer)

		### Data1d.
		self._writeData1d_histogram1d(storeFile, object, header + '\t', footer, entries)

		### End.
		storeFile.write(header + '</histogram1d>' + footer)

	def _writeHistogram2d(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		if object._option == None:
			storeFile.write('%s<histogram2d name="%s" title="%s" path="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, footer))
		else:
			storeFile.write('%s<histogram2d name="%s" title="%s" path="%s" options="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, xmlEscape(object._getOptionString()), footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		### Axis.
		self._writeAxis(storeFile, object, header + '\t', footer)

		### Statistics.
		entries = self._writeStatistics(storeFile, object, header + '\t', footer)

		### Data2d.
		self._writeData2d_histogram2d(storeFile, object, header + '\t', footer, entries)

		### End.
		storeFile.write(header + '</histogram2d>' + footer)

	def _writeHistogram3d(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		if object._option == None:
			storeFile.write('%s<histogram3d name="%s" title="%s" path="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, footer))
		else:
			storeFile.write('%s<histogram3d name="%s" title="%s" path="%s" options="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, xmlEscape(object._getOptionString()), footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		### Axis.
		self._writeAxis(storeFile, object, header + '\t', footer)

		### Statistics.
		entries = self._writeStatistics(storeFile, object, header + '\t', footer)

		### Data3d.
		self._writeData3d_histogram3d(storeFile, object, header + '\t', footer, entries)

		### End.
		storeFile.write(header + '</histogram3d>' + footer)

	def _writeFunction(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		storeFile.write('%s<function name="%s" title="%s" path="%s" isNormalized="false">%s' % (header, xmlEscape(object._name), xmlEscape(object.annotation().value('Title')), path, footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		### Codelet.
		self._writeCodelet(storeFile, object, header + '\t', footer)

		### Arguments.
		self._writeArguments(storeFile, object, header + '\t', footer)

		### Parameters.
		self._writeParameters(storeFile, object, header + '\t', footer)

		### End.
		storeFile.write(header + '</function>' + footer)

	def _writeDataPointSet(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		storeFile.write('%s<dataPointSet name="%s" title="%s" path="%s" dimension="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, object.dimension(), footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		### DataPoint.
		self._writeDataPoint(storeFile, object, header + '\t', footer)

		### End.
		storeFile.write(header + '</dataPointSet>' + footer)

	def _writeCloud1d(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		if object._option == None:
			storeFile.write('%s<cloud1d name="%s" maxEntries="%s" title="%s" path="%s" lowerEdgeX="%s" upperEdgeX="%s">%s' % (header, xmlEscape(object._name), object.maxEntries(), xmlEscape(object.title()), path, `object.lowerEdge()`, `object.upperEdge()`, footer))
		else:
			storeFile.write('%s<cloud1d name="%s" maxEntries="%s" title="%s" path="%s" options="%s" lowerEdgeX="%s" upperEdgeX="%s">%s' % (header, xmlEscape(object._name), object.maxEntries(), xmlEscape(object.title()), path, xmlEscape(object._getOptionString()), `object.lowerEdge()`, `object.upperEdge()`, footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		if object.isConverted ():
			### Histogram1d.
			self._writeHistogram1d(storeFile, object.histogram(), path, header + '\t', footer)
		else:
			### Entries1d.
			self._writeEntries1d(storeFile, object, header + '\t', footer)

		### End.
		storeFile.write(header + '</cloud1d>' + footer)

	def _writeCloud2d(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		if object._option == None:
			storeFile.write('%s<cloud2d name="%s" maxEntries="%s" title="%s" path="%s" lowerEdgeX="%s" upperEdgeX="%s" lowerEdgeY="%s" upperEdgeY="%s">%s' % (header, xmlEscape(object._name), object.maxEntries(), xmlEscape(object.title()), path, `object.lowerEdgeX()`, `object.upperEdgeX()`, `object.lowerEdgeY()`, `object.upperEdgeY()`, footer))
		else:
			storeFile.write('%s<cloud2d name="%s" maxEntries="%s" title="%s" path="%s" options="%s" lowerEdgeX="%s" upperEdgeX="%s" lowerEdgeY="%s" upperEdgeY="%s">%s' % (header, xmlEscape(object._name), object.maxEntries(), xmlEscape(object.title()), path, xmlEscape(object._getOptionString()), `object.lowerEdgeX()`, `object.upperEdgeX()`, `object.lowerEdgeY()`, `object.upperEdgeY()`, footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		if object.isConverted ():
			### Histogram2d.
			self._writeHistogram2d(storeFile, object.histogram(), path, header + '\t', footer)
		else:
			### Entries2d.
			self._writeEntries2d(storeFile, object, header + '\t', footer)

		### End.
		storeFile.write(header + '</cloud2d>' + footer)

	def _writeCloud3d(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		if object._option == None:
			storeFile.write('%s<cloud3d name="%s" maxEntries="%s" title="%s" path="%s" lowerEdgeX="%s" upperEdgeX="%s" lowerEdgeY="%s" upperEdgeY="%s" lowerEdgeZ="%s" upperEdgeZ="%s">%s' % (header, xmlEscape(object._name), object.maxEntries(), xmlEscape(object.title()), path, `object.lowerEdgeX()`, `object.upperEdgeX()`, `object.lowerEdgeY()`, `object.upperEdgeY()`, `object.lowerEdgeZ()`, `object.upperEdgeZ()`, footer))
		else:
			storeFile.write('%s<cloud3d name="%s" maxEntries="%s" title="%s" path="%s" options="%s" lowerEdgeX="%s" upperEdgeX="%s" lowerEdgeY="%s" upperEdgeY="%s" lowerEdgeZ="%s" upperEdgeZ="%s">%s' % (header, xmlEscape(object._name), object.maxEntries(), xmlEscape(object.title()), path, xmlEscape(object._getOptionString()), `object.lowerEdgeX()`, `object.upperEdgeX()`, `object.lowerEdgeY()`, `object.upperEdgeY()`, `object.lowerEdgeZ()`, `object.upperEdgeZ()`, footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		if object.isConverted ():
			### Histogram3d.
			self._writeHistogram3d(storeFile, object.histogram(), path, header + '\t', footer)
		else:
			### Entries3d.
			self._writeEntries3d(storeFile, object, header + '\t', footer)

		### End.
		storeFile.write(header + '</cloud3d>' + footer)

	def _writeTuple(self, storeFile, object, path, header, footer):
		xmlEscape = self._xmlEscape
		### Base.
		if object._getOption() == {}:
			storeFile.write('%s<tuple name="%s" title="%s" path="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, footer))
		else:
			storeFile.write('%s<tuple name="%s" title="%s" path="%s" options="%s">%s' % (header, xmlEscape(object._name), xmlEscape(object.title()), path, object._getOptionString(), footer))

		### Annotation.
		self._writeAnnotation(storeFile, object, header + '\t', footer)

		### Columns.
		self._writeColumns(storeFile, object, header + '\t', footer)

		### Rows.
		self._writeRows(storeFile, object, header + '\t', footer)

		### End.
		storeFile.write(header + '</tuple>' + footer)

	def _writeAnnotation(self, storeFile, object, header, footer):
		storeFile.write(header + '<annotation>' + footer)
		annotation = object.annotation()
		xmlEscape = self._xmlEscape
		for i in range(annotation.size()):
			if annotation._sticky(i):
				storeFile.write('%s\t<item key="%s" value="%s" sticky="true"/>%s' % (header, xmlEscape(annotation.key(i)), xmlEscape(annotation.value(i)), footer))
			else:
				storeFile.write('%s\t<item key="%s" value="%s" sticky="false"/>%s' % (header, xmlEscape(annotation.key(i)), xmlEscape(annotation.value(i)), footer))
		storeFile.write(header + '</annotation>' + footer)

	def _writeAxis(self, storeFile, object, header, footer):
		directions = ['x', 'y', 'z']
		dimension = object.dimension()
		if dimension == 1:
			axes = [object.axis()]
		elif dimension == 2:
			axes = [object.xAxis(), object.yAxis()]
		else:
			axes = [object.xAxis(), object.yAxis(), object.zAxis()]

		for i in range(dimension):
			axis = axes[i]
			storeFile.write('%s<axis direction="%s" min="%s" max="%s" numberOfBins="%s">%s' % (header, directions[i], `axis.lowerEdge()`, `axis.upperEdge()`, axis.bins(), footer))
			if axis.isFixedBinning() == False:
				for i in range(axis.bins() - 1):
					storeFile.write('%s\t<binBorder value="%s"/>%s' % (header, `axis.binUpperEdge(i)`, footer))
			storeFile.write(header + '</axis>' + footer)

	def _writeStatistics(self, storeFile, object, header, footer):
		statisticSet = object._getStatisticSet()
		storeFile.write('%s<statistics entries="%d">%s' % (header, statisticSet[0], footer))
		if object.dimension() == 1:
			storeFile.write('%s\t<statistic direction="x" mean="%.16f" rms="%.16f"/>%s' % (header, statisticSet[1], statisticSet[2], footer))
		elif object.dimension() == 2:
			storeFile.write('%s\t<statistic direction="x" mean="%.16f" rms="%.16f"/>%s' % (header, statisticSet[1], statisticSet[3], footer))
			storeFile.write('%s\t<statistic direction="y" mean="%.16f" rms="%.16f"/>%s' % (header, statisticSet[2], statisticSet[4], footer))
		else:
			storeFile.write('%s\t<statistic direction="x" mean="%.16f" rms="%.16f"/>%s' % (header, statisticSet[1], statisticSet[4], footer))
			storeFile.write('%s\t<statistic direction="y" mean="%.16f" rms="%.16f"/>%s' % (header, statisticSet[2], statisticSet[5], footer))
			storeFile.write('%s\t<statistic direction="z" mean="%.16f" rms="%.16f"/>%s' % (header, statisticSet[3], statisticSet[6], footer))
		storeFile.write(header + '</statistics>' + footer)
		return statisticSet[0]

	def _writeData1d_profile1d(self, storeFile, object, header, footer, entries):
		storeFile.write(header + '<data1d>' + footer)
		if entries:
			for i, binEntry in enumerate(object._binEntries.data):
				if binEntry:
					if i < 2:
						if i:
							indexX = 'OVERFLOW'
						else:
							indexX = 'UNDERFLOW'
					else:
						indexX = i - 2
					dataSet = object._getDataSet(i)
					storeFile.write('%s\t<bin1d binNum="%s" entries="%d" height="%.16f" error="%.16f" weightedMean="%.16f" weightedRms="%.16f" rms="%.16f"/>%s' % (header, indexX, binEntry, dataSet[0], dataSet[1], dataSet[2], dataSet[3], dataSet[4], footer))
		storeFile.write(header + '</data1d>' + footer)

	def _writeData2d_profile2d(self, storeFile, object, header, footer, entries):
		storeFile.write(header + '<data2d>' + footer)
		if entries:
			lenY = object._binEntries.length()
			for i, binEntry in enumerate(object._binEntries.data):
				if binEntry:
					innerY, innerX = divmod(i, lenY)
					if innerX < 2:
						if innerX:
							indexX = 'OVERFLOW'
						else:
							indexX = 'UNDERFLOW'
					else:
						indexX = innerX - 2
					if innerY < 2:
						if innerY:
							indexY = 'OVERFLOW'
						else:
							indexY = 'UNDERFLOW'
					else:
						indexY = innerY - 2
					dataSet = object._getDataSet(i)
					storeFile.write('%s\t<bin2d binNumX="%s" binNumY="%s" entries="%d" height="%.16f" error="%.16f" weightedMeanX="%.16f" weightedMeanY="%.16f" weightedRmsX="%.16f" weightedRmsY="%.16f" rms="%.16f"/>%s' % (header, indexX, indexY, binEntry, dataSet[0], dataSet[1], dataSet[2], dataSet[3], dataSet[4], dataSet[5], dataSet[6], footer))
		storeFile.write(header + '</data2d>' + footer)

	def _writeData1d_histogram1d(self, storeFile, object, header, footer, entries):
		storeFile.write(header + '<data1d>' + footer)
		if entries:
			for i, binEntry in enumerate(object._binEntries.data):
				if binEntry:
					if i < 2:
						if i:
							indexX = 'OVERFLOW'
						else:
							indexX = 'UNDERFLOW'
					else:
						indexX = i - 2
					dataSet = object._getDataSet(i)
					storeFile.write('%s\t<bin1d binNum="%s" entries="%d" height="%.16f" error="%.16f" weightedMean="%.16f" weightedRms="%.16f"/>%s' % (header, indexX, binEntry, dataSet[0], dataSet[1], dataSet[2], dataSet[3], footer))
		storeFile.write(header + '</data1d>' + footer)

	def _writeData2d_histogram2d(self, storeFile, object, header, footer, entries):
		storeFile.write(header + '<data2d>' + footer)
		if entries:
			lenY, lenZ = object._binEntries.length()
			for i, binEntry in enumerate(object._binEntries.data):
				if binEntry:
					innerY, innerX = divmod(i, lenY)
					if innerX < 2:
						if innerX:
							indexX = 'OVERFLOW'
						else:
							indexX = 'UNDERFLOW'
					else:
						indexX = innerX - 2
					if innerY < 2:
						if innerY:
							indexY = 'OVERFLOW'
						else:
							indexY = 'UNDERFLOW'
					else:
						indexY = innerY - 2
					dataSet = object._getDataSet(i)
					storeFile.write('%s\t<bin2d binNumX="%s" binNumY="%s" entries="%d" height="%.16f" error="%.16f" weightedMeanX="%.16f" weightedMeanY="%.16f" weightedRmsX="%.16f" weightedRmsY="%.16f"/>%s' % (header, indexX, indexY, binEntry, dataSet[0], dataSet[1], dataSet[2], dataSet[3], dataSet[4], dataSet[5], footer))
		storeFile.write(header + '</data2d>' + footer)

	def _writeData3d_histogram3d(self, storeFile, object, header, footer, entries):
		storeFile.write(header + '<data3d>' + footer)
		if entries:
			lenY, lenZ = object._binEntries.length()
			for i, binEntry in enumerate(object._binEntries.data):
				if binEntry:
					innerZ, rest = divmod(i, lenZ)
					innerY, innerX = divmod(rest, lenY)
					if innerX < 2:
						if innerX:
							indexX = 'OVERFLOW'
						else:
							indexX = 'UNDERFLOW'
					else:
						indexX = innerX - 2
					if innerY < 2:
						if innerY:
							indexY = 'OVERFLOW'
						else:
							indexY = 'UNDERFLOW'
					else:
						indexY = innerY - 2
					if innerZ < 2:
						if innerZ:
							indexZ = 'OVERFLOW'
						else:
							indexZ = 'UNDERFLOW'
					else:
						indexZ = innerZ - 2
					dataSet = object._getDataSet(i)
					storeFile.write('%s\t<bin3d binNumX="%s" binNumY="%s" binNumZ="%s" entries="%d" height="%.16f" error="%.16f" weightedMeanX="%.16f" weightedMeanY="%.16f" weightedMeanZ="%.16f" weightedRmsX="%.16f" weightedRmsY="%.16f" weightedRmsZ="%.16f"/>%s' % (header, indexX, indexY, indexZ, binEntry, dataSet[0], dataSet[1], dataSet[2], dataSet[3], dataSet[4], dataSet[5], dataSet[6], dataSet[7], footer))
		storeFile.write(header + '</data3d>' + footer)

	def _writeCodelet(self, storeFile, object, header, footer):
		storeFile.write(header + '<codelet>' + footer)
		storeFile.write('%s\t%s%s' % (header, self._xmlEscape(object.codeletString()), footer))
		storeFile.write(header + '</codelet>' + footer)

	def _writeArguments(self, storeFile, object, header, footer):
		storeFile.write(header + '<arguments>' + footer)
		for variableName in object.variableNames():
			storeFile.write('%s\t<argument name="%s">%s' % (header, self._xmlEscape(variableName), footer))
			storeFile.write('%s\t</argument>%s' % (header, footer))
		storeFile.write(header + '</arguments>' + footer)

	def _writeParameters(self, storeFile, object, header, footer):
		storeFile.write(header + '<parameters>' + footer)
		for parameterName in object.parameterNames():
			storeFile.write('%s\t<parameter name="%s" value="%s"/>%s' % (header, self._xmlEscape(parameterName), `object.parameter(parameterName)`, footer))
		storeFile.write(header + '</parameters>' + footer)

	def _writeDataPoint(self, storeFile, object, header, footer):
		for i in range(object.size()):
			storeFile.write(header + '<dataPoint>' + footer)
			dataPoint = object.point(i)
			for j in range(dataPoint.dimension()):
				measurement = dataPoint.coordinate(j)
				storeFile.write('%s\t<measurement value="%s" errorPlus="%s" errorMinus="%s"/>%s' % (header, `measurement.value()`, `measurement.errorPlus()`, `measurement.errorMinus()`, footer))
			storeFile.write(header + '</dataPoint>' + footer)

	def _writeEntries1d(self, storeFile, object, header, footer):
		storeFile.write(header + '<entries1d>' + footer)
		for i in range(object.entries()):
			storeFile.write('%s\t<entry1d valueX="%s" weight="%s"/>%s' % (header, `object.value(i)`, `object.weight(i)`, footer))
		storeFile.write(header + '</entries1d>' + footer)

	def _writeEntries2d(self, storeFile, object, header, footer):
		storeFile.write(header + '<entries2d>' + footer)
		for i in range(object.entries()):
			storeFile.write('%s\t<entry2d valueX="%s" valueY="%s" weight="%s"/>%s' % (header, `object.valueX(i)`, `object.valueY(i)`, `object.weight(i)`, footer))
		storeFile.write(header + '</entries2d>' + footer)

	def _writeEntries3d(self, storeFile, object, header, footer):
		storeFile.write(header + '<entries3d>' + footer)
		for i in range(object.entries()):
			storeFile.write('%s\t<entry3d valueX="%s" valueY="%s" valueZ="%s" weight="%s"/>%s' % (header, `object.valueX(i)`, `object.valueY(i)`, `object.valueZ(i)`, `object.weight(i)`, footer))
		storeFile.write(header + '</entries3d>' + footer)

	def _writeColumns(self, storeFile, object, header, footer):
		storeFile.write(header + '<columns>' + footer)
		xmlEscape = self._xmlEscape
		for columnIndex in range(object.columns()):
			columnType = object.columnType(columnIndex)
			columnName = xmlEscape(object.columnName(columnIndex))
			if columnType == PTypes.ITuple:
				storeFile.write('%s\t<column name="(%s) %s=%s" type="%s"/>%s' % (header, xmlEscape(object._getOptionString()), columnName, self._columnWalker('', object.getTuple(columnIndex)), columnType.TYPE, footer))
			else:
				columnDefault = object._columnDefaults[columnIndex]
				if columnDefault == None:
					storeFile.write('%s\t<column name="%s" type="%s"/>%s' % (header, columnName, columnType.TYPE, footer))
				else:
					if columnType == PTypes.Boolean:
						if columnDefault:
							storeFile.write('%s\t<column name="%s=true" type="%s"/>%s' % (header, columnName, columnType.TYPE, footer))
						else:
							storeFile.write('%s\t<column name="%s=false" type="%s"/>%s' % (header, columnName, columnType.TYPE, footer))
					elif columnType in [PTypes.String, PTypes.Character]:
						storeFile.write('%s\t<column name="%s=%s" type="%s"/>%s' % (header, columnName, xmlEscape(columnDefault), columnType.TYPE, footer))
					else:
						storeFile.write('%s\t<column name="%s=%s" type="%s"/>%s' % (header, columnName, `columnDefault`, columnType.TYPE, footer))
		storeFile.write(header + '</columns>' + footer)

	def _columnWalker(self, expression, ituple):
		expression += '{'
		xmlEscape = self._xmlEscape
		for columnIndex in range(ituple.columns()):
			columnType = ituple.columnType(columnIndex)
			columnName = ituple.columnName(columnIndex)
			if columnType == PTypes.ITuple:
				expression = self._columnWalker(expression + 'ITuple (%s) %s=' % (ituple._getOptionString(), columnName), ituple.getTuple(columnIndex))
			else:
				columnDefault = ituple._columnDefaults[columnIndex]
				if columnDefault == None:
					expression += '%s %s, ' % (columnType.TYPE, columnName)
				else:
					if columnType == PTypes.Boolean:
						if columnDefault:
							expression += '%s %s=true, ' % (columnType.TYPE, columnName)
						else:
							expression += '%s %s=false, ' % (columnType.TYPE, columnName)
					elif columnType in [PTypes.String, PTypes.Character]:
						expression += '%s %s="%s", ' % (columnType.TYPE, columnName, columnDefault)
					else:
						expression += '%s %s=%s, ' % (columnType.TYPE, columnName, `columnDefault`)
		if expression.endswith(', '):
			return self._xmlEscape(expression[:-2] + '}')
		else:
			return self._xmlEscape(expression + '}')

	def _writeRows(self, storeFile, object, header, footer):
		storeFile.write(header + '<rows>' + footer)
		self._rowWalker(storeFile, object, header + '\t', footer)
		storeFile.write(header + '</rows>' + footer)

	def _rowWalker(self, storeFile, ituple, header, footer):
		xmlEscape = self._xmlEscape
		itupleRows = ituple._rows
		nColumns = ituple.columns()
		PTypesITuple = PTypes.ITuple
		PTypesBoolean = PTypes.Boolean
		PTypesStringCharacter = [PTypes.String, PTypes.Character]

		columnTypes = []
		for columnIndex in range(nColumns):
			columnTypes.append(ituple.columnType(columnIndex))

		### Inner ITuple exists?
		ITupleList = []
		for columnIndex in range(nColumns):
			if columnTypes[columnIndex] == PTypesITuple:
				name = ituple._columnNames[columnIndex]
				tupleColumnsData = ituple._columnConverters[columnIndex]
				ITupleList.append(ITuple(name, name, tupleColumnsData[0], tupleColumnsData[1], tupleColumnsData[2], tupleColumnsData[3]))
			else:
				ITupleList.append(None)

		storeFileWrite = storeFile.write
		xml_rowStart = header + '<row>' + footer
		xml_rowEnd = header + '</row>' + footer
		xml_entryTrue = header + '\t<entry value="true"/>' + footer
		xml_entryFalse = header + '\t<entry value="false"/>' + footer
		xml_entryITupleStart = header + '\t<entryITuple>' + footer
		xml_entryITupleEnd = header + '\t</entryITuple>' + footer
		for rowIndex, rowData in enumerate(ituple._rows):
			storeFileWrite(xml_rowStart)
			for columnIndex, columnType in enumerate(columnTypes):
				if columnType == PTypesITuple:
					storeFileWrite(xml_entryITupleStart)
					innerTuple = ITupleList[columnIndex]
					if rowData[columnIndex] == None:
						innerTuple._rows = []
					else:
						innerTuple._rows = rowData[columnIndex]
					self._rowWalker(storeFile, innerTuple, header + '\t\t', footer)
					storeFileWrite(xml_entryITupleEnd)
				elif columnType == PTypesBoolean:
					if rowData[columnIndex]:
						storeFileWrite(xml_entryTrue)
					else:
						storeFileWrite(xml_entryFalse)
				elif columnType in PTypesStringCharacter:
					storeFileWrite('%s\t<entry value="%s"/>%s' % (header, xmlEscape(rowData[columnIndex]), footer))
				else:
					storeFileWrite('%s\t<entry value="%s"/>%s' % (header, `rowData[columnIndex]`, footer))
			storeFileWrite(xml_rowEnd)

	def _xmlEscape(self, data):
		return xml.sax.saxutils.escape(data, self._entities)

	def commit(self):
		if self.isReadOnly():
			return

		### Line separator.
		sep = os.linesep

		### Store file creation.
		try:
			import gzip
			if self._options.has_key('compress'):
				if self._options['compress']:
					storeFile = gzip.open(self._fileName, 'w')
				else:
					storeFile = file(self._fileName, 'w')
			else:
				storeFile = gzip.open(self._fileName, 'w')
		except ImportError:
			print 'PAIDA: gzip module is unavailable.'
			print 'PAIDA: all files are saved as unzipped.'
			storeFile = file(self._fileName, 'w')

		### Initial strings.
		storeFile.write('<?xml version="1.0" encoding="%s" ?>%s' % (encoding, sep))
		storeFile.write('<!DOCTYPE aida SYSTEM "http://aida.freehep.org/schemas/3.2.1/aida.dtd">' + sep)
		storeFile.write('<aida version="%s">%s' % (IConstants.AIDA_VERSION, sep))
		storeFile.write('\t<implementation package="PAIDA" version="%s"/>%s' % (IConstants.PAIDA_VERSION, sep))

		### Object walk.
		for object in self._listObjects('/', True):
			if object._instance == None:
				### Directory.
				pass
			else:
				escapedPath = self._xmlEscape(self.findPath(object._parent))
				if object._instance.__class__.__name__ == 'IProfile1D':
					self._writeProfile1d(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'IProfile2D':
					self._writeProfile2d(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'IHistogram1D':
					self._writeHistogram1d(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'IHistogram2D':
					self._writeHistogram2d(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'IHistogram3D':
					self._writeHistogram3d(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'IFunction':
					self._writeFunction(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'IDataPointSet':
					self._writeDataPointSet(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'ICloud1D':
					self._writeCloud1d(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'ICloud2D':
					self._writeCloud2d(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'ICloud3D':
					self._writeCloud3d(storeFile, object._instance, escapedPath, '\t', sep)

				elif object._instance.__class__.__name__ == 'ITuple':
					self._writeTuple(storeFile, object._instance, escapedPath, '\t', sep)

				else:
					raise RuntimeException('Unexpected data type in %s' % self.findPath(object))

		storeFile.write('</aida>')
		storeFile.close()
