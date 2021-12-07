from paida.paida_core.PAbsorber import *
from paida.math.pylapack.pyblas.xerbla import xerbla
from paida.math.pylapack.pyblas.lsame import lsame

def dgemm(transa, transb, m, n, k, alpha, a, lda, b, ldb, beta, c, ldc):
	"""Written on 8-February-1989.
	Jack Dongarra, Argonne National Laboratory.
	Iain Duff, AERE Harwell.
	Jeremy Du Croz, Numerical Algorithms Group Ltd.
	Sven Hammarling, Numerical Algorithms Group Ltd.
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Level 3 Blas routine.
	
	Purpose
	=======
	
	dgemm performs one of the matrix-matrix operations
		C := alpha*op( A )*op( B ) + beta*C,
	where op( X ) is one of
		op( X ) = X or op( X ) = X',
	alpha and beta are scalars,
	and A, B and C are matrices,
	with op( A ) an m by k matrix,
	op( B ) a k by n matrix
	and C an m by n matrix.
	
	Parameters
	==========
	
	transa - character
	On entry, transa specifies the form of op( A )
	to be used in the matrix multiplication as follows:
		transa = 'N' or 'n',  op( A ) = A.
		transa = 'T' or 't',  op( A ) = A'.
		transa = 'C' or 'c',  op( A ) = A'.
	Unchanged on exit.
	
	transb - character
	On entry, transb specifies the form of op( B )
	to be used in the matrix multiplication as follows:
		transb = 'N' or 'n',  op( B ) = B.
		transb = 'T' or 't',  op( B ) = B'.
		transb = 'C' or 'c',  op( B ) = B'.
	Unchanged on exit.
	
	m - integer
	On entry, m specifies the number of rows of the matrix op( A ) and of the matrix C.
	m must be at least zero.
	Unchanged on exit.
	
	n - integer
	On entry, n specifies the number of columns of the matrix op( B )
	and of the number of columns of the matrix C.
	n must be at least zero.
	Unchanged on exit.
	
	k - integer
	On entry, k specifies the number of columns of the matrix op( A )
	and the number of rows of the matrix op( B ).
	k must be at least zero.
	Unchanged on exit.
	
	alpha - double
	On entry, alpha specifies the scalar alpha.
	Unchanged on exit.
	
	a - double array of dimension at least (min(k, m), min(k, m)).
	Before entry with transa[0] = 'N' or 'n',
	the leading m by k part of the array A must contain the matrix A,
	otherwise the leading k by m part of the array A must contain the matrix A.
	Unchanged on exit.
	
	lda - leading dimension.
	In almost all cases, it is for compatibility.
	
	b - double array of dimension at least (min(k, n), min(k, n)).
	Before entry with transa[0] = 'N' or 'n',
	the leading n by k part of the array b must contain the matrix B,
	otherwise the leading k by n part of the array b must contain the matrix B.
	Unchanged on exit.
	
	ldb - leading dimension.
	In almost all cases, it is for compatibility.
	
	beta - double
	On entry, beta specifies the scalar beta.
	When beta is supplied as zero then C need not be set on input.
	Unchanged on exit.
	
	C - double array of dimension at least (max(l, m), n).
	Before entry, the leading m by n part of the array C must contain the matrix C,
	except when beta is zero, in which case C need not be set on entry.
	On exit, the array C is overwritten by the m by n matrix ( alpha*op( A )*op( B ) + beta*C ).
	
	ldc - leading dimension.
	In almost all cases, it is for compatibility.
	
	External Subroutines
	====================
	
	lsame, xerbla
	"""
	
	one = 1.0e+0
	zero = 0.0e+0
	
	### Set NOTA and NOTB as true if A and B respectively are not transposed
	### and set NROWA, NCOLA and NROWB as the number of rows
	### and columns of A and the number of rows of B respectively.
	nota = lsame(transa, 'N')
	notb = lsame(transb, 'N')
	if nota:
		nrowa = m
		ncola = k
	else:
		nrowa = k
		ncola = m
	if notb:
		nrowb = k
	else:
		nrowb = n
		
	### Test the input parameters.
	info[0] = 0
	if (not nota) and (not lsame(transa, 'C')) and (not lsame(transa, 'T')):
		info[0] = 1
	elif (not notb) and (not lsame(transb, 'C')) and (not lsame(transb, 'T')):
		info[0] = 2
	elif m < 0:
		info[0] = 3
	elif n < 0:
		info[0] = 4
	elif k < 0:
		info[0] = 5
	if info[0] != 0:
		xerbla('dgemm', info)
		return
	
	### Quick return if possible.
	if (m == 0) or (n == 0) or (((alpha == 0) or (k == 0)) and (beta == one)):
		return
	
	### And if alpha == zero.
	if alpha == zero:
		if beta == zero:
			for j in range(1, n + 1):
				for i in range(1, m + 1):
					c[j - 1, i - 1] = zero
		else:
			for j in range(1, n + 1):
				for i in range(1, m + 1):
					c[j - 1, i - 1] *= beta
		return
	
	### Start the operations.
	if notb:
		if nota:
			### Form  C := alpha*A*B + beta*C.
			for j in range(1, n + 1):
				if beta == zero:
					for i in range(1, m + 1):
						c[j - 1, i - 1] = zero
				elif beta != one:
					for i in range(1, m + 1):
						c[j - 1, i - 1] *= beta
				for l in range(1, k + 1):
					if b[j - 1, l - 1] != zero:
						temp = alpha * b[j - 1, l - 1]
						for i in range(1, m + 1):
							c[j - 1, i - 1] += temp * a[l - 1, i - 1]
		else:
			### Form  C := alpha*A'*B + beta*C
			for j in range(1, n + 1):
				for i in range(1, m + 1):
					temp = zero
					for l in range(1, k + 1):
						temp += a[i - 1, l - 1] * b[j - 1, l - 1]
					if beta == zero:
						c[j - 1, i - 1] = alpha * temp
					else:
						c[j - 1, i - 1] = alpha * temp + beta * c[j - 1, i - 1]
	else:
		if nota:
			### Form  C := alpha*A*B' + beta*C
			for j in range(1, n + 1):
				if beta == zero:
					for i in range(1, m + 1):
						c[j - 1, i - 1] = zero
				elif beta != one:
					for i in range(1, m + 1):
						c[j - 1, i - 1] *= beta
				for l in range(1, k + 1):
					if b[l - 1, j - 1] != zero:
						temp = alpha * b[l - 1, j - 1]
						for i in range(1, m + 1):
							c[j - 1, i - 1] += temp * a[l - 1, i - 1]
		else:
			### Form  C := alpha*A'*B' + beta*C
			for j in range(1, n + 1):
				for i in range(1, m + 1):
					temp = zero
					for l in range(1, k + 1):
						temp += a[i - 1, l - 1] * b[l - 1, j - 1]
					if beta == zero:
						c[j - 1, i - 1] = alpha * temp
					else:
						c[j - 1, i - 1] = alpha * temp + beta * c[j - 1, i - 1]
	return
