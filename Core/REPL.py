import os

from .Compiler.tokenizer import Tokenizer
from .Compiler.parser import Parser
from .MetaCommands import MetaCommands

#<summary>Read Eval Print Loop</summary>
class REPL:
	def __init__(self):
		self.__CleanCommandBuffer()
		#os.system('cls' if os.name == 'nt' else 'clear')

	def ReadCommandBuffer(self, commandBufferValue = None):
		if commandBufferValue == None:
			self.__command = str(input("ValkyrieDB>"))
		else:
			self.__command = commandBufferValue

	def __CleanCommandBuffer(self):
		self.__command = None

	def InitializeBuffer(self):
		while True:
			self.ReadCommandBuffer()
			if self.__command != "":
				if self.__command[0] == ".":
					if self.__command in MetaCommands.COMMANDS:
						MetaCommands.COMMANDS[self.__command]()
					else:
						print("Comando '{0}' não reconhecido.".format(self.__command))
						self.__CleanCommandBuffer()
						continue
				else:
					tokenizer = Tokenizer(self.__command)
					tokens = tokenizer.tokenize()
					
					for token in tokens:
						print(str(token))
					
					parser = Parser(tokens)
					parser.Execute()
