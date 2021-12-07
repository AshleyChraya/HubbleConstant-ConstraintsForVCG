from paida.paida_core.PAbsorber import *
def dscal(n, da, dx, incx):
	"""scales a vector by a constant.
	uses unrolled loops for increment equal to one.
	jack dongarra, linpack, 3/11/78.
	modified 3/93 to return if incx .le. 0.
	modified 12/3/93, array(1) declarations changed to array(*)
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	"""
	
	if (n <= 0) or (incx <= 0):
		return
	if incx == 1:
		### code for increment equal to 1
		m = n % 5
		if m != 0:
			for i in range(1, m + 1):
				dx[i - 1] *= da
			if n < 5:
				return
		mp1 = m + 1
		for i in range(mp1, n + 1, 5):
			dx[i - 1] *= da
			dx[i] *= da
			dx[i + 1] *= da
			dx[i + 2] *= da
			dx[i + 3] *= da
		return
	else:
		### code for increment not equal to 1
		nincx = n * incx
		for i in range(1, nincx + 1, incx):
			dx[i - 1] *= da
		return
