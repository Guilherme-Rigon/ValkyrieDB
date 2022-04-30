import os
import sys

COMMANDS = {
	'.ajuda': lambda: print(
		'.ajuda: Retorna a lista de comandos.\n'+
		'.versão: Exibe a versão do banco de dados.\n'+
		'.sair: Sai do modo de comandos do banco de dados.'),
	'.sair': lambda: exit(),
	'.versão': lambda: print("ValkyrieDB Versão 1.0.0")
}