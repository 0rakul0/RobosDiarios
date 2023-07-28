from pdjus.conexao.Conexao import Singleton
from pdjus.dal.CnisEstabelecimentoDao import CnisEstabelecimentoDao
from pdjus.modelo.CnisEstabelecimento import CnisEstabelecimento
from pdjus.service.BaseService import BaseService


class CnisEstabelecimentoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(CnisEstabelecimentoService, self).__init__(CnisEstabelecimentoDao())

    def preence_cnis_estabelecimento(self,id_empresa_estab,cnpj, nome = None,cnisEmpresa= None,id_muni_prev= None,nu_cep= None,id_uf_prev= None,cd_situacao_prev= None,cd_situacao_srf= None,cd_matriz_filial= None,cs_cnae_2_0=None,nu_cnae_2_0=None,nu_cnae_cmpl_2_0=None):
        cnisEstabelecimento = self.dao.get_por_id_empresa_estab_e_cnpj(id_empresa_estab, cnpj)
        if not cnisEstabelecimento:
            cnisEstabelecimento = CnisEstabelecimento()
            cnisEstabelecimento.id_empresa_estab = id_empresa_estab
            cnisEstabelecimento.id_muni_prev = id_muni_prev
            cnisEstabelecimento.nu_cep = nu_cep
            cnisEstabelecimento.id_uf_prev = id_uf_prev
            cnisEstabelecimento.cd_situacao_prev = cd_situacao_prev
            cnisEstabelecimento.cd_situacao_srf = cd_situacao_srf
            cnisEstabelecimento.cnpj = cnpj
            cnisEstabelecimento.cd_matriz_filial = cd_matriz_filial
            cnisEstabelecimento.nome = nome
            try:
                cnisEstabelecimento.data_inicio_atividade = datetime.strptime(data_inicio_atividade, '%d/%m/%Y')
            except:
                cnisEstabelecimento.data_inicio_atividade = None
            cnisEstabelecimento.cs_cnae_2_0 = cs_cnae_2_0
            cnisEstabelecimento.nu_cnae_2_0 = nu_cnae_2_0
            cnisEstabelecimento.nu_cnae_cmpl_2_0 = nu_cnae_cmpl_2_0
            cnisEstabelecimento.cnis_empresa = cnisEmpresa
            self.salvar(cnisEstabelecimento)
        return cnisEstabelecimento