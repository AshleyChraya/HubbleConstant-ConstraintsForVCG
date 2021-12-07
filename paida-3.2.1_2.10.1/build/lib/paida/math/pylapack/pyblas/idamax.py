from paida.paida_core.PAbsorber import *
from math import fabs

def idamax(n, dx, incx):
	"""finds the index of element having max. absolute value.
	jack dongarra, linpack, 3/11/78.
	modified 3/93 to return if incx .le. 0.
	modified 12/3/93, array(1) declarations changed to array(*)
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	"""
	
	result = 0
	if (n < 1) or (incx <= 0):
		return result
	result = 1
	if n == 1:
		return result
	if incx == 1:
		dmax = fabs(dx[0])
		for i in range(2, n + 1):
			if fabs(dx[i - 1]) <= dmax:
				return result
			else:
				result = i
				dmax = fabs(dx[i - 1])
		return result
	else:
		### code for increment not equal to 1
		ix = 1
		dmax = fabs(dx[0])
		ix += incx
		for i in range(2, n + 1):
			if fabs(dx[ix - 1]) < dmax:
				result = i
				dmax = fabs(dx[ix - 1])
			ix += incx
		return result
