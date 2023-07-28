import pdjus.conexao.settings as settings
import os
from pdjus.conexao.ExtensaoPeewee import *
import logging

#conexao_direta = psycopg2.connect(database=settings.DATABASE.get("database"), user = settings.DATABASE.get("username"), password=settings.DATABASE.get("password"), host=settings.DATABASE.get("host"), port=settings.DATABASE.get("port"))


db = PooledPostgresqlExtDatabase(
    settings.DATABASE.get("database"),  # Required by Peewee.
    user=settings.DATABASE.get("username"),  # Will be passed directly to psycopg2.
    password=settings.DATABASE.get("password"),  # Ditto.
    host=settings.DATABASE.get("host"),  # Ditto.
    operations={OP.MOD: '%%',OP.NEG_REGEX: '!~',OP.NOT_EXISTS: 'NOT EXISTS'},
)

default_schema = 'producao'
default_schema = os.getenv('CONEXAO', default_schema)

#PARA PRINTAR TODAS AS CONSULTAS FEITAS NO BANCO BASTA COLOCAR TRUE
print_sqls = False

if print_sqls:
    logger = logging.getLogger('peewee')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SessionDB(metaclass=Singleton):
    transaction = db.transaction()


#from pdjus.conexao import ValidaSchema
#ValidaSchema.valida()











