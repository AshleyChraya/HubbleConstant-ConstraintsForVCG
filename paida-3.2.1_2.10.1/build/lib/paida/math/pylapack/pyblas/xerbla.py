from paida.paida_core.PAbsorber import *
class stop:
	"""Exception class of replacement with fortran 'STOP'"""
	### If you want to exit, comment out the following lines.
	### def __init__(self):
	### 	import sys
	### 	sys.exit(0)
	pass

def xerbla(srname, info):
	"""LAPACK auxiliary routine (version 3.0)
	Univ. of Tennessee, Univ. of California Berkeley, NAG Ltd.,
	Courant Institute, Argonne National Lab, and Rice University
	September 30, 1994
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	xerbla is an error handler for the LAPACK routines.
	It is called by an LAPACK routine if an input parameter has an invalid value.
	A message is printed and raises stop exception.
	
	Arguments
	=========
	
	srname (input) character
	The name of the routine which called xerbla.
	
	info (input) integer array, dimension (1)
	The position of the invalid parameter in the parameter list of the calling routine.
	"""
	
	print ' ** On entry to %s parameter number %d had an illegal value' % (srname, info[0])
	raise stop()
