from paida.paida_core.PAbsorber import *
from paida.math.pylapack.pyblas.xerbla import xerbla

def dger(m, n, alpha, x, incx, y, incy, a, lda):
	"""Level 2 Blas routine.
	Written on 22-October-1986.
	Jack Dongarra, Argonne National Lab.
	Jeremy Du Croz, Nag Central Office.
	Sven Hammarling, Nag Central Office.
	Richard Hanson, Sandia National Labs.
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	dger performs the rank 1 operation
		A := alpha*x*y' + A,
	where alpha is a scalar,
	x is an m element vector,
	y is an n element vector
	and A is an m by n matrix.
	
	Parameters
	==========
	
	m - integer
	On entry, M specifies the number of rows of the matrix A.
	M must be at least zero.
	Unchanged on exit.
	
	n - integer
	On entry, N specifies the number of columns of the matrix A.
	N must be at least zero.
	Unchanged on exit.
	
	alpha - double
	On entry, alpha specifies the scalar alpha.
	Unchanged on exit.
	
	x - double array of dimension at least (1 + (m - 1) * abs(incx))
	Before entry, the incremented array X must contain the m element vector x.
	Unchanged on exit.
	
	incx - integer
	On entry, INCX specifies the increment for the elements of X.
	INCX must not be zero.
	Unchanged on exit.
	
	y - double array of dimension at least (1 + (n - 1) * abs(incy))
	Before entry, the incremented array Y must contain the m element vector y.
	Unchanged on exit.
	
	incy - integer
	On entry, INCY specifies the increment for the elements of Y.
	INCY must not be zero.
	Unchanged on exit.
	
	a - double array of dimension at least (m, n)
	Before entry, the leading m by n part of the array A must contain the matrix of coefficients.
	On exit, A is overwritten by the updated matrix.
	
	lda - leading dimension.
	In almost all cases, it is for compatibility.
	
	External Subroutines
	====================
	
	xerbla
	"""
	
	zero = 0.0e+0
	
	### Test the input parameters.
	info = [0]
	if m < 0:
		info[0] = 1
	elif n < 0:
		info[0] = 2
	elif incx == 0:
		info[0] = 5
	elif incy == 0:
		info[0] = 7
	if info[0] != 0:
		xerbla('dger', info)
		return
	
	### Quick return if possible.
	if (m == 0) or (n == 0) or (alpha == zero):
		return
	
	### Start the operations.
	### In this version the elements of A are accessed sequentially with one pass through A.
	if incy > 0:
		jy = 1
	else:
		jy = 1 - (n - 1) * incy
	if incx == 1:
		for j in range(1, n + 1):
			if y[jy - 1] != zero:
				temp = alpha * y[jy - 1]
				for i in range(1, m + 1):
					a[j - 1, i - 1] += x[i - 1] * temp
			jy += incy
	else:
		if incx > 0:
			kx = 1
		else:
			kx = 1 - (m - 1) * incx
		for j in range(1, n + 1):
			if y[jy - 1] != zero:
				temp = alpha * y[jy - 1]
				ix = kx
				for i in range(1, m + 1):
					a[j - 1, i - 1] += x[ix - 1] * temp
					ix += incx
			jy += incy
	return