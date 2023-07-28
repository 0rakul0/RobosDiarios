from peewee import SENTINEL
from pdjus.conexao.Conexao import *
import re


class UpdateSchema():
    def __init__(self):
        #self.execute_script()
        self.insert_proc_temp('09629521020128260506', 'desenv_jucesp')

    def execute_script(self):
        ############################################################################################################################
        # A LISTA DE SCHEMAS DEVE SER PREENCHIDA COM TODOS OS SCHEMAS QUE SE DESEJA ATUALIZAR                                            #
        # A VARIÁVEL "query" É A MODIFICAÇÃO QUE SE DESEJA FAZER NO BANCO DE DADOS (MANTER TODA A MODIFICAÇÃO SEM QUEBRA DE LINHA) #
        ############################################################################################################################

        lista_schemas = ['desenv_teste','desenv_teste2']

        query = 'CREATE TABLE desenv_teste.tabela_teste (     id bigserial NOT NULL,     nome character varying NOT NULL,     processo_id bigint NOT NULL,     CONSTRAINT tabela_teste_id_pkey PRIMARY KEY (id),     CONSTRAINT tabela_teste_processo_id_fkey FOREIGN KEY (processo_id)         REFERENCES desenv_teste.processo (id) MATCH SIMPLE         ON UPDATE NO ACTION         ON DELETE NO ACTION ) WITH (     OIDS = FALSE ) TABLESPACE pg_default;  ALTER TABLE desenv_teste.tabela_teste     OWNER to role_mining;'.replace("'",'"')

        # drop = "DROP TABLE desenv_teste2.tabela_teste"

        for schema in lista_schemas:

            nome_schema = re.findall('(\w+)\.\w+', query)[0]
            nova_query = re.sub(nome_schema, schema, query)

            try:
                db.execute_sql(nova_query, params=None, commit=SENTINEL)
                print('Atualizou o schema {}'.format(schema))
            except Exception as e:
                print(e)

    def insert_proc_temp(self, npu, schema):

        query = "INSERT INTO {schema}.proc_temp(tag_id, numero) values (1, '{npu}');".format(schema=schema, npu=npu)

        try:
            db.execute_sql(query, params=None, commit=SENTINEL)
            print('Inseriu o processo {} na proc_temp do schema {}'.format(npu,schema))
        except Exception as e:
            print(e)



if __name__ == '__main__':
    chama_classe = UpdateSchema()