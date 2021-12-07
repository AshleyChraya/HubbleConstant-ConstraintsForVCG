try:
	import xml.etree.cElementTree as ET
except ImportError:
	import cElementTree as ET
import gzip
from paida.paida_core.PExceptions import *
from paida.paida_core.PAbsorber import *
from paida.paida_core.IAnnotation import IAnnotation
from paida.paida_core.IHistogram1D import IHistogram1D
from paida.paida_core.IHistogram2D import IHistogram2D
from paida.paida_core.IHistogram3D import IHistogram3D
from paida.paida_core.ICloud1D import ICloud1D
from paida.paida_core.ICloud2D import ICloud2D
from paida.paida_core.ICloud3D import ICloud3D
from paida.paida_core.IDataPointSet import IDataPointSet
from paida.paida_core.IAxis import IAxis
from paida.paida_core.IManagedObject import IManagedObject
from paida.paida_core.PUtilities import optionAnalyzer, optionConstructor
from paida.paida_core.ITuple import ITuple
from paida.paida_core.IConstants import IConstants
from paida.paida_core.ITupleFactory import ITupleFactory
from paida.paida_core.IFunctionFactory import IFunctionFactory
import paida.paida_gui.PRoot as PRoot
import paida.paida_core.PTypes as PTypes
import sys
import os
import xml

encoding = 'ISO-8859-1'

class _baseHandler(object):
	directions = {'x': 0, 'y': 1, 'z': 2}
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


class _annotationHandler(_baseHandler):
	def __init__(self, element):
		self.annotation = IAnnotation()
		### Some implementations ommit annotation node when its content is empty.
		if element is not None:
			for item in element.findall('item'):
				self.annotation._addItem(str(item.get('key')), str(item.get('value')), item.get('sticky') == u'true')


# in contrast to namedHandler, it is not assumed here that the
# element is complete, i.e. the end event does not have to be read, yet
class _namedParser(_baseHandler):
	def __init__(self, element):
		self.name = str(element.get('name'))
		self.title = str(element.get('title', self.name))
		self.path = str(element.get('path', '/'))
		options = element.get('options')
		if options is None:
			self.options = None
		else:
			self.options = optionAnalyzer(str(options))


class _namedHandler(_namedParser):
	def __init__(self, element):
		_namedParser.__init__(self, element)
		self.annotation = _annotationHandler(element.find('annotation')).annotation
		self.annotation._addItem('Title', self.title, True)


class _aidaHandler(_baseHandler):
	def __init__(self, file, tree):
		# iterparse returns only end events by default
		fileParser = iter(ET.iterparse(file, events=('start', 'end')))
		for event, item in fileParser:
			name = item.tag
			if event == 'start' and name in ('cloud1d', 'cloud2d', 'cloud3d', 'dataPointSet'):
				handler = globals()['_%sHandler' % name](item, fileParser)
			elif event == 'start' and name in ('histogram1d', 'histogram2d', 'histogram3d', 'profile1d' 'profile2d'):
				for event, item in fileParser:
					if item.tag == name and event == 'end':
						break
				handler = globals()['_%sHandler' % name](item)
			elif event == 'start' and name == 'function':
				for event, item in fileParser:
					if item.tag == name and event == 'end':
						break
				try:
					functionFactory = self.functionFactory
				except AttributeError:
					self.functionFactory = IFunctionFactory(tree)
					functionFactory = self.functionFactory
				handler = globals()['_%sHandler' % name](item, functionFactory)
			elif event == 'start' and name == 'tuple':
				handler = globals()['_%sHandler' % name](item, fileParser, tree)
			elif event == 'end' and name == 'aida':
				tree.cd('/', update = True, block = True)
				continue
			else:
				continue

			# the object in each handler is given the same name as the tag
			object = handler.__getattribute__(name)
			path = handler.path
			tree.mkdirs(path, update = False)
			tree.cd(path, update = False)
			tree._mkObject(handler.name, object, update = True, block = False)
			item.clear()


class _axisHandler(_baseHandler):
	standard_attributes = (('min', float), ('max', float), ('numberOfBins', int))

	def __init__(self, element):
		### Direction.
		self.direction = str(element.get('direction', 'x'))

		for attr, _type in self.standard_attributes:
			try:
				self.__dict__[attr] = _type(element.get(attr))
			except ValueError:
				self.__dict__[attr] = self.evaluator(element.get(attr))

		self.binBorders = [float(item.get('value')) for item in element.findall('binBorder')]
		if self.binBorders == []:
			self.isFixedBinning = True
			tempEdge = [tempMinimum] = [self.min]
			unit = (self.max - tempMinimum) / self.numberOfBins
			for i in range(1, self.numberOfBins):
				tempEdge.append(tempMinimum + i * unit)			
		else:
			self.isFixedBinning = False
			tempEdge = [self.min]
			tempEdge.extend(self.binBorders)
		tempEdge.append(self.max)
		self.edge = tempEdge


