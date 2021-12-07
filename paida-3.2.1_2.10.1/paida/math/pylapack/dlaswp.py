from paida.paida_core.PAbsorber import *
def dlaswp(n, a, lda, k1, k2, ipiv, incx):
	"""LAPACK auxiliary routine (version 3.0)
	Univ. of Tennessee, Univ. of California Berkeley, NAG Ltd.,
	Courant Institute, Argonne National Lab, and Rice University
	June 30, 1999
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	dlaswp performs a series of row interchanges on the matrix A.
	One row interchange is initiated for each of rows K1 through K2 of A.
	
	Arguments
	=========
	
	n (input) integer
	The number of columns of the matrix A.
	
	a (input/output) double array, dimension (lda, n)
	On entry, the matrix of column dimension N to which the row interchanges will be applied.
	On exit, the permuted matrix.
	
	lda (input) integer
	The leading dimension of the array A.
	In almost all cases, it is for compatibility.
	
	k1 (input) integer
	The first element of IPIV for which a row interchange will be done.
	
	k2 (input) integer
	The last element of IPIV for which a row interchange will be done.
	
	ipiv (input) integer array, dimension (M * abs(incx))
	The vector of pivot indices.
	Only the elements in positions K1 through K2 of IPIV are accessed.
	IPIV(K) = L implies rows K and L are to be interchanged.
	
	incx (input) integer
	The increment between successive values of IPIV.
	If IPIV is negative, the pivots are applied in reverse order.
	
	Further Details
	===============
	
	Modified by
	 R. C. Whaley, Computer Science Dept., Univ. of Tenn., Knoxville, USA
	"""
	
	### Interchange row I with row IPIV(I) for each of rows K1 through K2.
	if incx > 0:
		ix0 = k1
		i1 = k1
		i2 = k2
		inc = 1
	elif incx < 0:
		ix0 = 1 + (1 - k2) * incx
		i1 = k2
		i2 = k1
		inc = -1
	else:
		return
	
	n32 = (n / 32) * 32
	if n32 != 0:
		for j in range(1, n32 + 1, 32):
			ix = ix0
			for i in range(i1, i2, inc):
				ip = ipiv[ix - 1]
				if ip != i:
					for k in range(j, j + 32):
						temp = a[k - 1, i - 1]
						a[k - 1, i - 1] = a[k - 1, ip - 1]
						a[k - 1, ip - 1] = temp
				ix += incx
	if n32 != n:
		n32 += 1
		ix = ix0
		for i in range(i1, i2 +1, inc):
			ip = ipiv[ix - 1]
			if ip != i:
				for k in range(n32, n + 1):
					temp = a[k - 1, i - 1]
					a[k - 1, i - 1] = a[k - 1, ip - 1]
					a[k - 1, ip - 1] = temp
			ix += incx
	return
