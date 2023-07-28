
from pdjus.dal.GenericoDao import *
from pdjus.modelo.ProcTempTag import ProcTempTag
from util.StringUtil import remove_varios_espacos, remove_acentos


class ProcTempTagDao(GenericoDao, metaclass=Singleton):
    def __init__(self):
        super(ProcTempTagDao, self).__init__(ProcTempTag)

    def get_por_tag(self, tag):
        try:
            return self._classe.select().where(self._classe.tag == tag).get()
        except self._classe.DoesNotExist as e:
            return None