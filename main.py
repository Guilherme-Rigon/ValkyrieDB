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
		input = None
		if '-w' in args:
			Welcome()
		repl = REPL()
		if '-path' in args:
			path = args[args.index('-path') + 1]
			if path.endswith('.psql'):
				archive = open(path, 'r')
				repl.ExecuteBufferFile(archive)
				archive.close()
			else:
				print('A extensão informada não é surpotada pelo sistema!')
		else:
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