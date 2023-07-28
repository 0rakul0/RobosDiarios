#TODO Depreciado
'''
# -*- coding: utf-8 -*-
from extrator.ExtratorCPCSTJ import ExtratorCPCSTJ

from util.ConfigManager import ConfigManager
from extrator.ProcessaExtrator import ProcessaExtrator
from extrator.ExtratorDJRS import ExtratorDJRS
from extrator.ExtratorDJSP import ExtratorDJSP
from extrator.ExtratorJUCESP import ExtratorJUCESP
from acompanhamento_processual.AcompanhamentoProcessualRS import AcompanhamentoProcessualRS
from acompanhamento_processual.AcompanhamentoProcessualDJSP import AcompanhamentoProcessualDJSP

class IniciaExtracao:
    def inicia_extracao(self):
        #pwd = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))

        #multi_processa = MultiProcessaExtrator("DJRS", "txt", ExtratorDJRS,AcompanhamentoProcessualRS)
        #multi_processa.extrai_diversos()
        #multi_processa = MultiProcessaExtrator("STJ", "txt", ExtratorCPCSTJ)
        #multi_processa.extrai_diversos()
        multi_processa = ProcessaExtrator("DJSP", "txt", ExtratorDJSP,AcompanhamentoProcessualDJSP)
        multi_processa.extrai_diversos()
        # multi_processa = MultiProcessaExtrator("JUCESP", "txt", ExtratorJUCESP,AcompanhamentoProcessualDJSP)
        # multi_processa.extrai_diversos()
        pass

if __name__ == '__main__':
    ie = IniciaExtracao()
    ie.inicia_extracao()
'''