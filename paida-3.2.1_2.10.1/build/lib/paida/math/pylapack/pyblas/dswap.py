from paida.paida_core.PAbsorber import *
def dswap(n, dx, incx, dy, incy):
	"""interchanges two vectors.
	uses unrolled loops for increments equal one.
	jack dongarra, linpack, 3/11/78.
	modified 12/3/93, array(1) declarations changed to array(*)
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	"""
	
	if n <= 0:
		return
	if (incx == 1) and (incy == 1):
		### code for both increments equal to 1
		m = n % 3
		if m != 0:
			for i in range(1, m + 1):
				dtemp = dx[i - 1]
				dx[i - 1] = dy[i - 1]
				dy[i - 1] = dtemp
			if n < 3:
				return
		mp1 = m + 1
		for i in range(mp1, n + 1, 3):
			dtemp = dx[i - 1]
			dx[i - 1] = dy[i - 1]
			dy[i - 1] = dtemp
			dtemp = dx[i]
			dx[i] = dy[i]
			dy[i] = dtemp
			dtemp = dx[i + 1]
			dx[i + 1] = dy[i + 1]
			dy[i + 1] = dtemp
		return
	else:
		### code for unequal increments or equal increments not equal to 1
		ix = 1
		iy = 1
		if incx < 0:
			ix = (1 - n) * incx + 1
		if incy < 0:
			iy = (1 - n) * incy + 1
		for i in range(1, n + 1):
			dtemp = dx[ix - 1]
			dx[ix - 1] = dy[iy - 1]
			dy[iy - 1] = dtemp
			ix += incx
			iy += incy
		return
