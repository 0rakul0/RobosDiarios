import abc


class BaseService(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,DAO):
        self.dao = DAO
        super(BaseService, self).__init__()

    def salvar(self,obj, caderno=None, tag=None, commit=True, salvar_estrangeiras = True,salvar_many_to_many = True):
        self.dao.salvar(obj, caderno, tag, commit, salvar_estrangeiras,salvar_many_to_many)
