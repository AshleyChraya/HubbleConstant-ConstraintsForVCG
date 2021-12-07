from paida.paida_core.PAbsorber import *
from paida.math.pylapack.dgetrf import dgetrf
from paida.math.pylapack.dgetrs import dgetrs
from paida.math.pylapack.pyblas.xerbla import xerbla

def dgesv(n, nrhs, a, lda, ipiv, b, ldb, info):
	"""LAPACK driver routine (version 3.0)
	Univ. of Tennessee, Univ. of California Berkeley, NAG Ltd.,
	Courant Institute, Argonne National Lab, and Rice University
	March 31, 1993
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	dgesv computes the solution to a real system of linear equations
		A * X = B,
	where A is an N-by-N matrix and X and B are N-by-NRHS matrices.
	
	The LU decomposition with partial pivoting and row interchanges is used to factor A as
		A = P * L * U,
	where P is a permutation matrix, L is unit lower triangular, and U is upper triangular.
	The factored form of A is then used to solve the system of equations A * X = B.
	
	Arguments
	=========
	
	n (input) integer
	The number of linear equations, i.e., the order of the matrix a. n >= 0.
	
	nrhs (input) integer
	The number of right hand sides, i.e., the number of columns of the matrix b. nrhs >= 0.
	
	a (input/output) double array, dimension at least (nrhs, n)
	On entry, the n-by-n coefficient matrix a.
	On exit, the factors L and U from the factorization a = P*L*U;
	the unit diagonal elements of L are not stored.
	
	lda (input) integer array, dimension (2)
	This represents the starting indices of a.
	
	ipiv (output) interger array, dimension (n)
	The pivot indices that define the permutation matrix P;
	row i of the matrix was interchanged with row ipiv[i].
	
	b (input/output) double array, dimension at least (n, nrhs)
	On entry, the n-by-nrhs matrix of right hand side matrix b.
	On exit, if no error, the n-by-nrhs solution matrix X.
	
	ldb (input) integer array, dimension (2)
	This represents the starting indices of b.
	
	info (output) integer array, dimension (1)
	info[0]
	= 0:	successful exit
	< 0:	if info = -i, the i-th argument had an illegal value
	> 0:	if info = i, U(i,i) is exactly zero.
			The factorization has been completed,
			but the factor U is exactly singular,
			so the solution could not be computed.
	
	External Subroutines
	====================
	
	dgetrf, dgetrs, xerbla
	"""
	
	### Test the input parameters.
	info[0] = 0
	if n < 0:
		info[0] = -1
	elif nrhs < 0:
		info[0] = -2
	if info[0] != 0:
		xerbla('dgesv', [-info[0]])
		return
	
	### Compute the LU factorization of A.
	dgetrf(n, n, a, lda, ipiv, info)
	if info[0] == 0:
		### Solve the system A*X = B, overwriting B with X.
		dgetrs('No transpose'[0], n, nrhs, a, lda, ipiv, b, ldb, info)
