from pdjus.dal.GenericoDao import *
from pdjus.modelo.ProcessoServidor import ProcessoServidor

class ProcessoServidorDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ProcessoServidorDao, self).__init__(ProcessoServidor)
