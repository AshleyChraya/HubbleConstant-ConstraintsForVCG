from paida.paida_core.PAbsorber import *
from paida.math.pylapack.pyblas.idamax import idamax
from paida.math.pylapack.pyblas.dger import dger
from paida.math.pylapack.pyblas.dscal import dscal
from paida.math.pylapack.pyblas.dswap import dswap
from paida.math.pylapack.pyblas.xerbla import xerbla

def dgetf2(m, n, a, lda, ipiv, info):
	"""LAPACK routine (version 3.0)
	Univ. of Tennessee, Univ. of California Berkeley, NAG Ltd.,
	Courant Institute, Argonne National Lab, and Rice University
	June 30, 1992
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	dgetf2 computes an LU factorization of a general m-by-n matrix A
	using partial pivoting with row interchanges.
	
	The factorization has the form
		A = P * L * U
	where P is a permutation matrix,
	L is lower triangular with unit diagonal elements (lower trapezoidal if m > n),
	and U is upper triangular (upper trapezoidal if m < n).
	
	This is the right-looking Level 2 BLAS version of the algorithm.
	
	Arguments
	=========
	
	m (input) integer
	The number of rows of the matrix A. M >= 0.
	
	n (input) integer
	The number of columns of the matrix A. N >= 0.
	
	a (input/output) double array, dimension at least (m, n)
	On entry, the m by n matrix to be factored.
	On exit, the factors L and U from the factorization A = P*L*U;
	the unit diagonal elements of L are not stored.
	
	lda (input) leading dimension.
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
	
	idamax, dger, dscal, dswap, xerbla
	"""
	
	one = 1.0e+0
	zero = 0.0e+0
	
	### Test the input parameters.
	info[0] = 0
	if m < 0:
		info[0] = -1
	elif n < 0:
		info[0] = -2
	if info[0] != 0:
		xerbla('dgetf2', [-info[0]])
		return
	
	### Quick return if possible
	if (m == 0) or (n == 0):
		return
	
	for j in range(1, min(m, n) + 1):
		### Find pivot and test for singularity.
		jp = j - 1 + idamax(m - j + 1, a[j - 1, j - 1:], 1)
		ipiv[j - 1] = jp
		if a[j - 1, jp - 1] != zero:
			### Apply the interchange to columns 1:N.
			if jp != j:
				dswap(n, a[0:, j - 1], 1, a[0:, jp - 1], 1)
			
			### Compute elements J+1:M of J-th column.
			if j < m:
				dscal(m - j, one / a[j - 1, j - 1], a[j - 1, j:], 1)
		
		elif info[0] == 0:
			info[0] = j
		
		if j < min(m, n):
			### Update trailing submatrix.
			dger(m - j, n - j, -one, a[j - 1, j:], 1, a[j:, j - 1], 1, a[j:, j:], 1)
	return