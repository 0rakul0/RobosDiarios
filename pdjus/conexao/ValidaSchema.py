from peewee import ProgrammingError

from pdjus.conexao.Conexao import SessionDB,default_schema
from pdjus.modelo import BaseClass
import re


def valida():
    coluna_nao_existe = re.compile("column.*\.(.*)\s.*does not exist")
    tabela_nao_existe = re.compile("relation.*\.(.*)\".*does not exist")
    if "siape" in default_schema:
        return
    lista_erros = []
    base = BaseClass()
    MODELS = base.subclasses
    for i,model in enumerate(MODELS):
        try:
            #print("numero {i} de {len}".format(i=i, len=len(MODELS)))
            objs = list(model.select().limit(1))


            if len(objs) > 0:
                obj = objs[0]
        except ProgrammingError as e:
            coluna_match = coluna_nao_existe.search(str(e))
            tabela_match = tabela_nao_existe.search(str(e))
            if coluna_match:
                lista_erros.append(("coluna",coluna_match.group(1),model))
            if tabela_match:
                lista_erros.append(("tabela",tabela_match.group(1),model))
            SessionDB().transaction.rollback()

    for erro in lista_erros:
        if erro[0] == "tabela":
            print("Erro a tabela {tabela} não existe!".format(tabela=erro[1]))
        if erro[0] == "coluna":
            print("Erro a tabela {tabela} precisa que seja criada a coluna {coluna}!".format(tabela=erro[2].__name__,coluna= erro[1]))
    if len(lista_erros) > 0:
        raise ProgrammingError("É necessário fazer modificações no schema, criando as tabelas e colunas citadas!")




