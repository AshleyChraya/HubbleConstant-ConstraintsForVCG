from paida.paida_core.PAbsorber import *
from paida.paida_core.PExceptions import RuntimeException
import paida.paida_gui.PGuiSelector

guiEngineName = paida.paida_gui.PGuiSelector.getGuiEngineName()
if guiEngineName == 'firefox':
	from paida.paida_gui.firefox.PRoot import *
elif guiEngineName == 'matplotlib':
	from paida.paida_gui.matplotlib.PRoot import *
elif guiEngineName == 'tkinter':
	from paida.paida_gui.tkinter.PRoot import *
elif guiEngineName == 'swing':
	from paida.paida_gui.swing.PRoot import *
elif guiEngineName == 'batch':
	from paida.paida_gui.batch.PRoot import *
else:
	raise RuntimeException()
