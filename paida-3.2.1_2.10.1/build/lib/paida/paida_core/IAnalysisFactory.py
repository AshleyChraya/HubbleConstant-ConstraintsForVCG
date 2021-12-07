from paida.paida_core.PAbsorber import *
from paida.paida_core.IDataPointSetFactory import *
from paida.paida_core.IFitFactory import *
from paida.paida_core.IFunctionFactory import *
from paida.paida_core.IHistogramFactory import *
from paida.paida_core.IPlotterFactory import *
from paida.paida_core.ITreeFactory import *
from paida.paida_core.ITupleFactory import *
from paida.paida_core.PExceptions import RuntimeException
import paida.paida_gui.PRoot

def _create():
	paida.paida_gui.PRoot.createRoot()
	guiRoot = paida.paida_gui.PRoot.getRoot()
	rootCondition = guiRoot._getRootCondition()
	rootCondition.acquire()
	paida.paida_gui.PRoot.startRoot()
	rootCondition.wait()
	rootCondition.release()

def create():
	try:
		### IPython support.
		_raw_input_original = __IPYTHON__.raw_input
	except NameError:
		_create()
	else:
		### Running source file?
		### (Comment: This check is not needed? Simply calling _create() seems to work.)
		if __IPYTHON__.rc.args:
			### Yes.
			_create()
		else:
			### No.
			def _raw_input_new(prompt, more):
				_create()
				__IPYTHON__.raw_input = _raw_input_original
				return ''
			__IPYTHON__.raw_input = _raw_input_new

	analysisFactory = IAnalysisFactory()

	import atexit
	atexit.register(analysisFactory._atexit)

	return analysisFactory

class IAnalysisFactory:
	def _atexit(self):
		root = paida.paida_gui.PRoot.getRoot()
		root._getLock().acquire()
		root._setQuitLoop(True)
		root._getLock().release()

	def createTreeFactory(self):
		return ITreeFactory()

	def createHistogramFactory(self, tree):
		return IHistogramFactory(tree)

	def createDataPointSetFactory(self, tree):
		return IDataPointSetFactory(tree)

	def createTupleFactory(self, tree):
		return ITupleFactory(tree)

	def createFunctionFactory(self, tree):
		return IFunctionFactory(tree)

	def createPlotterFactory(self):
		return IPlotterFactory()

	def createFitFactory(self):
		return IFitFactory()