class _statisticsHandler(_baseHandler):
	class _statisticHandler(_baseHandler):
		def __init__(self, element):
			self.direction = str(element.get('direction'))
			try:
				self.mean = float(element.get('mean'))
			except ValueError:
				self.mean = self.evaluator(element.get('mean'))
			try:
				self.rms = float(element.get('rms'))
			except ValueError:
				self.rms = self.evaluator(element.get('rms'))

	def __init__(self, element):
		try:
			self.entries = int(element.get('entries'))
		except ValueError:
			self.entries = self.evaluator(element.get('entries'))

		self.mean = [0.0, 0.0, 0.0]
		self.rms = [0.0, 0.0, 0.0]
		for item in element.findall('statistic'):
			stat = self._statisticHandler(item)
			self.mean[self.directions[stat.direction]] = stat.mean
			self.rms[self.directions[stat.direction]] = stat.rms


class _histogram1dHandler(_namedHandler):
	bin1d_attributes = (('height', float), ('error', float), ('entries', int), ('binNum', int), ('weightedMean', float), ('weightedRms', float))

	def __init__(self, element):
		_namedHandler.__init__(self, element)

		self.axis = _axisHandler(element.find('axis'))
		self.edges = [[], [], []]
		self.edges[self.directions[self.axis.direction]] = self.axis.edge
		
		self.statistics = _statisticsHandler(element.find('statistics'))
		self.histogram1d = IHistogram1D(self.name, self.title, self.edges, self.axis.isFixedBinning, self.options)
		self.histogram1d._annotation = self.annotation

		self.process_data1d(element.find('data1d'))


	def process_data1d(self, element):
		histogram = self.histogram1d
		statistics = self.statistics
		for bin1d in element.findall('bin1d'):
			data = {}
			for attr, _type in self.bin1d_attributes:
				binData = bin1d.get(attr)
				if binData is None:
					data[attr] = None
				else:
					try:
						data[attr] = _type(binData)
					except ValueError:
						data[attr] = self.evaluator(binData)

			if data['weightedMean'] is None:
				axis = histogram.axis()
				if data['binNum'] == IAxis.OVERFLOW_BIN:
					data['weightedMean'] = axis.binLowerEdge(data['binNum'])
				elif data['binNum'] == IAxis.UNDERFLOW_BIN:
					data['weightedMean'] = axis.binUpperEdge(data['binNum'])
				else:
					data['weightedMean'] = (axis.binUpperEdge(data['binNum']) - axis.binLowerEdge(data['binNum'])) / 2.0

			### Event if data['weightedRms'] is 0.0, "if not data['weightedRms']:" test it True.
			### So, we must explicitly describe the condition.
			if data['weightedRms'] is None:
				if data['binNum'] in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
					data['weightedRms'] = 0.0
				else:
					axis = histogram.axis()
					data['weightedRms'] = statistics.rms[0] * axis.binWidth(data['binNum']) / (axis.upperEdge() - axis.lowerEdge())

			if data['height'] is None:
				data['height'] = data['entries']

			if data['error'] is None:
				data['error'] = sqrt(data['entries'])
					
			### Fill.
			innerIndex = histogram._binEntries.getIndex(data['binNum'] + 2, 0, 0)
			histogram._binEntries.data[innerIndex] = data['entries']
			histogram._binSumOfWeights.data[innerIndex] = data['height']
			histogram._binSumOfErrors.data[innerIndex] = data['error']*data['error']
			histogram._binSumOfTorquesX.data[innerIndex] = data['weightedMean'] * data['height']
			histogram._binSumOfInertialsX.data[innerIndex] = (data['weightedRms']*data['weightedRms'] + data['weightedMean']*data['weightedMean']) * data['height']

	
