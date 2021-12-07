from paida.paida_core.PAbsorber import *
from paida.math.pylapack.pyblas.lsame import lsame
from paida.math.pylapack.pyblas.xerbla import xerbla

def dtrsm(side, uplo, transa, diag, m, n, alpha, a, lda, b, ldb):
	"""Level 3 Blas routine.
	Written on 8-February-1989.
	Jack Dongarra, Argonne National Laboratory.
	Iain Duff, AERE Harwell.
	Jeremy Du Croz, Numerical Algorithms Group Ltd.
	Sven Hammarling, Numerical Algorithms Group Ltd.
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	dtrsm  solves one of the matrix equations
		op( A )*X = alpha*B,   or   X*op( A ) = alpha*B,
	where alpha is a scalar,
	X and B are m by n matrices,
	A is a unit, or non-unit, upper or lower triangular matrix
	and op( A ) is one of
		op( A ) = A   or   op( A ) = A'.
	The matrix X is overwritten on B.
	
	Parameters
	==========
	
	side - character
	On entry, SIDE specifies whether op( A ) appears on the left or right of X as follows:
		SIDE = 'L' or 'l'   op( A )*X = alpha*B.
		SIDE = 'R' or 'r'   X*op( A ) = alpha*B.
	Unchanged on exit.
	
	uplo - character
	On entry, UPLO specifies whether the matrix A is an upper or lower triangular matrix as follows:
		UPLO = 'U' or 'u'   A is an upper triangular matrix.
		UPLO = 'L' or 'l'   A is a lower triangular matrix.
	Unchanged on exit.
	
	transa - character
	On entry, TRANSA specifies the form of op( A ) to be used in the matrix multiplication as follows:
		TRANSA = 'N' or 'n'   op( A ) = A.
		TRANSA = 'T' or 't'   op( A ) = A'.
		TRANSA = 'C' or 'c'   op( A ) = A'.
	Unchanged on exit.
	
	diag - character
	On entry, DIAG specifies whether or not A is unit triangular as follows:
		DIAG = 'U' or 'u'   A is assumed to be unit triangular.
		DIAG = 'N' or 'n'   A is not assumed to be unit triangular.
	Unchanged on exit.
	
	m - integer
	On entry, M specifies the number of rows of B. M must be at least zero.
	Unchanged on exit.
	
	n - integer
	On entry, N specifies the number of columns of B. N must be at least zero.
	Unchanged on exit.
	
	alpha - double
	On entry, ALPHA specifies the scalar alpha.
	When alpha is zero then A is not referenced and B need not be set before entry.
	Unchanged on exit.
	
	a - double array of dimension (lda, k)
	where k is m when SIDE = 'L' or 'l' and is n when SIDE = 'R' or 'r'.
	Before entry  with  UPLO = 'U' or 'u',
	the leading k by k upper triangular part of the array A must contain the upper triangular matrix
	and the strictly lower triangular part of A is not referenced.
	Before entry with UPLO = 'L' or 'l',
	the leading k by k lower triangular part of the array A must contain the lower triangular matrix
	and the strictly upper triangular part of A is not referenced.
	Note that when DIAG = 'U' or 'u',
	the diagonal elements of A are not referenced either, but are assumed to be unity.
	Unchanged on exit.
	
	lda - integer
	On entry, LDA specifies the first dimension of A as declared in the calling (sub) program.
	When SIDE = 'L' or 'l' then LDA must be at least max( 1, m ),
	when SIDE = 'R' or 'r' then LDA must be at least max( 1, n ).
	Unchanged on exit.
	
	b - double array of dimension (ldb, n)
	Before entry, the leading m by n part of the array B must contain the right-hand side matrix B,
	and on exit is overwritten by the solution matrix X.
	
	ldb - integer
	On entry, LDB specifies the first dimension of b as declared in the calling (sub) program.
	LDB must be at least max( 1, m ).
	Unchanged on exit.
	
	External Subroutines
	====================
	
	lsame, xerbla
	"""
	
	one = 1.0e+0
	zero = 0.0e+0
	
	### Test the input parameters.
	lside = lsame(side, 'L')
	if lside:
		nrowa = m
	else:
		nrowa = n
	nounit = lsame(diag, 'N')
	upper = lsame(uplo, 'U')
	
	info = [0]
	if (not lside) and (not lsame(side, 'R')):
		info[0] = 1
	elif (not upper) and (not lsame(uplo, 'L')):
		info[0] = 2
	elif (not lsame(transa, 'N')) and (not lsame(transa, 'T')) and (not lsame(transa, 'C')):
		info[0] = 3
	elif (not lsame(diag, 'U')) and (not lsame(diag, 'N')):
		info[0] = 4
	elif m < 0:
		info[0] = 5
	elif n < 0:
		info[0] = 6
	if info[0] != 0:
		xerbla('dtrsm', info)
		return
	
	### Quick return if possible.
	if n == 0:
		return
	
	### And when alpha.eq.zero.
	if alpha == zero:
		for j in range(1, n + 1):
			for i in range(1, m + 1):
				b[j - 1, i - 1] = zero
		return
	
	### Start the operations.
	if lside:
		if lsame(transa, 'N'):
			### Form  B := alpha*inv( A )*B.
			if upper:
				for j in range(1, n + 1):
					if alpha != one:
						for i in range(1, m + 1):
							b[j - 1, i - 1] *= alpha
					for k in range(m, 0, -1):
						if b[j - 1, k - 1] != zero:
							if nounit:
								b[j - 1, k - 1] /= a[k - 1, k - 1]
							for i in range(1, k):
								b[j - 1, i - 1] -= b[j - 1, k - 1] * a[k - 1, i - 1]
			else:
				for j in range(1, n + 1):
					if alpha != one:
						for i in range(1, m + 1):
							b[j - 1, i - 1] *= alpha
					for k in range(1, m + 1):
						if b[j - 1, k - 1] != zero:
							if nounit:
								b[j - 1, k - 1] /= a[k - 1, k - 1]
							for i in range(k + 1, m + 1):
								b[j - 1, i - 1] -= b[j - 1, k - 1] * a[k - 1, i - 1]
		else:
			### Form  B := alpha*inv( A' )*B.
			if upper:
				for j in range(1, n + 1):
					for i in range(1, m + 1):
						temp = alpha * b[j - 1, i - 1]
						for k in range(1, i):
							temp -= a[i - 1, k - 1] * b[j - 1, k - 1]
						if nounit:
							temp /= a[i - 1, i - 1]
						b[j - 1, i - 1] = temp
			else:
				for j in range(1, n + 1):
					for i in range(m, 0, -1):
						temp = alpha * b[j - 1, i - 1]
						for k in range(i + 1, m + 1):
							temp -= a[i - 1, k - 1] * b[j - 1, k - 1]
						if nounit:
							temp /= a[i - 1, i - 1]
						b[j - 1, i - 1] = temp
	else:
		if lsame(transa, 'N'):
			### Form  B := alpha*B*inv( A ).
			if upper:
				for j in range(1, n + 1):
					if alpha != one:
						for i in range(1, m + 1):
							b[j - 1, i - 1] *= alpha
					for k in range(1, j):
						if a[j - 1, k - 1] != zero:
							for i in range(1, m + 1):
								b[j - 1, i - 1] -= a[j - 1, k - 1] * b[k - 1, i - 1]
					if nounit:
						temp = one / a[j - 1, j - 1]
						for i in range(1, m + 1):
							b[j - 1, i - 1] *= temp
			else:
				for j in range(n, 0, -1):
					if alpha != one:
						for i in range(1, m + 1):
							b[j - 1, i - 1] *= alpha
					for k in range(j + 1, n + 1):
						if a[j - 1, k - 1] != zero:
							for i in range(1, m + 1):
								b[j - 1, i - 1] -= a[j - 1, k - 1] * b[k - 1, i - 1]
					if nounit:
						temp = one / a[j - 1, j - 1]
						for i in range(1, m + 1):
							b[j - 1, i - 1] *= temp
		else:
			### Form  B := alpha*B*inv( A' ).
			if upper:
				for k in range(n, 0, -1):
					if nounit:
						temp = one / a[k - 1, k - 1]
						for i in range(1, m + 1):
							b[k - 1, i - 1] *= temp
					for j in range(1, k):
						if a[k - 1, j - 1] != zero:
							temp = a[k - 1, j - 1]
							for i in range(1, m + 1):
								b[j - 1, i - 1] -= temp * b[k - 1, i - 1]
					if alpha != one:
						for i in range(1, m + 1):
							b[k - 1, i - 1] *= alpha
			else:
				for k in range(1, n + 1):
					if nounit:
						temp = one / a[k - 1, k - 1]
						for i in range(1, m + 1):
							b[k - 1, i - 1] *= temp
					for j in range(k + 1, n + 1):
						if a[k - 1, j - 1] != zero:
							temp = a[k - 1, j - 1]
							for i in range(1, m + 1):
								b[j - 1, i - 1] -= temp * b[k - 1, i - 1]
					if alpha != one:
						for i in range(1, m + 1):
							b[k - 1, i - 1] *= alpha
	return
