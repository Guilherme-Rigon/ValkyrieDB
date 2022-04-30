import os
import sys
import Core.Compiler.keywords as Keywords
import Core.Compiler.consts as Consts
from .token import Token

#<summary>Tokenizer ou Lexer do Compilador SQL</summary>
class Tokenizer:
	def __init__(self, text):
		self.text = text
		#self.__current_char = text[0] if text != None else None
		self.idx = 0
		self.ln = 0
		self.col = 0
		self.tokens = []

	def advance(self) -> bool:
		breakLine = False
		current_char = self.__getCurrentChar()
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.col = 0
			self.ln += 1
			breakLine = True
		return breakLine

	def __getCurrentChar(self, nCaracteres = 0):
		if self.idx + nCaracteres < len(self.text):
			return self.text[self.idx + nCaracteres]
		else:
			return None

	def __endOfFile(self) -> bool:
		return self.__getCurrentChar() == None

	def __addToken(self, token: Token):
		self.tokens.append(token)

	def __getToken(self) -> Token:
		value = ""
		pos = CharPosition(self.idx, self.ln, self.col)

		while not self.__endOfFile() and self.__getCurrentChar() in Consts.caracteres + Consts.numeric_values:
			value += self.__getCurrentChar()
			self.advance()
		value = value.upper()

		if value in Keywords.ALL:
			keyword = Keywords.GetKeyword(value)
			return Token(keyword, pos)
		
		return Token("id", pos, value)

	def __getString(self) -> Token:
		value = ""
		pos = CharPosition(self.idx, self.ln, self.col)

		self.advance()
		while not self.__endOfFile() and self.__getCurrentChar() in Consts.text_values + Consts.numeric_values and self.__getCurrentChar() != "'":
			value += self.__getCurrentChar()
			self.advance()
			
		if self.__getCurrentChar() == "'":
			self.advance()
		return Token("String", pos, value)

	def __getVariable(self):
		value = ""
		pos = CharPosition(self.idx, self.ln, self.col)
		
		if  self.__getCurrentChar() == "@":
			self.advance()
		while not self.__endOfFile() and self.__getCurrentChar() in Consts.caracteres and self.__getCurrentChar() != " ":
			value += self.__getCurrentChar()
			self.advance()
		value = value.upper()
		return Token("Variable", pos, value)

	def __getNumber(self):
		value = ""
		pos = CharPosition(self.idx, self.ln, self.col)

		while not self.__endOfFile() and self.__getCurrentChar() in Consts.numeric_values:
			value += self.__getCurrentChar()
			self.advance()
		value = value.upper()
		return Token("Number", pos, value)

	def __getLogicalOperator(self):
		value = ""
		pos = CharPosition(self.idx, self.ln, self.col)

		while not self.__endOfFile() and self.__getCurrentChar() in Consts.relational_operators:
			value += self.__getCurrentChar()
			self.advance()
		value = value.upper()
		return Token(value, pos, value)

	def __getLogicalOperation(self):
		value = ""
		pos = CharPosition(self.idx, self.ln, self.col)

		while not self.__endOfFile() and self.__getCurrentChar in Consts.logical_operations:
			value += self.__getCurrentChar()
			self.advance()
		value = value.upper()
		return Token(value, pos, value)

	def tokenize(self) -> list:
		while not self.__endOfFile():
			current_char = self.__getCurrentChar()
			if current_char in ' \t':
				self.advance()	
			elif current_char in Consts.caracteres:
				self.__addToken(self.__getToken())
			elif current_char in Consts.numeric_values:
				self.__addToken(self.__getNumber())
			elif current_char in Consts.relational_operators:
				self.__addToken(self.__getLogicalOperator())
			elif current_char in Keywords.LOGICAL_OPERATIONS:
				self.__addToken(self.__getLogicalOperation())
			elif current_char == "'":
				self.__addToken(self.__getString())
			elif current_char == "@":
				self.__addToken(self.__getVariable())
			elif current_char == ";":
				self.__addToken(Token("EOC", CharPosition(self.idx, self.ln, self.col), ";"))
				self.advance()
			elif current_char == ",":
				self.__addToken(Token('Separator', CharPosition(self.idx, self.ln, self.col), ','))
				self.advance()
			elif current_char in "()":
				self.__addToken(Token(current_char, CharPosition(self.idx, self.ln, self.col), current_char))
				self.advance()
			else:
				self.advance()

		self.__addToken(Token("EOF", CharPosition(self.idx, self.ln, self.col)))
		return self.tokens

class CharPosition:
	def __init__(self, idx, ln, col):
		self.idx = idx
		self.ln = ln
		self.col = col

	def __str__(self):
		return f"Linha: {self.ln}, Coluna: {self.col}"