class _histogram2dHandler(_namedHandler):
	bin2d_attributes = (('entries', int), ('height', float), ('error', float), ('binNumX', int), ('binNumY', int), ('weightedMeanX', float), ('weightedMeanY', float), ('weightedRmsX', float), ('weightedRmsY', float))

	def __init__(self, element):
		_namedHandler.__init__(self, element)

		self.axes = [_axisHandler(axis) for axis in element.findall('axis')]
		self.edges = [[], [], []]
		isFixedBinning = True
		for axis in self.axes:
			self.edges[self.directions[axis.direction]] = axis.edge
			isFixedBinning &= axis.isFixedBinning
		self.statistics = _statisticsHandler(element.find('statistics'))
		self.histogram2d = IHistogram2D(self.name, self.title, self.edges, isFixedBinning, self.options)
		self.histogram2d._annotation = self.annotation
		self.process_data2d(element.find('data2d'))

	def process_data2d(self, element):
		histogram = self.histogram2d
		statistics = self.statistics

		for bin2d in element.findall('bin2d'):
			data = {}
			for attr, _type in self.bin2d_attributes:
				binData = bin2d.get(attr)
				if binData is None:
					data[attr] = None
				else:
					try:
						data[attr] = _type(binData)
					except ValueError:
						data[attr] = self.evaluator(binData)


			if data['height'] is None:
				data['height'] = data['entries']
			if data['error'] is None:
				data['error'] = sqrt(data['entries'])

			if data['weightedMeanX'] is None:
				axis = histogram.xAxis()
				if data['binNumX'] == IAxis.OVERFLOW_BIN:
					data['weightedMeanX'] = axis.binLowerEdge(data['binNumX'])
				elif data['binNumX'] == IAxis.UNDERFLOW_BIN:
					data['weightedMeanX'] = axis.binUpperEdge(data['binNumX'])
				else:
					data['weightedMeanX'] = (axis.binUpperEdge(data['binNumX']) - axis.binLowerEdge(data['binNumX'])) / 2.0


			if data['weightedMeanY'] is None:
				axis = histogram.yAxis()
				if data['binNumY'] == IAxis.OVERFLOW_BIN:
					data['weightedMeanY'] = axis.binLowerEdge(data['binNumY'])
				elif data['binNumY'] == IAxis.UNDERFLOW_BIN:
					data['weightedMeanY'] = axis.binUpperEdge(data['binNumY'])
				else:
					data['weightedMeanY'] = (axis.binUpperEdge(data['binNumY']) - axis.binLowerEdge(data['binNumY'])) / 2.0

			if data['weightedRmsX'] is None:
				if data['binNumX'] in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
					data['weightedRmsX'] = 0.0
				else:
					axis = histogram.xAxis()
					data['weightedRmsX'] = statistics.rms[0] * axis.binWidth(data['binNumX']) / (axis.upperEdge() - axis.lowerEdge())
			
			if data['weightedMeanY'] is None:
				if data['binNumY'] in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
					data['weightedRmsY'] = 0.0
				else:
					axis = histogram.yAxis()
					data['weightedRmsY'] = statistics.rms[1] * axis.binWidth(data['binNumY']) / (axis.upperEdge() - axis.lowerEdge())
			### Fill.
			innerIndex = histogram._binEntries.getIndex(data['binNumX'] + 2, data['binNumY'] + 2, 0)
			histogram._binEntries.data[innerIndex] = data['entries']
			histogram._binSumOfWeights.data[innerIndex] = data['height']
			histogram._binSumOfErrors.data[innerIndex] = data['error']*data['error']
			histogram._binSumOfTorquesX.data[innerIndex] = data['weightedMeanX'] * data['height']
			histogram._binSumOfTorquesY.data[innerIndex] = data['weightedMeanY'] * data['height']
			histogram._binSumOfInertialsX.data[innerIndex] = (data['weightedRmsX']*data['weightedRmsX'] + data['weightedMeanX']*data['weightedMeanX']) * data['height']
			histogram._binSumOfInertialsY.data[innerIndex] = (data['weightedRmsY']*data['weightedRmsY'] + data['weightedMeanY']*data['weightedMeanY']) * data['height']


