import os
import sys
from Core.REPL import *

def main(args = sys.argv[1:]):
	'''
	repl = REPL()
	repl.InitializeBuffer()
	Dispose()
	'''
	
	try:
		if '-w' in args:
			Welcome()
		repl = REPL()
		repl.InitializeBuffer()
	finally:
		Dispose()

def Dispose():
	os._exit(0)
	sys.exit()

def Welcome():
	os.system('cls' if os.name == 'nt' else 'clear')
	print("\n")
	welcome = open("ascii.txt", "r")
	for linha in welcome:
		print(linha, end = "")
	print("\n")
	welcome.close()

if __name__ == "__main__":
    main()