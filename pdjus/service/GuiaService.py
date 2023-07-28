from pdjus.conexao.Conexao import Singleton
from pdjus.dal.GuiaDao import GuiaDao
from pdjus.modelo.Guia import Guia
from pdjus.service.BaseService import BaseService


class GuiaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(GuiaService, self).__init__(GuiaDao())
    
    def preenche_guia(self ,processo , numero_guia,data_pagamento = None,data_emissao = None,valor = None,pagante = None,cheque_sem_fundo = None,autenticacao = None):
        guia = self.dao.get_por_processo_e_numero_guia(processo ,numero_guia)
        if not guia:
            guia = Guia()
            guia.numero_guia = numero_guia
            guia.data_pagamento = data_pagamento
            guia.data_emissao = data_emissao
            guia.valor = valor
            guia.pagante = pagante
            guia.cheque_sem_fundo = cheque_sem_fundo
            guia.autenticacao = autenticacao
            guia.processo = processo
            self.salvar(guia)
        return guia

    def preenche_guia_por_dic_guia(self,processo,dic_guia):
        cheque_sem_fundo = False if dic_guia['cheque_sem_fundo'] == 'Não' else True
        return self.preenche_guia(processo,dic_guia['numero_guia'],dic_guia['data_pagamento'],dic_guia['data_emissao'],dic_guia['valor'],dic_guia['pagante'],cheque_sem_fundo,dic_guia['autenticacao'])