class _histogram3dHandler(_namedHandler):
	bin3d_attributes = (('entries', int), ('height', float), ('error', float), ('binNumX', int), ('binNumY', int), ('binNumZ', int), ('weightedRmsX', float), ('weightedRmsY', float), ('weightedRmsZ', float))

	def __init__(self, element):
		_namedHandler.__init__(self, element)

		self.axes = [_axisHandler(axis) for axis in element.findall('axis')]
		self.edges = [[], [], []]
		isFixedBinning = True
		for axis in self.axes:
			self.edges[self.directions[axis.direction]] = axis.edge
			isFixedBinning &= axis.isFixedBinning
		self.statistics = _statisticsHandler(element.find('statistics'))

		self.histogram3d = IHistogram3D(self.name, self.title, self.edges, isFixedBinning, self.options)
		self.histogram3d._annotation = self.annotation
		self.process_data3d(element.find('data3d'), self)

	def process_bin3d(self, element):
		histogram = self.histogram3d
		statistics = self.statistics
		for bin3d in element.findall('bin3d'):    
			data = {}
			for attr, _type in self.standard_attributes:
				binData = bin3d.get(attr)
				if binData is None:
					data[attr] = None
				else:
					try:
						data[attr] = _type(binData)
					except ValueError:
						data[attr] = self.evaluator(binData)

			if data['height'] is None:
				data['height'] = data['entries']

			if data['error'] is None:
				data['error'] = sqrt(data['entries'])

			if data['weightedMeanX'] is None:
				axis = histogram.xAxis()
				if data['binNumX'] == IAxis.OVERFLOW_BIN:
					data['weightedMeanX'] = axis.binLowerEdge(data['binNumX'])
				elif data['binNumX'] == IAxis.UNDERFLOW_BIN:
					data['weightedMeanX'] = axis.binUpperEdge(data['binNumX'])
				else:
					data['weightedMeanX'] = (axis.binUpperEdge(data['binNumX']) - axis.binLowerEdge(data['binNumX'])) / 2.0

			if data['weightedMeanY'] is None:
				axis = histogram.yAxis()
				if data['binNumY'] == IAxis.OVERFLOW_BIN:
					data['weightedMeanY'] = axis.binLowerEdge(data['binNumY'])
				elif data['binNumY'] == IAxis.UNDERFLOW_BIN:
					data['weightedMeanY'] = axis.binUpperEdge(data['binNumY'])
				else:
					data['weightedMeanY'] = (axis.binUpperEdge(data['binNumY']) - axis.binLowerEdge(data['binNumY'])) / 2.0

			if data['weightedMeanZ'] is None:
				axis = histogram.zAxis()
				if data['binNumZ'] == IAxis.OVERFLOW_BIN:
					data['weightedMeanZ'] = axis.binLowerEdge(data['binNumZ'])
				elif data['binNumZ'] == IAxis.UNDERFLOW_BIN:
					data['weightedMeanZ'] = axis.binUpperEdge(data['binNumZ'])
				else:
					data['weightedMeanZ'] = (axis.binUpperEdge(data['binNumZ']) - axis.binLowerEdge(data['binNumZ'])) / 2.0

			if data['weightedRmsX'] is None:
				if data['binNumX'] in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
					data['weightedRmsX'] = 0.0
				else:
					axis = histogram.xAxis()
					data['weightedRmsX'] = statistics.rms[0] * axis.binWidth(data['binNumX']) / (axis.upperEdge() - axis.lowerEdge())
			
			if data['weightedRmsY'] is None:
				if data['binNumY'] in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
					data['weightedRmsY'] = 0.0
				else:
					axis = histogram.yAxis()
					data['weightedRmsY'] = statistics.rms[1] * axis.binWidth(data['binNumY']) / (axis.upperEdge() - axis.lowerEdge())

			if data['weightedRmsZ'] is None:
				if data['binNumZ'] in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
					data['weightedRmsZ'] = 0.0
				else:
					axis = histogram.zAxis()
					data['weightedRmsZ'] = statistics.rms[2] * axis.binWidth(data['binNumZ']) / (axis.upperEdge() - axis.lowerEdge())

			### Fill.
			innerIndex = histogram._binEntries.getIndex(data['binNumX'] + 2, data['binNumY'] + 2, data['binNumZ'] + 2)
			histogram._binEntries.data[innerIndex] = data['entries']
			histogram._binSumOfWeights.data[innerIndex] = data['height']
			histogram._binSumOfErrors.data[innerIndex] = data['error']*data['error']
			histogram._binSumOfTorquesX.data[innerIndex] = data['weightedMeanX'] * data['height']
			histogram._binSumOfTorquesY.data[innerIndex] = data['weightedMeanY'] * data['height']
			histogram._binSumOfTorquesZ.data[innerIndex] = data['weightedMeanZ'] * data['height']
			histogram._binSumOfInertialsX.data[innerIndex] = (data['weightedRmsX']*data['weightedRmsX'] + data['weightedMeanX']*data['weightedMeanX']) * data['height']
			histogram._binSumOfInertialsY.data[innerIndex] = (data['weightedRmsY']*data['weightedRmsY'] + data['weightedMeanY']*data['weightedMeanY']) * data['height']
			histogram._binSumOfInertialsZ.data[innerIndex] = (data['weightedRmsZ']*data['weightedRmsZ'] + data['weightedMeanZ']*data['weightedMeanZ']) * data['height']

# first read the columns, then instantiate a tuple with that information
# then add the rows one by one
class _tupleHandler(_namedParser):
	def __init__(self, element, fileIterator, tree):
		_namedParser.__init__(self, element)

		self.annotation = None
		columns = self.process_columns(fileIterator)
		self.expression = ''.join(columns)
		tupleFactory = ITupleFactory(tree)
		self.tuple = tupleFactory._create(self.name, self.title, self.expression, optionConstructor(self.options))
		if self.annotation is not None:
			self.tuple._annotation = self.annotation
		self.process_rows(fileIterator, self.tuple)

	def process_columns(self, fileIterator):
		while 1:
			event, item = fileIterator.next()
			name = item.tag
			if name == 'columns':
				if event == 'start':
					columns = []
				elif event == 'end':
					break
			elif name == 'annotation' and event == 'end':
				self.annotation = _annotationHandler(item).annotation
			elif name == 'column' and event == 'end':
				colName = str(item.get('name')).strip()
				if colName.endswith('='):
					colName = colName[:-1]

				colType = item.get('type', PTypes.Double.TYPE)
				### For Java implementation compatibility.
				if colType == 'java.lang.String':
					colType = PTypes.String.TYPE
				elif colType == 'java.lang.Object':
					colType = PTypes.Object.TYPE
				
				if '=' in colName and colType in (PTypes.String.TYPE, PTypes.Character.TYPE):
					columnNameList = colName.split('=')
					columnNameList[1] = '"%s"' % columnNameList[1]
					colName = '='.join(columnNameList)

				columns.append('%s %s; ' % (colType, colName))
			elif name == 'rows':
				### Rows should come after columns.
				raise RuntimeError('rows before columns')
			else:
				continue
		return columns

	# recursively deal with nested tuples
	# passing the tuple as the argument allows for recursive calls
	def process_rows(self, fileIterator, tuple, toBeCleared = None):
		converters = tuple._columnConverters
		### I think column will be always initialized to zero at (name == 'row and event == 'start')?
		#column = 0
		while 1:
			event, item = fileIterator.next()
			name = item.tag
			if name == 'entry' and event == 'end':
				tuple._rowBuffer[column] = converters[column](item.get('value'))
				column += 1
				### For performance reason.
				#item.clear()
			elif name == 'entryITuple':
				if event == 'start':
					self.process_rows(fileIterator, tuple.getTuple(column), toBeCleared)
					column += 1
				elif event == 'end':
					item.clear()
					break
			elif name == 'row':
				if event == 'start':
					column = 0
				elif event == 'end':
					tuple.addRow()
					toBeCleared.clear()
			elif name == 'rows':
				if event == 'start':
					toBeCleared = item
				else:
					break

