from paida.paida_core.PAbsorber import *
from paida.math.pylapack.dlaswp import dlaswp
from paida.math.pylapack.pyblas.dgemm import lsame
from paida.math.pylapack.pyblas.dtrsm import dtrsm
from paida.math.pylapack.pyblas.xerbla import xerbla

def dgetrs(trans, n, nrhs, a, lda, ipiv, b, ldb, info):
	"""LAPACK routine (version 3.0)
	Univ. of Tennessee, Univ. of California Berkeley, NAG Ltd.,
	Courant Institute, Argonne National Lab, and Rice University
	March 31, 1993
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	dgetrs solves a system of linear equations
		A * X = B  or  A' * X = B
	with a general N-by-N matrix A using the LU factorization computed by dgetrf.
	
	Arguments
	=========
	
	trans (input) character
	Specifies the form of the system of equations:
	= 'N':  A * X = B  (No transpose)
	= 'T':  A'* X = B  (Transpose)
	= 'C':  A'* X = B  (Conjugate transpose = Transpose)
	
	n (input) integer
	The order of the matrix A.  N >= 0.
	
	nrhs (input) integer
	The number of right hand sides, i.e., the number of columns of the matrix B. nrhs >= 0.
	
	a (input) double array, dimension (lda, n)
	The factors L and U from the factorization A = P*L*U as computed by DGETRF.
	
	lda (input) integer
	The leading dimension of the array A.
	In almost all cases, it is for compatibility.
	
	ipiv (input) integer array, dimension (n)
	The pivot indices from DGETRF; for 1<=i<=N, row i of the matrix was interchanged with row IPIV(i).
	
	b (input/output) double array, dimension (ldb, nrhs)
	On entry, the right hand side matrix B.
	On exit, the solution matrix X.
	
	ldb (input) integer
	The leading dimension of the array B.
	In almost all cases, it is for compatibility.
	
	info (output) integer
	= 0:  successful exit
	< 0:  if INFO = -i, the i-th argument had an illegal value
	
	External Subroutines
	====================
	
	lsame, dlaswp, dtrsm, xerbla
	"""
	
	one = 1.0e+0
	
	### Test the input parameters.
	info[0] = 0
	notran = lsame(trans, 'N')
	if (not notran) and (not lsame(trans, 'T')) and (not lsame(trans, 'C')):
		info[0] = -1
	elif n < 0:
		info[0] = -2
	elif nrhs < 0:
		info[0] = -3
	if info[0] != 0:
		xerbla('DGETRS', [-info[0]])
		return
	
	### Quick return if possible
	if (n == 0) or (nrhs == 0):
		return
	
	if notran:
		### Solve A * X = B.
		### Apply row interchanges to the right hand sides.
		dlaswp(nrhs, b, ldb, 1, n, ipiv, 1)
		
		### Solve L*X = B, overwriting B with X.
		dtrsm('Left'[0], 'Lower'[0], 'No transpose'[0], 'Unit'[0], n, nrhs, one, a, lda, b, ldb)
		
		### Solve U*X = B, overwriting B with X.
		dtrsm('Left'[0], 'Upper'[0], 'No transpose'[0], 'Non-unit'[0], n, nrhs, one, a, lda, b, ldb)
	else:
		### Solve A' * X = B.
		### Solve U'*X = B, overwriting B with X.
		dtrsm('Left'[0], 'Upper'[0], 'Transpose'[0], 'Non-unit'[0], n, nrhs, one, a, lda, b, ldb)
		
		### Solve L'*X = B, overwriting B with X.
		dtrsm('Left'[0], 'Lower'[0], 'Transpose'[0], 'Unit'[0], n, nrhs, one, a, lda, b, ldb)
		
		### Apply row interchanges to the solution vectors.
		dlaswp(nrhs, b, ldb, 1, n, ipiv, -1)
	return
