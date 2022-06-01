# ValkyrieDB
## Instalação
1. Você pode adquirir o software através do link: https://github.com/Guilherme-Rigon/ValkyrieDB/releases
2. Crie uma pasta (preferencialmente na raiz do sistema) e extraia os arquivos dentro da pasta
3. Para testar você pode através do Prompt de Comando executar a seguinte linha de código 
```CMD
main.exe -w -path teste.psql
```
4. Para executar comandos através do CLI você pode executar o arquivo com dois cliques ou através do Prompt de Comando executar:
```CMD
main.exe -w
```
## Debugando o Código Fonte do Sistema
Caso queira fazer alguma modificação no código fonte, para executar o código primeiramente deverá instalar as seguintes dependencias:
* Tabulate (pip install tabulate)
* SQLite3

O mesmo comando de uso pode ser usado para iniciar a aplicação mudando somente o arquivo para o main.py
```CMD
py main.py -w -path teste.psql
```
## Utilização dos Comandos
Todos os comandos do PSQL são utilizados com as declarativas em sua forma **imperativa** sendo assim segue abaixo alguns exemplos de comandos válidos pelo analisador sintático:
* DDL
```PSQL
CRIE TABELA Usuarios (id INTEIRO IDENTIFICADOR CHAVE, nome TEXTO)
CRIE TABELA Endereco (id INTEIRO IDENTIFICADOR CHAVE, IdUsuario INTEIRO, Endereco TEXTO, CHAVE ESTRANGEIRA (idUsuario) REFERENTE Usuarios(id))
ALTERE TABELA Usuarios ADICIONE Telefone TEXTO
ALTERE TABELA Usuarios RENOMEIE PARA tbl_usuarios
EXCLUA TABELA tbl_usuarios
```
* DML
```PSQL
INSIRA EM Usuarios2 VALORES (1, 'Guilherme', '999999999')
INSIRA EM Endereco VALORES (1, 1, 'RUA X PERTO DE Y NUMERO 00')
ATUALIZE Usuarios2 DEFINA nome = 'Guilherme Rigon' ONDE id = 1
DELETE DE Usuarios2 ONDE id = 1
```
* DQL
```PSQL
SELECIONE TUDO DE tbl_usuarios, Endereco ONDE tbl_usuarios.id = Endereco.IdUsuario
```