class _cloud1dHandler(_namedParser):
	def __init__(self, element, fileIterator):
		_namedParser.__init__(self, element)
		self.maxEntries = int(element.get('maxEntries'))
		self.cloud1d = ICloud1D(self.name, self.title, self.maxEntries, self.options)
		
		# caching name for faster access
		fill = self.cloud1d.fill
		self.entries1d = False
		while 1:
			event, item = fileIterator.next()
			name = item.tag
			if name == 'entries1d':
				self.entries1d = True
				itemEntries1d = item
			elif name == 'annotation' and event == 'end':
				self.cloud1d._annotation = _annotationHandler(item).annotation
			elif name == 'entry1d' and event == 'end':
				try:
					weight = float(item.get('weight', 1.0))
				except ValueError:
					weight = self.evaluator(item.get('weight'))

				try:
					valueX = float(item.get('valueX'))
				except ValueError:
					valueX = self.evaluator(item.get('valueX'))

				fill(valueX, weight)
				itemEntries1d.clear()
			elif name == 'cloud1d' and event == 'end':
				if not self.entries1d:
					histogram1d = _histogram1dHandler(element.find('histogram1d')).histogram1d
					cloud1d = self.cloud1d
					cloud1d._histogram = histogram1d
					cloud1d._isConverted = True
					cloud1d._sumOfWeights = histogram1d.sumAllBinHeights()
					cloud1d._lowerEdges[0] = histogram1d.axis().lowerEdge()
					cloud1d._upperEdges[0] = histogram1d.axis().upperEdge()
					sumOfWeights = cloud1d.sumOfWeights()
					cloud1d._sumOfTorques[0] = histogram1d.mean() * sumOfWeights
					cloud1d._sumOfInertials[0] = (histogram1d.rms()*histogram1d.rms() + histogram1d.mean()*histogram1d.mean()) * sumOfWeights
				item.clear()
				break


class _cloud2dHandler(_namedParser):
	def __init__(self, element, fileIterator):
		_namedParser.__init__(self, element)

		self.maxEntries = int(element.get('maxEntries'))
		self.cloud2d = ICloud2D(self.name, self.title, self.maxEntries, self.options)
		# caching name for faster access
		fill = self.cloud2d.fill
		
		self.entries2d = False
		while 1:
			event, item = fileIterator.next()
			name = item.tag
			if name == 'entries2d':
				self.entries2d = True
				itemEntries2d = item
			elif name == 'annotation' and event == 'end':
				self.cloud2d._annotation = _annotationHandler(item).annotation
			elif name == 'entry2d' and event == 'end':
				try:
					weight = float(item.get('weight', 1.0))
				except ValueError:
					weight = self.evaluator(item.get('weight'))

				try:
					valueX = float(item.get('valueX'))
				except ValueError:
					valueX = self.evaluator(item.get('valueX'))
				try:
					valueY = float(item.get('valueY'))
				except ValueError:
					valueY = self.evaluator(item.get('valueY'))

				fill(valueX, valueY, weight)
				itemEntries2d.clear()
			elif name == 'cloud2d' and event == 'end':
				if not self.entries2d:
					histogram2d = _histogram2dHandler(element.find('histogram2d')).histogram2d
					cloud2d = self.cloud2d
					cloud2d._histogram = histogram2d
					cloud2d._isConverted = True
					cloud2d._sumOfWeights = histogram2d.sumAllBinHeights()
					cloud2d._lowerEdges[0] = histogram2d.xAxis().lowerEdge()
					cloud2d._lowerEdges[1] = histogram2d.yAxis().lowerEdge()
					cloud2d._upperEdges[0] = histogram2d.xAxis().upperEdge()
					cloud2d._upperEdges[1] = histogram2d.yAxis().upperEdge()
					sumOfWeights = cloud2d.sumOfWeights()
					cloud2d._sumOfTorques[0] = histogram2d.meanX() * sumOfWeights
					cloud2d._sumOfTorques[1] = histogram2d.meanY() * sumOfWeights
					cloud2d._sumOfInertials[0] = (histogram2d.rmsX()*histogram2d.rmsX() + histogram2d.meanX()*histogram2d.meanX()) * sumOfWeights
					cloud2d._sumOfInertials[1] = (histogram2d.rmsY()*histogram2d.rmsY() + histogram2d.meanY()*histogram2d.meanY()) * sumOfWeights
				item.clear()
				break
		

