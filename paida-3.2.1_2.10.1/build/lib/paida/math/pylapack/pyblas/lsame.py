from paida.paida_core.PAbsorber import *
def lsame(ca, cb):
	"""LAPACK auxiliary routine (version 2.0)
	Univ. of Tennessee, Univ. of California Berkeley, NAG Ltd.,
	Courant Institute, Argonne National Lab, and Rice University
	September 30, 1994
	Python replacement by K. KISHIMOTO (korry@users.sourceforge.net)
	
	Purpose
	=======
	
	lsame returns .TRUE. if CA is the same letter as CB regardless of case.
	
	Arguments
	=========
	
	ca (input) character
	ca specifies the single character to be compared.
	
	cb (input) character
	cb specifies the single character to be compared.
	"""
	
	### Test if the characters are equal
	result = (ca == cb)
	if result:
		return result
	
	### Now test for equivalence if both characters are alphabetic.
	zcode = ord('Z')
	
	### Use 'Z' rather than 'A' so that ASCII can be detected on Prime machines,
	### on which ord (originally ichar()) returns a value with bit 8 set.
	### ICHAR('A') on Prime machines returns 193 which is the same as ICHAR('A') on an EBCDIC machine.
	
	inta = ord(ca)
	intb = ord(cb)
	
	if (zcode == 90) or (zcode == 122):
		### ASCII is assumed - ZCODE is the ASCII code of either lower or upper case 'Z'.
		if (inta >= 97) and (inta <= 122):
			inta -= 32
		if (intb >= 97) and (intb <= 122):
			intb -= 32
	elif (zcode == 233) or (zcode == 169):
		### EBCDIC is assumed - ZCODE is the EBCDIC code of either lower or upper case 'Z'.
		if (129 <= inta <= 137) or (145 <= inta <= 153) or (162 <= inta <= 169):
			inta += 64
		if (129 <= intb <= 137) or (145 <= intb <= 153) or (162 <= intb <= 169):
			intb += 64
	elif (zcode == 218) or (zcode == 250):
		### ASCII is assumed, on Prime machines - ZCODE is the ASCII code plus 128 of either lower or upper case 'Z'.
		if 225 <= inta <= 250:
			inta -= 32
		if 225 <= intb <= 250:
			intb -= 32
	return (inta == intb)
