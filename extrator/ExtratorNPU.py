# -*- coding: utf-8 -*-

import re

import os, sys
import datetime
from extrator.ExtratorBase import ExtratorBase
from extrator.ProcessaExtrator import ProcessaExtrator
from pdjus.service.CadernoService import CadernoService
from pdjus.service.DiarioService import DiarioService
from pdjus.service.ProcTempService import ProcTempService
from pdjus.service.ProcTempTagService import ProcTempTagService
from util.StringUtil import remove_acentos, remove_varios_espacos
from util.ConfigManager import ConfigManager
from pdjus.modelo.ProcTemp import ProcTemp
from util.RegexUtil import RegexUtil

class ExtratorNPU(ExtratorBase):

    def __init__(self, arquivo, acompanhamento = None,arquivo_bd = None):
        super(ExtratorNPU, self).__init__("TRF", arquivo, acompanhamento, None,arquivo_bd)

        self.aux_dict_estados = {
            'amazonas': "AM",
            'acre': "AC",
            'bahia': "BA",
            'tocantins': "TO",
            'minas gerais': "MG",
            'distrito federal': "DF",
            'goias': "GO",
            'piaui': "PI",
            'amapa': "AP",
            'roraima': "RR",
            'rondonia': "RO",
            'para': "PA",
            'maranhao': "MA",
            'mato grosso': "MT",
            'mato grosso do sul': "MS"
        }

        self.distribuicoes = []
        self.publicacoes = []

        self.versao = 1

        self.regex_npu = "(\\b\d{1,7}[\-\s]*?\d{2}\.?(19|20)\d{2}\.?[48]\.?\d{2}\.?\d{4}\\b|\\b(19|20)\d{2}\.?\d{2}\.?\d{2}\.?\d{5,6}[\-\s]*?\d\\b)"  # AAAA.RE.OR.NNNNN-D

        self.regex_skip_bad_conversion = "PROCESSO:\s*PROCESSO:"
        self.regex_partes = "(?P<PARTE>^.*\s:.*\s)"

        self.flags=re.I|re.M|re.U|re.X


    @profile
    def extrai(self,tag=None):

        texto_arquivo = self._arquivo.read()

        if texto_arquivo:

            proc_temp_service = ProcTempService()
            proc_temp_tag_service = ProcTempTagService()

            currTag = proc_temp_tag_service.dao.get_por_tag(os.path.basename(self._arquivo.name).split('_')[0] + '_pre')

            k = 0

            for m in re.finditer(self.regex_npu, texto_arquivo, flags=self.flags):

                k += 1

                p = ProcTemp()
                p.numero = m.group(0).replace(' ', '')

                print(p.numero)

                if re.search(RegexUtil.npu_trfs, m.group(0), self.flags):
                    p.is_npu = True
                    p.numero = p.numero.zfill(20)
                    p.ano = int(re.search('(\d{4})\d{7}$', p.numero).group(1))
                else:
                    p.is_npu = False
                    p.ano = int(re.search('^(\d{4})', p.numero).group(1))

                p.tag = currTag
                p.versao = self.versao
                p.arquivo_origem = self._arquivo_bd

                proc_temp_service.salvar(p, commit=False)

                if k == 300:
                    k = 0
                    proc_temp_service.dao.commit()

            proc_temp_service.dao.commit()

            return True
        else:
            return False

    def trata_classe(self, classe):
        return re.sub("\s\s", " ", classe.strip().upper().replace("AUTOR","").strip())

    def pular_arquivo_mal_convertido(self, regex):

        with open(self._arquivo.name, encoding='utf-8', mode='r', errors="ignore") as file:

            try:
                f = file.read()

                if re.search(self.regex_skip_bad_conversion, f, flags=self.flags):
                    return None

                return f

            except Exception as e:
                print("Erro ao limpar cabeçalhos")
                return None

    def cria_lista_de_linhas(self):
        pass
    def identifica_data_cabecalho(self):
        pass
    def is_edital(self):
        pass
    def procura_processos_falencia(self):
        pass
    def salva_dados(self):
        pass

    def get_caderno(self):
        diario = os.path.basename(self._arquivo.name)

        try:
            data = datetime.datetime.strptime(re.search("(\d{4}_\d{2}_\d{2}).*?\.txt", diario).group(1),
                                              "%Y_%m_%d")
        except:
            data = None
            ConfigManager().escreve_log('Data invalida para ' + diario + '. Pulando...',
                                        self._acompanhamento.nome, self.__erro)

        diario = DiarioService().preenche_diario('TRF01', data)

        caderno = CadernoService().preenche_caderno(self.get_nome_caderno(),diario)

        return caderno

    def get_nome_caderno(self):

        return '_'.join(self._arquivo.name.split('_')[1:3])

if __name__ == '__main__':

    try:
        param = sys.argv[1]
    except:
        param = "processar"

    if param == "listar":
        # listar todos os arquivos do TRF1 que não foram processados ainda
        p = ProcessaExtrator(sys.argv[2], "txt", ExtratorNPU, None)
        p.lista_arquivos_nao_processados(sys.argv[2])
    else:
        p = ProcessaExtrator(param.split('_')[0], "txt", ExtratorNPU, None)
        p.extrai_arquivo(param, extrai_extraido=True)

        # for ano in range(2017, 2018):
        # # for ano in range(2014, 2015):
        #     for mes in range(12, 13):
        #         print("Processando {}/{}".format(ano, mes))
        #         p.extrai_diversos_diretorio('C:\\Users\\e279274021\\Desktop\\TRF\\TRF5\\{ANO}\\{MES}'.format(ANO=str(ano), MES="{:02d}".format(mes)), 'TRF05_')
        #         # p.extrai_diversos_diretorio(
        #         #   'Z:\\TRF\\TRF01\\txt\\{ANO}\\{MES}'.format(ANO=str(ano), MES="{:02d}".format(mes)), 'TRF01_COMPLETO_2014_01_15')
        #         # p.extrai_diversos_diretorio(
        #             #     '..\\..\\dados',
        #             #     'TRF01_COMPLETO_2014_02_06')