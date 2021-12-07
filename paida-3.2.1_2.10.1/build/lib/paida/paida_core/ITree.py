### Check which backend should be used.
try:
	import xml.etree.cElementTree as ET
	from paida.paida_core.ITreeElementTree import *
except ImportError:
	try:
		import cElementTree as ET
		from paida.paida_core.ITreeElementTree import *
	except:
		from paida.paida_core.ITreeOld import *
except:
	from paida.paida_core.ITreeOld import *
