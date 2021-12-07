from paida.paida_core.PAbsorber import *
def ilaenv(ispec, name, opts, n1, n2, n3, n4):
	"""LAPACK auxiliary routine (version 3.0)
	Univ. of Tennessee, Univ. of California Berkeley, NAG Ltd.,
	Courant Institute, Argonne National Lab, and Rice University
	June 30, 1999
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	ilaenv is called from the LAPACK routines to choose problem-dependent parameters for the local environment.
	See ISPEC for a description of the parameters.
	
	This version provides a set of parameters which should give good,
	but not optimal, performance on many of the currently available computers.
	Users are encouraged to modify this subroutine to set the tuning parameters
	for their particular machine using the option and problem size information in the arguments.
	
	Arguments
	=========
	
	ispec (input) integer
	Specifies the parameter to be returned as the value of ilaenv.
	= 1:	the optimal blocksize;
			if this value is 1, an unblocked algorithm will give the best performance.
	= 2:	the minimum block size for which the block routine should be used;
			if the usable block size is less than this value, an unblocked routine should be used.
	= 3:	the crossover point
			(in a block routine, for N less than this value, an unblocked routine should be used)
	= 4:	the number of shifts, used in the nonsymmetric eigenvalue routines
	= 5:	the minimum column dimension for blocking to be used;
			rectangular blocks must have dimension at least k by m, where k is given by ILAENV(2,...) and m by ILAENV(5,...)
	= 6:	the crossover point for the SVD
			(when reducing an m by n matrix to bidiagonal form, if max(m,n)/min(m,n) exceeds this value,
			a QR factorization is used first to reduce the matrix to a triangular form.)
	= 7:	the number of processors
	= 8:	the crossover point for the multishift QR and QZ methods for nonsymmetric eigenvalue problems.
	= 9:	maximum size of the subproblems at the bottom of the computation tree in the divide-and-conquer algorithm
			(used by xGELSD and xGESDD)
	=10:	ieee NaN arithmetic can be trusted not to trap
	=11:	infinity arithmetic can be trusted not to trap
	
	name (input) character
	The name of the calling subroutine. Case insensitive.
	
	opts (input) character
	The character options to the subroutine NAME, concatenated into a single character string.
	For example, UPLO = 'U', TRANS = 'T', and DIAG = 'N' for a triangular routine would be specified as OPTS = 'UTN'.
	
	n1 (input) integer
	n2 (input) integer
	n3 (input) integer
	n4 (input) integer
	Problem dimensions for the subroutine NAME; these may not all be required.
	
	Return Value
	============
	
	integer
	>= 0:	the value of the parameter specified by ISPEC
	< 0: 	if ILAENV = -k, the k-th argument had an illegal value.
	
	Further Details
	===============
	
	The following conventions have been used when calling ILAENV from the LAPACK routines:
	1) 	OPTS is a concatenation of all of the character options to subroutine NAME,
		in the same order that they appear in the argument list for NAME,
		even if they are not used in determining the value of the parameter specified by ISPEC.
	2) 	The problem dimensions N1, N2, N3, N4 are specified in the order that they appear in the argument list for NAME.
		N1 is used first, N2 second, and so on, and unused problem dimensions are passed a value of -1.
	3) 	The parameter value returned by ILAENV is checked for validity in the calling subroutine.
		For example, ILAENV is used to retrieve the optimal blocksize for STRTRI as follows:
			NB = ILAENV( 1, 'STRTRI', UPLO // DIAG, N, -1, -1, -1 )
			IF( NB.LE.1 ) NB = MAX( 1, N )
	
	External Subroutines
	====================
	
	ieeeck
	"""
	
	if ispec == 1:
		subnam = name.upper()
		c1 = subnam[0:1]
		sname = (c1 == 'S') or (c1 == 'D')
		cname = (c1 == 'C') or (c1 == 'Z')
		if not (cname or sname):
			return
		c2 = subnam[1:3]
		c3 = subnam[3:6]
		c4 = c3[1:3]
		### c1 = name[0:1]
		### In these examples, separate code is provided for setting NB for real and complex.
		### We assume that NB will take the same value in single or double precision.
		nb = 1
		
		if c2 == 'GE':
			if c3 == 'TRF':
				if sname:
					nb = 64
				else:
					nb = 64
			elif (c3 == 'QRF') or (c3 == 'RQF') or (c3 == 'LQF') or (c3 == 'QLF'):
				if sname:
					nb = 32
				else:
					nb = 32
			elif c3 == 'HRD':
				if sname:
					nb = 32
				else:
					nb = 32
			elif c3 == 'BRD':
				if sname:
					nb = 32
				else:
					nb = 32
			elif c3 == 'TRI':
				if sname:
					nb = 64
				else:
					nb = 64
			elif c2 == 'PO':
				if c3 == 'TRF':
					if sname:
						nb = 64
					else:
						nb = 64
			elif c2 == 'SY':
				if c3 == 'TRF':
					if sname:
						nb = 64
					else:
						nb = 64
				elif sname and (c3 == 'TRD'):
					nb = 32
				elif sname and (c3 == 'GST'):
					nb = 64
			elif cname and (c2 == 'HE'):
				if c3 == 'TRF':
					nb = 64
				elif c3 == 'TRD':
					nb = 32
				elif c3 == 'GST':
					nb = 64
			elif sname and (c2 == 'OR'):
				if c3[0:1] == 'G':
					if (c4 == 'QR') or (c4 == 'RQ') or (c4 == 'LQ') or (c4 == 'QL') or (c4 == 'HR') or (c4 == 'TR') or (c4 == 'BR'):
						nb = 32
				elif c3[0:1] == 'M':
					if (c4 == 'QR') or (c4 == 'RQ') or (c4 == 'LQ') or (c4 == 'QL') or (c4 == 'HR') or (c4 == 'TR') or (c4 == 'BR'):
						nb = 32
			elif cname and (c2 == 'UN'):
				if c3[0:1] == 'G':
					if (c4 == 'QR') or (c4 == 'RQ') or (c4 == 'LQ') or (c4 == 'QL') or (c4 == 'HR') or (c4 == 'TR') or (c4 == 'BR'):
						nb = 32
				elif c3[0:1] == 'M':
					if (c4 == 'QR') or (c4 == 'RQ') or (c4 == 'LQ') or (c4 == 'QL') or (c4 == 'HR') or (c4 == 'TR') or (c4 == 'BR'):
						nb = 32
			elif c2 == 'GB':
				if c3 == 'TRF':
					if sname:
						if n4 <= 64:
							nb = 1
						else:
							nb = 32
					else:
						if n4 <= 64:
							nb = 1
						else:
							nb = 32
			elif c2 == 'PB':
				if c3 == 'TRF':
					if sname:
						if n2 <= 64:
							nb = 1
						else:
							nb = 32
					else:
						if n2 <= 64:
							nb = 1
						else:
							nb = 32
			elif c2 == 'TR':
				if c3 == 'TRI':
					if sname:
						nb = 64
					else:
						nb = 64
			elif c2 == 'LA':
				if c3 == 'UUM':
					if sname:
						nb = 64
					else:
						nb = 64
			elif sname and (c2 == 'ST'):
				if c3 == 'EBZ':
					nb = 1
			return nb
	
	elif ispec == 2:
		subnam = name.upper()
		c1 = subnam[0:1]
		sname = (c1 == 'S') or (c1 == 'D')
		cname = (c1 == 'C') or (c1 == 'Z')
		if not (cname or sname):
			return
		c2 = subnam[1:3]
		c3 = subnam[3:6]
		c4 = c3[1:3]
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	elif ispec == 3:
		subnam = name.upper()
		c1 = subnam[0:1]
		sname = (c1 == 'S') or (c1 == 'D')
		cname = (c1 == 'C') or (c1 == 'Z')
		if not (cname or sname):
			return
		c2 = subnam[1:3]
		c3 = subnam[3:6]
		c4 = c3[1:3]
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	elif ispec == 4:
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	elif ispec == 5:
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	elif ispec == 6:
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	elif ispec == 7:
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	elif ispec == 8:
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	elif ispec == 9:
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	elif ispec == 10:
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	elif ispec == 11:
		error = 'ilaenv(ispec = %d) is not implemented yet.' % ispec
		print error
		raise error
	else:
		return -1