class _cloud3dHandler(_namedParser):
	def __init__(self, element, fileIterator):
		_namedParser.__init__(self, element)

		self.maxEntries = int(element.get('maxEntries'))
		self.cloud3d = ICloud3D(self.name, self.title, self.maxEntries, self.options)


		# caching name for faster access
		fill = self.cloud3d.fill
		self.entries3d = False
		while 1:
			event, item = fileIterator.next()
			name = item.tag
			if name == 'entries3d':
				self.entries3d = True
				itemEntries3d = item
			elif name == 'annotation' and event == 'end':
				self.cloud3d._annotation = _annotationHandler(item).annotation
			elif name == 'entry3d' and event == 'end':
				try:
					weight = float(item.get('weight', 1.0))
				except ValueError:
					weight = self.evaluator(item.get('weight'))

				try:
					valueX = float(item.get('valueX'))
				except ValueError:
					valueX = self.evaluator(item.get('valueX'))
				try:
					valueY = float(item.get('valueY'))
				except ValueError:
					valueY = self.evaluator(item.get('valueY'))
				try:
					valueZ = float(item.get('valueZ'))
				except ValueError:
					valueZ = self.evaluator(item.get('valueZ'))

				fill(valueX, valueY, valueZ, weight)
				itemEntries3d.clear()
			elif name == 'cloud3d' and event == 'end':
				if not self.entries3d:
					histogram3d = _histogram3dHandler(element.find('histogram3d')).histogram3d 
					cloud3d = self.cloud3d
					cloud3d._histogram = histogram3d
					cloud3d._isConverted = True
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
					cloud3d._sumOfInertials[0] = (histogram3d.rmsX()*histogram3d.rmsX() + histogram3d.meanX()*histogram3d.meanX()) * sumOfWeights
					cloud3d._sumOfInertials[1] = (histogram3d.rmsY()*histogram3d.rmsY() + histogram3d.meanY()*histogram3d.meanY()) * sumOfWeights
					cloud3d._sumOfInertials[2] = (histogram3d.rmsZ()*histogram3d.rmsZ() + histogram3d.meanZ()*histogram3d.meanZ()) * sumOfWeights
				item.clear()
				break

class _profile1dHandler(_namedHandler):
	bin1d_attributes = (('entries', int), ('height', float), ('error', float), ('binNum', int), ('weightedMean', float), ('weightedRms', float), ('rms', float))

	def __init__(self, element):
		_namedHandler.__init__(self, element)

		self.axis = _axisHandler(element.find('axis'))
		self.edges = [[], [], []]
		self.edges[self.directions[self.axis.direction]] = self.axis.edge
		self.statistics = _statisticsHandler(element.find('statistics'))

		self.profile1d = IProfile1D(self.name, self.title, self.edges, self.axis.isFixedBinning, None, None, self.options)
		self.profile1d._annotation = self.annotation

		self.process_data1d(element.find('data1d'))


	def process_data1d(self, element):
		profile = self.profile1d
		statistics = self.statistics

		for bin1d in element.findall('bin1d'):
			data = {}
			for attr, _type in self.bin1d_attributes:
				try:
					data[attr] = _type(bin1d.get(attr))
				except ValueError:
					data[attr] = self.evaluator(bin1d.get(attr))

			if not data['height']:
				data['height'] = data['entries']
			if not data['error']:
				data['error'] = sqrt(data['entries'])
			if not data['weightedMean']:
				axis = profile.axis()
				if data['binNum'] == IAxis.OVERFLOW_BIN:
					data['weightedMean'] = axis.binLowerEdge(data['binNum'])
				elif data['binNum'] == IAxis.UNDERFLOW_BIN:
					data['weightedMean'] = axis.binUpperEdge(data['binNum'])
				else:
					data['weightedMean'] = (axis.binUpperEdge(data['binNum']) - axis.binLowerEdge(data['binNum'])) / 2.0
			if not data['weightedRms']:
				if data['binNum'] in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
					data['weightedRms'] = 0.0
				else:
					axis = profile.axis()
					data['weightedRms'] = statistics.rms[0] * axis.binWidth(data['binNum']) / (axis.upperEdge() - axis.lowerEdge())

			if not data['rms']:
				raise IllegalArgumentException('PAIDA needs "rms" in "profile1d.data1d.bin1d".')

			### Fill.
			innerIndex = profile._binEntries.getIndex(data['binNum'] + 2, 0)
			profile._binEntries.data[innerIndex] = entries
			if height < 0:
				profile._binSumOfTorquesY.data[innerIndex] = -(data['height']*data['height'] / (data['error']*data['error']))
			else:
				profile._binSumOfTorquesY.data[innerIndex] = data['height']*data['height'] / (data['error']*data['error'])
			binSumOfWeights = profile._binSumOfTorquesY.data[innerIndex] / data['height']
			profile._binSumOfWeights.data[innerIndex] = binSumOfWeights
			profile._binSumOfTorquesX.data[innerIndex] = binSumOfWeights * data['weightedMean']
			profile._binSumOfTorquesY.data[innerIndex] = binSumOfWeights * data['height']
			profile._binSumOfInertialsX.data[innerIndex] = binSumOfWeights * (data['weightedRms']*data['weightedRms'] + data['weightedMean']*data['weightedMean'])
			profile._binSumOfInertialsY.data[innerIndex] = binSumOfWeights * (data['rms']*data['rms'] + data['height']*data['height'])


