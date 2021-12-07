from paida.paida_core.PAbsorber import *
from paida.paida_core.IBrushStyle import *

class ITextStyle(IBrushStyle):

	def __init__(self):
		IBrushStyle.__init__(self)
		self._setType('font', fontParameter())
		self._setType('fontSize', floatParameter(12.0))
		self._setType('bold', booleanParameter(False))
		self._setType('italic', booleanParameter(False))
		self._setType('underlined', booleanParameter(False))

	def availableFonts(self):
		return self.availableParameterOptions('font')

	def fontSize(self):
		return self._parameterData('fontSize')
		
	def setFontSize(self, fontSize):
		return self.setParameter('fontSize', fontSize)

	def font(self):
		return self._parameterData('font')

	def setFont(self, font):
		return self.setParameter('font', font)

	def isBold(self):
		return self._parameterData('bold')

	def isItalic(self):
		return self._parameterData('italic')
		
	def isUnderlined(self):
		return self._parameterData('underlined')

	def setBold(self, boolean = None):
		if boolean == None:
			self._getType('bold').reset()
			return True
		else:
			return self.setParameter('bold', boolean)

	def setItalic(self, boolean = None):
		if boolean == None:
			self._getType('italic').reset()
			return True
		else:
			return self.setParameter('italic', boolean)

	def setUnderlined(self, boolean = None):
		if boolean == None:
			self._getType('underlined').reset()
			return True
		else:
			return self.setParameter('underlined', boolean)

	def _createCopy(self):
		style = ITextStyle()
		self._createCopyWalker(self, style)
		return style

	def _createCopyWalker(self, styleData, copyTo):
		for name in styleData.availableParameters():
			parameterType = styleData._getType(name)
			if parameterType.__class__.__name__ == 'styleParameter':
				self._createCopyWalker(parameterType.getValue(), copyTo._parameterData(name))
			else:
				result = copyTo.setParameter(name, parameterType.getValue(), styleData._getCustomized(name))
