__author__ = 'B249025230'
from pdjus.modelo.BaseClass import *

class ProcTempTag(BaseClass):
    id = PrimaryKeyField(null=False)
    tag = CharField(db_column="tag")

    def __init__(self,*args, **kwargs):
       self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(ProcTempTag, self).__init__(["nome"],*args, **kwargs)

    def is_valido(self):
        return True

    class Meta:
        db_table = "proc_temp_tag"