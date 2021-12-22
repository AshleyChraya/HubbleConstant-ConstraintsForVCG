"""A pure Python package for the scientific data analysis and plotting

PAIDA is pure Python scientific analysis package.
The main features are:

 - Pure Python! (so works on both Python and Jython)
 - AIDA (Abstract Interfaces for Data Analysis) support
 - Creating/Plotting the histogram, ntuple, profile and cloud
 - Function fitting (parameter optimization) with constraints and its parabolic and asymmetric errors evaluation
 - XML based storing
 - Matrix calculation

PAIDA web site:
http://paida.sourceforge.net/

AIDA project has other implementations like Java (JAIDA), C++ etc. (Open Scientist and Anaphe).
For more information about AIDA itself, please refer to
http://aida.freehep.org/
"""

from distutils.core import setup
import os

doclines = __doc__.split(os.linesep)

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
License :: OSI Approved :: Python Software Foundation License
Operating System :: OS Independent
Programming Language :: Java
Programming Language :: Python
Topic :: Scientific/Engineering
"""

packages = ['paida',
	'paida.paida_core',
	'paida.paida_core.PAbsorber',
	'paida.paida_gui',
	'paida.paida_gui.batch',
	'paida.paida_gui.tkinter',
	'paida.paida_gui.swing',
	'paida.paida_gui.firefox',
	'paida.paida_gui.matplotlib',
	'paida.math',
	'paida.math.optimize',
	'paida.math.pylapack',
	'paida.math.pylapack.pyblas',
	'paida.math.array',
	'paida.tools']

setup (name = "paida",
       version = "3.2.1_2.10.1",
       author = "Koji Kishimoto",
       author_email = "korry@users.sourceforge.net",
       url = "http://paida.sourceforge.net/",
       license = "Python Software Foundation License",
       platforms = ["any"],
       description = doclines[0],
       long_description = os.linesep.join(doclines[2:]),
       classifiers = filter(None, classifiers.split(os.linesep)),
       packages = packages
       )
