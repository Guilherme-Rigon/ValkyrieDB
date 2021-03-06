from lib2to3.pgen2 import token
import sqlite3
import traceback
import sys
import os
from matplotlib.pyplot import isinteractive

from pyparsing import Keyword
import Core.Compiler.keywords as Keywords
import Core.Compiler.consts as Consts
from tabulate import tabulate
from .token import Token

class Parser:
    def __init__(self, tokenList):
        self.tokens = tokenList
        self.__hasErros = False

    def __ExecuteInSQLite(self, commandList, db = "master"):
        try:
            con = sqlite3.connect(f"{os.path.dirname(os.path.realpath(__file__))}\..\..\Data\{db}.db")
            cursor = con.cursor()

            for command in commandList:
                cursor.execute(command)
                if "SELECT" in command:
                    columNames = [''] + list(map(lambda x: x[0], cursor.description))
                    rows = cursor.fetchall()
                    table = [columNames]
                    row_number = 1
                    for row in rows:
                        table.append((row_number,) + row)
                        row_number += 1
                    print("")
                    print(tabulate(table, headers='firstrow', tablefmt='grid'))
                    print("")
                elif cursor.rowcount == -1:
                    print("Comando executado com sucesso!")
                else:
                    print(f"Linhas afetadas: {cursor.rowcount}")
            print()
            con.commit()
            con.close()
        except sqlite3.Error as er:
            print('[Erro do SQLite]: %s' % (' '.join(er.args)))
            '''
            print("[Classe de Exceção]: ", er.__class__)
            print('[SQLite Traceback]: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
            '''

    def Execute(self):
        commandList = []
        command = ""
        i = 0
        while i < len(self.tokens) and not self.__hasErros:
            if self.tokens[i].getType() == Keywords.SELECIONE:
                (command, i) = self.__select(self.tokens, i)
                if command == '':
                    break
                commandList.append(command)
                command = ""
            elif self.tokens[i].getType() == Keywords.INSIRA:
                (command, i) = self.__insert(self.tokens, i)
                if command == '':
                    break
                commandList.append(command)
                command = ""
            elif self.tokens[i].getType() == Keywords.ATUALIZE:
                (command, i) = self.__update(self.tokens, i)
                if command == '':
                    break
                commandList.append(command)
                command = ""
            elif self.tokens[i].getType() == Keywords.DELETE:
                (command, i) = self.__delete(self.tokens, i)
                if command == '':
                    break
                commandList.append(command)
                command = ""
            elif self.tokens[i].getType() == Keywords.CRIE:
                (command, i) = self.__create(self.tokens, i)
                if command == '':
                    break
                commandList.append(command)
                command = ""
            elif self.tokens[i].getType() == Keywords.ALTERE:
                (command, i) = self.__alter(self.tokens, i)
                if command == '':
                    break
                commandList.append(command)
                command = ""
            elif self.tokens[i].getType() == Keywords.EXCLUA:
                (command, i) = self.__drop(self.tokens, i)
                if command == '':
                    break
                commandList.append(command)
                command = ""
            elif self.tokens[i].getType() == "EOC":
                pass
            elif self.tokens[i].getType() != "EOF":
                thk = self.tokens[i]
                value = thk.getValue() if thk.getValue() != None else thk.getType()
                self.__showMessageError(f"[PSQL#01] Token `{Keywords.GetPSQL(value)}` não esperado próximo a {thk.getPosition()}")
                break

            i += 1
            #print(commandList)
        if len(commandList) > 0 and not self.__hasErros:
            self.__ExecuteInSQLite(commandList)

    def __select(self, tokens, index = 0): # Implementar a analise do WHERE e TESTAR COM DOIS COMANDOS
        KeywordId = Keywords.SELECIONE
        vSELECT = False
        vFROM = False
        vWHERE = False
        HasWhere = False
        i = 0
        command = ""
        if tokens[index].getType() == Keywords.SELECIONE:
            while i < len(tokens):
                if tokens[i].getType() == Keywords.ONDE:
                    HasWhere = True
                    KeywordId = Keywords.ONDE

                if tokens[i].getType() in ('id', Keywords.TUDO) and KeywordId == Keywords.SELECIONE:
                    vSELECT, i = self.__getIdentificators(tokens, i, ('id', Keywords.TUDO))
                    KeywordId = Keywords.DE
                elif vSELECT and KeywordId == Keywords.DE and tokens[i].getType() == 'id':
                    vFROM, i = self.__getIdentificators(tokens, i)
                elif vFROM and HasWhere and KeywordId == Keywords.ONDE and tokens[i].getType() in ('id', 'String', 'Number', 'Variable') and not vWHERE:
                    vWHERE, i = self.__verifyWhereKeyword(tokens, i)
                    if not vWHERE:
                        break

                if tokens[i].getType() != "EOF":
                    command += f"{self.__writeToken(tokens[i])} "

                i += 1

        #print(f"S: {vSELECT}, F: {vFROM}, W: {vWHERE}")
        if vSELECT and vFROM:
            if HasWhere and not vWHERE:
                command = ''
            else:
                command = command.strip()
            return (command, i)
        else:
            self.__showMessageError(f"[PSQL#08] Comando não pode ser executado pelo sistema, por favor verifique a sintaxe antes de executar novamente.")
            return ('', i)

    def __insert(self, tokens, index = 0):
        iSintaxe = 1
        sintaxe = {
            1 : Keywords.INSIRA,
            2 : Keywords.EM,
            3 : "id",
            4 : Keywords.VALORES,
            5 : "(",
            6 : ('id', 'Number', 'String', 'Separator'),
            7 : ")"
        }
        i = index
        ids = []
        dataStatus = None
        command = ""
        if tokens[index].getType() == Keywords.INSIRA:
            while i < len(tokens):
                if iSintaxe == 6:
                    if dataStatus == None:
                        dataStatus, i = self.__getIdentificators(tokens, i, ('id', 'Number', 'String'))
                        if not dataStatus:
                            thk = tokens[i]
                            command = None
                            self.__showMessageError(f'[PSQL#11] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                            break
                    elif tokens[i].getType() not in sintaxe[iSintaxe]:
                        iSintaxe += 1
                elif iSintaxe > 6:
                    pass
                elif tokens[i].getType() == sintaxe[iSintaxe]:
                    ids.append(tokens[i])
                    iSintaxe += 1
                else:
                    thk = tokens[i]
                    command = None
                    self.__showMessageError(f'[PSQL#10] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                    break

                if tokens[i].getType() != "EOF":
                    command += f"{self.__writeToken(tokens[i])} "
                i += 1

        if command != None:
            return (command, i)
        else:
            return ('', index)

    def __update(self, tokens, index = 0):
        iSintaxe = 1
        sintaxe = {
            1 : Keywords.ATUALIZE,
            2 : "id",
            3 : Keywords.DEFINA,
            4 : "id",
            5 : Keywords.ONDE
        }
        i = index
        ids = []
        setStatus = False
        whereStatus = False
        command = ""

        if tokens[index].getType() == Keywords.ATUALIZE:
            while i < len(tokens) and not self.__hasErros:
                if iSintaxe == 4 and not setStatus:
                    (setStatus, i, commandReturned) = self.__searchTokenPattern(tokens, i, ('id', '=', 'External'))
                    if not setStatus:
                        break
                    command = f"{command.strip()} {commandReturned}"
                    iSintaxe += 1
                elif iSintaxe == 5 and not whereStatus:
                    (whereStatus, i) = self.__verifyWhereKeyword(tokens, i)
                    if not whereStatus:
                        break
                    iSintaxe += 1
                elif iSintaxe > 5:
                    pass
                elif tokens[i].getType() == sintaxe[iSintaxe]:
                    ids.append(tokens[i])
                    iSintaxe += 1
                else:
                    thk = tokens[i]
                    command = None
                    self.__showMessageError(f'[PSQL#12] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                    break

                if tokens[i].getType() != "EOF":
                    command += f"{self.__writeToken(tokens[i])} "
                i += 1
        
        if command != None and setStatus and ((whereStatus and Keywords.WHERE in command) or not whereStatus):
            return (command, i)
        else:
            return ('', index)

    def __delete(self, tokens, index = 0):
        iSintaxe = 1
        sintaxe = {
            1 : Keywords.DELETE,
            2 : Keywords.DE,
            3 : "id",
            4 : Keywords.ONDE
        }
        i = index
        ids = []
        whereStatus = False
        command = ""
        
        if tokens[index].getType() == Keywords.DELETE:
            while i < len(tokens) and not self.__hasErros:
                if iSintaxe == 5 and not whereStatus and tokens[i].getType() in ('id', 'String', 'Number', 'Variable') :
                    (whereStatus, i) = self.__verifyWhereKeyword(tokens, i)
                    if not whereStatus:
                        break
                    iSintaxe += 1
                elif iSintaxe > 5:
                    pass
                elif tokens[i].getType() == sintaxe[iSintaxe]:
                    ids.append(tokens[i])
                    iSintaxe += 1
                else:
                    thk = tokens[i]
                    command = None
                    self.__showMessageError(f'[PSQL#14] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                    break

                if tokens[i].getType() != "EOF":
                    command += f"{self.__writeToken(tokens[i])} "
                i += 1

            if not self.__hasErros and whereStatus:
                return (command, i)
            else:
                return ('', index)

    def __create(self, tokens, index = 0):
        iSintaxe = 0
        sintaxe = {
            1 : Keywords.CRIE,
            2 : Keywords.TABELA,
            3 : "id",
            4 : "(",
            5 : "id",
            6 : Keywords.PSQLDATATYPES,
            7 : Keywords.IDENTIFICADOR,
            8 : Keywords.CHAVE,
            9 : "Separator",
            10 : ")"
        }
        i = index
        ids = []
        command = ""
        fkStatus = None
        if tokens[i].getType() == Keywords.CRIE:
            while i < len(tokens) and not self.__hasErros and iSintaxe < 10 and tokens[i].getType() not in ("EOC", "EOF"):
                iSintaxe += 1
                if iSintaxe == 7 and tokens[i].getType() == sintaxe[iSintaxe]:
                    if tokens[i + 1].getType() == sintaxe[iSintaxe + 1]:
                        ids.append(tokens[i])
                        ids.append(tokens[i + 1])
                        command += f"{self.__writeToken(tokens[i])} "
                        i += 1
                        iSintaxe += 1
                    else:
                        thk = tokens[i]
                        self.__showMessageError(f'[PSQL#16] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                elif iSintaxe == 7:
                    iSintaxe = 9

                if iSintaxe == 6 and tokens[i].getType() in sintaxe[iSintaxe]:
                    ids.append(tokens[i])
                elif iSintaxe == 9 and tokens[i].getType() == sintaxe[iSintaxe]:
                    iSintaxe = 4
                elif iSintaxe == 9:
                    iSintaxe += 1
                elif iSintaxe == 5 and tokens[i].getType() == Keywords.CHAVE:
                    fkStatus, partialCommand, i = self.__retriveForeignKeyKeyword(tokens, i)
                    command += partialCommand
                elif tokens[i].getType() == sintaxe[iSintaxe]:
                    ids.append(tokens[i])
                else:
                    thk = tokens[i]
                    self.__showMessageError(f'[PSQL#17] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')

                if tokens[i].getType() != "EOF":
                    command += f"{self.__writeToken(tokens[i])} "
                i += 1
        if not self.__hasErros and (fkStatus or fkStatus == None):
            return (command, i)
        else:
            return ('', index)

    def __alter(self, tokens, index = 0):
        iSintaxe = 0
        sintaxe = {
            1 : Keywords.ALTERE,
            2 : Keywords.TABELA,
            3 : "id",
            4 : (Keywords.ADICIONE, Keywords.RENOMEIE),
            5 : "id",
            6 : Keywords.PSQLDATATYPES,
            7 : Keywords.PARA,
            8 : "id"
        }
        i = index
        ids = []
        command = ""
        addStatus = None
        toStatus = None
        if tokens[i].getType() == Keywords.ALTERE:
            while i < len(tokens) and not self.__hasErros and iSintaxe < 8:
                iSintaxe += 1
                if iSintaxe == 5:
                    if sintaxe[4] == Keywords.ADICIONE:
                        addStatus = self.__retriveAddKeywordContent(tokens, i)
                    elif sintaxe[4] == Keywords.RENOMEIE:
                        toStatus = self.__retriveTOKeyword(tokens, i)
                    else:
                        thk = tokens[i]
                        self.__showMessageError(f'[PSQL#19] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                elif iSintaxe == 4 and tokens[i].getType() in sintaxe[iSintaxe]:
                    ids.append(tokens[i])
                    sintaxe[iSintaxe] = tokens[i].getType()
                elif tokens[i].getType() == sintaxe[iSintaxe] or addStatus or toStatus:
                    ids.append(tokens[i])
                else:
                    thk = tokens[i]
                    self.__showMessageError(f'[PSQL#18] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                if tokens[i].getType() != "EOF":
                    command += f"{self.__writeToken(tokens[i])} "
                i += 1

        if not self.__hasErros and (toStatus or addStatus):
            return (command, i)
        else:
            return ('', index)

    def __drop(self, tokens, index = 0):
        iSintaxe = 0
        sintaxe = {
            1 : Keywords.EXCLUA,
            2 : Keywords.TABELA,
            3 : "id"
        }
        i = index
        command = ""
        if tokens[i].getType() == Keywords.EXCLUA:
            while i < len(tokens) and not self.__hasErros and iSintaxe < 3:
                iSintaxe += 1
                if tokens[i].getType() != sintaxe[iSintaxe]:
                    thk = tokens[i]
                    self.__showMessageError(f'[PSQL#22] Token `{Keywords.GetPSQL(thk.getValue())}` '
                    + f'não esperado próximo a {thk.getPosition()}')
                if tokens[i].getType() != "EOF":
                    command += f"{self.__writeToken(tokens[i])} "
                i += 1
        if not self.__hasErros:
            return (command, i)
        else:
            return ('', index)

    def __getIdentificators(self, tokens, index = 0, searchedIds = ('id',)):
        separator = True
        i = index
        ids = []
        if tokens[index].getType() in searchedIds:
            separator = False
        else:
            thk = tokens[i]
            self.__showMessageError(f'[PSQL#02] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')

        while tokens[i].getType() in searchedIds + ('Separator',):
            if separator and tokens[i].getType() == 'Separator':
                ids.append(tokens[i])
                i += 1
                separator = False
            elif not separator and tokens[i].getType() in searchedIds:
                ids.append(tokens[i])
                i += 1
                separator = True
            else:
                thk = tokens[i]
                self.__showMessageError(f'[PSQL#03] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                return (False, index)

        if len(ids) > 0 and ids[-1].getType() in searchedIds:
            return (True, index)
        else:
            thk = ids[-1]
            self.__showMessageError(f'[PSQL#04] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
            return (False, index)

    def __verifyWhereKeyword(self, tokens, index = 0):
        i = index
        searchedTokens = ('id', 'String', 'Number')
        ids = []
        count = 1
        sintaxe = {
            1 : searchedTokens,
            2 : Consts.relational_operators,
            3 : searchedTokens,
            4 : Keywords.PSQL_LOGICAL_OPERATIONS
        }

        if tokens[index].getType() not in searchedTokens:
            thk = tokens[index]
            self.__showMessageError(f'[PSQL#05] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
            return (False, i)

        #while tokens[i].getType() in searchedTokens + tuple(Consts.relational_operators) + tuple(Keywords.LOGICAL_OPERATIONS):
        while i < len(tokens) and tokens[i].getType() not in ('EOC', 'EOF'):
            if count == 4:
                count = 0
                if tokens[i].getType() in Keywords.PSQL_LOGICAL_OPERATIONS:
                    ids.append(tokens[i])
                #elif tokens[i].getType() in searchedTokens + tuple(Keywords.LOGICAL_OPERATIONS) + tuple(Consts.relational_operators):
                else:
                    thk = tokens[i]
                    self.__showMessageError(f'[PSQL#09] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                    return (False, index)
            elif tokens[i].getType() in sintaxe[count]:
                ids.append(tokens[i])
            else:
                thk = tokens[i]
                self.__showMessageError(f'[PSQL#06] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                return (False, index)

            count += 1
            i += 1
        
        if len(ids) > 0 and ids[-1].getType() in searchedTokens:
            return (True, index)
        else:
            thk = ids[-1]
            self.__showMessageError(f'[PSQL#07] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
            return (False, index)

    def __searchTokenPattern(self, tokens, index, pattern, externalValues = ('String', 'Number', 'id'), searchedTokens = ('id', 'String', 'Number', '=')):
        i = index
        iPattern = 0
        ids = []
        command = ""
        while i < len(tokens) and tokens[i].getType() in searchedTokens + ('Separator',):
            if iPattern < len(pattern) and tokens[i].getType() == pattern[iPattern]:
                ids.append(tokens[i])
                iPattern += 1
            elif iPattern < len(pattern) and tokens[i].getType() in externalValues and pattern[iPattern] == 'External':
                ids.append(tokens[i])
                iPattern += 1
            elif tokens[i].getType() == "Separator":
                ids.append(tokens[i])
                iPattern = 0
            else:
                thk = tokens[i]
                self.__showMessageError(f'[PSQL#13] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                return (False, index, '')

            command += f"{self.__writeToken(tokens[i])} "
            i+=1

        if ids[-1].getType() in searchedTokens:
            return (True, i, command)
        else:
            thk = ids[-1]
            self.__showMessageError(f'[PSQL#15] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
            return (False, index, '')

    def __retriveAddKeywordContent(self, tokens, index):
        i = index
        iSintaxe = 0
        sintaxe = {
            1 : "id",
            2 : Keywords.PSQLDATATYPES
        }
        while i < len(tokens) and not self.__hasErros and tokens[i].getType() not in ("EOC", "EOF") and iSintaxe < 2:
            iSintaxe += 1
            if (tokens[i].getType() in sintaxe[iSintaxe]):
                pass
            elif (tokens[i].getType() != sintaxe[iSintaxe]):
                thk = tokens[i]
                self.__showMessageError(f'[PSQL#20] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                return False
            i += 1
        return True

    def __retriveTOKeyword(self, tokens, index):
        i = index
        iSintaxe = 0
        sintaxe = {
            1 : Keywords.PARA,
            2 : "id"
        }
        while i < len(tokens) and not self.__hasErros and tokens[i].getType() not in ("EOC", "EOF"):
            iSintaxe += 1
            if tokens[i].getType() != sintaxe[iSintaxe]:
                thk = tokens[i]
                self.__showMessageError(f'[PSQL#21] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                return False
            i += 1
        return True

    def __retriveForeignKeyKeyword(self, tokens, index):
        i = index
        iSintaxe = 0
        sintaxe = {
            1 : Keywords.CHAVE,
            2 : Keywords.ESTRANGEIRA,
            3 : '(',
            4 : 'id',
            5 : ')',
            6 : Keywords.REFERENTE,
            7 : 'id',
            8 : '(',
            9 : 'id',
            10 : ')'
        }
        command = ""
        
        while i < len(tokens) and not self.__hasErros and tokens[i].getType() not in ("EOC", "EOF") and iSintaxe < len(sintaxe):
            iSintaxe += 1
            if iSintaxe in (1, 2):
                if tokens[i].getType() == sintaxe[1] and tokens[i + 1].getType() == sintaxe[2]:
                    command += f"{Keywords.FOREIGN} {Keywords.KEY} "
                    i += 2
                    iSintaxe = 2
                    continue
                else:
                    thk = tokens[i]
                    self.__showMessageError(f'[PSQL#23] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                    return (False, '', index)
            elif tokens[i].getType() != sintaxe[iSintaxe]:
                thk = tokens[i]
                self.__showMessageError(f'[PSQL#24] Token `{Keywords.GetPSQL(thk.getValue())}` não esperado próximo a {thk.getPosition()}')
                return (False, '', index)
            command += f"{self.__writeToken(tokens[i])} "
            i += 1
        return (True, command, i)

    def __writeToken(self, token):
        value = f"{token.getType() if token.getType() in Keywords.ALL else token.getValue()}"
        value = Keywords.GetSQLKeyword(value)
        if token.getType() == 'String':
            return f"'{value}'"
        else:
            return value

    def __showMessageError(self, message):
        if not self.__hasErros:
            self.__hasErros = True
            print(message)