class _profile2dHandler(_namedHandler):
	bin2d_attributes = (('entries', int), ('height', float), ('error', float), ('binNumX', int), ('binNumY', int), ('weightedMeanX', float), ('weightedRmsX', float), ('weightedMeanY', float), ('weightedRmsY', float), ('rms', float))

	def __init__(self, element):
		_namedHandler.__init__(self, element)

		self.axes = [_axisHandler(axis) for axis in element.findall('axis')]
		self.edges = [[], [], []]
		isFixedBinning = True
		for axis in self.axes:
			self.edges[self.direction[axis.direction]] = axis.edge
			if not axis.isFixedBinning:
				isFixedBinning = False
		self.statistics = _statisticsHandler(element.find('statistics'))

		self.profile2d = IProfile2D(self.name, self.title, self.edges, isFixedBinning, None, None, self.options)
		self.profile2d._annotation = self.annotation

		self.process_data2d(element.find('data2d'))


	def process_data2d(self, element):
		profile = self.profile2d
		statistics = self.statistics

		for bin2d in element.findall('bin2d'):
			data = {}
			for attr, _type in self.bin2d_attributes:
				try:
					data[attr] = _type(bin2d.get(attr))
				except ValueError:
					data[attr] = self.evaluator(bin2d.get(attr))

			if not data['height']:
				data['height'] = data['entries']
			
			if not data['error']:
				data['error'] = sqrt(data['entries'])

			if not data['weightedMeanX']:
				axis = profile.xAxis()
				if data['binNumX'] == IAxis.OVERFLOW_BIN:
					data['weightedMeanX'] = axis.binLowerEdge(data['binNumX'])
				elif data['binNumX'] == IAxis.UNDERFLOW_BIN:
					data['weightedMeanX'] = axis.binUpperEdge(data['binNumX'])
				else:
					data['weightedMeanX'] = (axis.binUpperEdge(data['binNumX']) - axis.binLowerEdge(data['binNumX'])) / 2.0
				
			if not data['weightedMeanY']:
				axis = profile.yAxis()
				if data['binNumY'] == IAxis.OVERFLOW_BIN:
					data['weightedMeanY'] = axis.binLowerEdge(data['binNumY'])
				elif data['binNumY'] == IAxis.UNDERFLOW_BIN:
					data['weightedMeanY'] = axis.binUpperEdge(data['binNumY'])
				else:
					data['weightedMeanY'] = (axis.binUpperEdge(data['binNumY']) - axis.binLowerEdge(data['binNumY'])) / 2.0

			if not data['weightedRmsX']:
				if data['binNumX'] in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
					data['weightedRmsX'] = 0.0
				else:
					axis = profile.xAxis()
					data['weightedRmsX'] = statistics.rms[0] * axis.binWidth(data['binNumX']) / (axis.upperEdge() - axis.lowerEdge())

			if not data['weightedRmsY']:
				if data['binNumY'] in [IAxis.UNDERFLOW_BIN, IAxis.OVERFLOW_BIN]:
					data['weightedRmsY'] = 0.0
				else:
					axis = profile.yAxis()
					weightedRmsY = statistics.rms[1] * axis.binWidth(data['binNumY']) / (axis.upperEdge() - axis.lowerEdge())

			if not data['rms']:
				raise IllegalArgumentException('PAIDA needs "rms" in "profile2d.data2d.bin2d".')

			### Fill.
			innerIndex = profile._binEntries.getIndex(data['binNumX'] + 2, data['binNumY'] + 2)
			profile._binEntries.data[innerIndex] = data['entries']
			if data['height'] < 0:
					profile._binSumOfTorquesZ.data[innerIndex] = -(data['height']*data['height'] / (data['error']*data['error']))
			else:
					profile._binSumOfTorquesZ.data[innerIndex] = data['height']*data['height'] / (data['error']*data['error'])
			binSumOfWeights = profile._binSumOfTorquesZ.data[innerIndex] / data['height']
			profile._binSumOfWeights.data[innerIndex] = binSumOfWeights
			profile._binSumOfTorquesX.data[innerIndex] = binSumOfWeights * data['weightedMeanX']
			profile._binSumOfTorquesY.data[innerIndex] = binSumOfWeights * data['weightedMeanY']
			profile._binSumOfTorquesZ.data[innerIndex] = binSumOfWeights * data['height']
			profile._binSumOfInertialsX.data[innerIndex] = binSumOfWeights * (data['weightedRmsX']*data['weightedRmsX'] + data['weightedMeanX']*data['weightedMeanX'])
			profile._binSumOfInertialsY.data[innerIndex] = binSumOfWeights * (data['weightedRmsY']*data['weightedRmsY'] + data['weightedMeanY']*data['weightedMeanY'])
			profile._binSumOfInertialsZ.data[innerIndex] = binSumOfWeights * (data['rms']*data['rms'] + data['height']*data['height'])


