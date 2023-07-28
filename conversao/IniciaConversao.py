# -*- coding: utf-8 -*-
import sys
import traceback
from conversao.Conversor import Conversor
from util.ConfigManager import ConfigManager
import multiprocessing

#ATENÇÃO!!!!
#NÃO ESTÁ CONVERTENDO ARQUIVOS DA PASTA SEM_DATA!
#ATENÇÃO!!!!
def _converte_diario(diarios):
    for diario in diarios:
        try:
            conversor = Conversor(diario[0], diario[1])
            conversor.converte_diretorio()
        except:
            pass

class IniciaConversao(object):

    def __pedacos(self, l, n):
        newn = int(1.0 * len(l) / n + 0.5)
        for i in range(0, n-1):
            yield l[i*newn:i*newn+newn]
        yield l[n*newn-newn:]

    def inicia_conversao(self):
        #pwd = os.path.dirname(os.path.abspath(__file__))#os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
        log = "log_conversao.txt"
        diretorio = "RAIZ"
        erro = "erro_conversao.txt"
        extracoes = [
            ("TRTSP", "pdf"),
            ("DJRS", "pdf"),
            ("DJSP", "pdf"),
            ("JUCESP", "pdf"),
            ("DEJT", "pdf"),
            ("DJRJ", "pdf"),
            ("DJBA", "pdf"),
            ("DJCE", "pdf"),
            ("DOU", "pdf"),
            ("DJMS", "pdf"),
            ("DJPE", "pdf"),
            ("DJPI", "pdf"),
            ("DJPR", "pdf"),
            ("DJSC", "pdf"),
            ("TRF01", "pdf"),
            ("TRF02", "pdf"),
            ("TRF03", "pdf"),
            ("TRF04", "pdf"),
            ("TRF05", "pdf"),
            ("STJ", "pdf"),
            ("DJMG", "pdf"),
            #("DJMG", "rtf"),
            ("DJAC", "pdf"),
            ("DJPB", "pdf"),
            ("DJRR", "pdf"),
            ("DJRN", "pdf"),
            ("DJMA", "pdf"),
            ("DJSE", "pdf"),
            ("DJAL", "pdf"),
            ("DJES", "pdf"),
            ("DJGO", "pdf"),
            ("DJMT", "pdf"),
            ("DJRO", "pdf"),
            ("DJTO", "pdf")
        ]

        try:
            num_procs = multiprocessing.cpu_count()
            ConfigManager().escreve_log("Iniciando conversão {} processos.".format(num_procs), diretorio, log)
        except NotImplementedError:
            num_procs = 4
            ConfigManager().escreve_log("Não foi possível detectar a quantidade de núcleos. "
                                        "Iniciando conversão com {} processos (padrão).".format(num_procs),
                                        diretorio, log)

        pool = multiprocessing.Pool(num_procs)

        jobs = list(self.__pedacos(extracoes, num_procs))

        pool.map(_converte_diario, jobs)

        pool.close()

        ConfigManager().escreve_log("Conversão concluída. Verificar os logs individuais para possíveis erros.", diretorio, log)

if __name__ == '__main__':
    ie = IniciaConversao()
    ie.inicia_conversao()
