import datetime

from pdjus.conexao.Conexao import Singleton
from pdjus.dal.CnisEmpresaDao import CnisEmpresaDao
from pdjus.modelo.CnisEmpresa import CnisEmpresa
from pdjus.service.BaseService import BaseService


class CnisEmpresaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(CnisEmpresaService, self).__init__(CnisEmpresaDao())

    def preenche_cnis_empresa(self,id_empresa_estab,nome, natureza_juridica, opcao_simples, situacao_prev, situacao_srf, nome_fantasia , microempresa, mei,data_inicio):
        cnisEmpresa = self.dao.get_por_id_empresa_estab(id_empresa_estab)
        if not cnisEmpresa:
            cnisEmpresa = CnisEmpresa()
            cnisEmpresa.nome = nome
            cnisEmpresa.id_empresa_estab = id_empresa_estab
            cnisEmpresa.natureza_juridica = natureza_juridica
            cnisEmpresa.opcao_simples = opcao_simples
            cnisEmpresa.situacao_prev = situacao_prev
            cnisEmpresa.situacao_srf = situacao_srf
            cnisEmpresa.nome_fantasia = nome_fantasia
            cnisEmpresa.in_microempresa = microempresa
            cnisEmpresa.in_mei = mei
            try:
                cnisEmpresa.data_inicio_atividade = datetime.strptime(data_inicio, '%d/%m/%Y')
            except:
                pass
            self.salvar(cnisEmpresa)
        return cnisEmpresa