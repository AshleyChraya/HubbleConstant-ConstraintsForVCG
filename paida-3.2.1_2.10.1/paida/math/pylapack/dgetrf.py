from paida.paida_core.PAbsorber import *
from paida.math.pylapack.ilaenv import ilaenv
from paida.math.pylapack.dgetf2 import dgetf2
from paida.math.pylapack.dlaswp import dlaswp
from paida.math.pylapack.pyblas.dgemm import dgemm
from paida.math.pylapack.pyblas.dtrsm import dtrsm
from paida.math.pylapack.pyblas.xerbla import xerbla

def dgetrf(m, n, a, lda, ipiv, info):
	"""LAPACK routine (version 3.0)
	Univ. of Tennessee, Univ. of California Berkeley, NAG Ltd.,
	Courant Institute, Argonne National Lab, and Rice University
	March 31, 1993
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	dgetrf computes an LU factorization of a general M-by-N matrix A
	using partial pivoting with row interchanges.
	
	The factorization has the form
		A = P * L * U
	where P is a permutation matrix,
	L is lower triangular with unit diagonal elements (lower trapezoidal if m > n),
	and U is upper triangular (upper trapezoidal if m < n).
	
	This is the right-looking Level 3 BLAS version of the algorithm.
	
	Arguments
	=========
	
	m (input) integer
	The number of rows of the matrix a. m >= 0.
	
	n (input) integer
	The number of columns of the matrix a. n >= 0.
	
	a (input/output) double array, dimension at least (m, n)
	On entry, the m-by-n matrix to be factored.
	On exit, the factors L and U from the factorization a = P*L*U;
	the unit diagonal elements of L are not stored.
	
	lda (input) integer
	The leading dimension of the array A.
	In almost all cases, it is for compatibility.
	
	ipiv (output) interger array, dimension (min(m, n))
	The pivot indices;
	for 0 <= i < min(M,N), row i of the matrix was interchanged with row ipiv[i].
	
	info (output) integer array, dimension (1)
	info[0]
	= 0:	successful exit
	< 0:	if info = -i, the i-th argument had an illegal value
	> 0:	if info = i, U(i,i) is exactly zero.
			The factorization has been completed,
			but the factor U is exactly singular,
			and division by zero will occur
			if it is used to solve a system of equations.
	
	External Subroutines
	====================
	
	dgemm, dgetf2, dlaswp, dtrsm, xerbla, ilaenv
	"""
	
	one = 1.0e+0
	
	### Test the input parameters.
	info[0] = 0
	if m < 0:
		info[0] = -1
	elif n < 0:
		info[0] = -2
	if info[0] != 0:
		xerbla('dgetrf', [-info[0]])
		return
	
	### Quick return if possible
	if (m == 0) or (n == 0):
		return
	
	### Determine the block size for this environment.
	nb = ilaenv(1, 'dgetrf', ' ', m, n, -1, -1)
	if (nb <= 1) or (nb >= min(m, n)):
		### Use unblocked code.
		dgetf2(m, n, a, lda, ipiv, info)
	else:
		### Use blocked code.
		for j in range(1, min(m, n), nb):
			jb = min(min(m, n) - j + 1, nb)
			
			### Factor diagonal and subdiagonal blocks and test for exact singularity.
			iinfo = [0]
			dgetf2(m - j + 1, jb, a[j - 1:, j - 1:], lda, ipiv[j - 1:], iinfo)
			
			### Adjust INFO and the pivot indices.
			if (info[0] == 0) and (iinfo[0] > 0):
				info[0] = iinfo[0] + j - 1
			for i in range(j, min(m, j + jb - 1)):
				ipiv[i - 1] += j - 1
			
			### Apply interchanges to columns 1:J-1.
			dlaswp(j - 1, a, lda, j, j + jb - 1, ipiv, 1)
			
			if j + jb <= n:
				### Apply interchanges to columns J+JB:N.
				dlaswp(n - j - jb + 1, a[j + jb - 1:, 0:], lda, j, j + jb - 1, ipiv, 1)
				
				### Compute block row of U.
				dtrsm('Left'[0], 'Lower'[0], 'No transpose'[0], 'Unit'[0], jb, n - j - jb + 1, one, a[j - 1:, j - 1:], lda, a[j + jb - 1:, j - 1], lda)
				if j + jb <= m:
					### Update trailing submatrix.
					dgemm('No transpose'[0], 'No transpose'[0], m - j - jb + 1, n - j - jb + 1, jb, -one, a[j - 1:, j + jb - 1:], lda, a[j + jb - 1:, j - 1:], lda, one, a[j + jb - 1:, j + jb - 1:], lda)
		return