class _dataPointSetHandler(_namedHandler):
	def __init__(self, element, fileIterator):
		_namedHandler.__init__(self, element)

		self.dimension = int(element.get('dimension'))
		self.dataPointSet = IDataPointSet(self.name, self.title, self.dimension)
		self.dataPointSet._annotation = self.annotation
		self.process_dataPoint(fileIterator, element)

	def process_dataPoint(self, fileIterator, toBeCleared):
		while 1:
			event, item = fileIterator.next()
			name = item.tag
			if name == 'dataPoint':
				if event == 'start':
					dataPoint = self.dataPointSet.addPoint()
					coordinate = 0
				else:
					toBeCleared.clear()
			elif name == 'measurement' and event == 'end':
				value = float(item.get('value'))
				try:
					errorPlus = float(item.get('errorPlus', 0.0))
				except ValueError:
					errorPlus = self.evaluator(item.get('errorPlus'))
				try:
					errorMinus = float(item.get('errorMinus', errorPlus))
				except ValueError:
					errorMinus = self.evaluator(item.get('errorMinus'))
				### Fill.
				measurement = dataPoint.coordinate(coordinate)
				measurement.setValue(value)
				measurement.setErrorPlus(errorPlus)
				measurement.setErrorMinus(errorMinus)
				coordinate += 1
			elif name == 'dataPointSet' and event == 'end':
				break


class _functionHandler(_namedHandler):
	def __init__(self, element, functionFactory):
		_namedHandler.__init__(self, element)
		self.isNormalized = (element.get('isNormalized') == u'true')
		codelet = self.process_codelet(element.find('codelet'))
		self.function = functionFactory._createCopy(codelet, self.name, inner = False)
		self.process_parameters(element.find('parameters'))

	def process_codelet(self, element):
		oneLine = ''.join(element.text.splitlines())
		codelet = oneLine.strip()

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
		return codelet

	def process_parameters(self, element):
		for parameter in element.findall('parameter'):
			name = parameter.get('name')
			try:
				value = float(parameter.get('value'))
			except ValueError:
				value = self.evaluator(parameter.get('value'))
			self.function.setParameter(name, value)


class ITree:
		_entities = {'"': '&quot;', "'": "&apos;"}

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
				if fileName is None:
					guiTree.setTitle('PAIDA tree')
				else:
					guiTree.setTitle(fileName)
					### Check if the file is zipped or normal.
					try:
						import gzip
						### Jython2.1 fails to gzip.open with 'r' argument.
						fileObj = gzip.open(fileName, 'r')
						fileObj.read(1)
						fileObj.seek(0)
					except ImportError:
						print 'PAIDA: gzip module is unavailable.'
						print 'PAIDA: all files are treated as unzipped.'
						fileObj = file(fileName, 'r')
					except IOError:
						fileObj.close()
						fileObj = file(fileName, 'r')
											
					_aidaHandler(fileObj, self)
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
				if self._fileName is None:
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
								if currentPosition._parent is None:
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
				if position._instance is None:
						self._pwd = position
						if update:
								self._treeUpdate(block)
				else:
						###Not directory.
						raise IllegalArgumentException()

		def find(self, path):
				position = self._internalFind(path)
				if position._instance is None:
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
				if position._instance is not None:
						###Analysis object.
						result.append(position)
				else:
						subDirectories = []
						for child in position._children:
								result.append(child)
								if child._instance is None:
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
						if child._instance is None:
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
								if object._instance is None:
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
						if object._instance is None:
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
				if current is None:
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
				if position._instance is None:
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
				if position._parent is None:
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
				if object._instance is None:
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
				if position._tree is None:
						raise IllegalArgumentException()
				return position._tree

		def unmount(self, path, update = True, block = True):
				unmountPosition = self._internalFind(path)
				if unmountPosition._tree is None:
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
				if object._instance._option is None:
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
				if object._option is None:
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
				if object._option is None:
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
				if object._option is None:
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
				if object._option is None:
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
				if object._option is None:
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
				if object._option is None:
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
				if object._option is None:
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
								if columnDefault is None:
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
								if columnDefault is None:
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
										if rowData[columnIndex] is None:
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
						if object._instance is None:
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


