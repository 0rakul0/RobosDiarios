from multiprocessing import Process, JoinableQueue, cpu_count
import os, time
from abc import ABCMeta, abstractmethod

# classe responsável por gerenciar o multiprocessamento
class WorkManager:
    def __init__(self, n_procs=cpu_count()):  # numero de processos default igual ao numero de cores
        self.n_procs = n_procs

        # fifo list, maximo de 2x de itens esperando para ser processados
        self.queue = JoinableQueue(maxsize=int(n_procs * 2))
        self.procs = []

        # cria processos trabalhadores
        for i in range(n_procs):
            self.procs.append(_worker(self.queue))

        self.start_procs()

    # inicializa processamento dos workers
    def start_procs(self):
        for proc in self.procs:
            proc.start()

    # insere task t na fila de tarefas a serem executadas pelos workers
    def append_task(self, t):
        self.queue.put(t)

    def print_queue_size(self):
        print(self.queue.qsize())

    # manager espera pelo termino do processamento de todas as tarefas da fila
    def wait(self):
        self.queue.join()

    # finaliza processos workers
    def terminate(self):
        # sentinel objects to allow clean shutdown: 1 per worker
        for i in range(self.n_procs):
            self.queue.put(None)

# classe worker ~privada~ > deve ser instanciada e terminada somente pelo workmanager
class _worker(Process):
    def __init__(self, queue):
        super(_worker, self).__init__()
        self.queue = queue

    def run(self):
        for task in iter(self.queue.get, None):
            task.execute()
            self.queue.task_done()

    def print_pid(self):
        print(os.getpid(), "is instanciated")

# classe abstrata que define uma tarefa
class AbstractTask(object):
    __metaclass__ = ABCMeta

    #def __init__(self):
    #    pass

    @abstractmethod
    def execute(self):
        return NotImplemented


###################### inicio ########################

# exemplos de como uma tarefa pode ser criada

class MergeTask(AbstractTask):

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def execute(self):

        # dado um nome de PDF, juntar todas as partes
        # caso haja problema em alguma página, baixa novamente a mesma
        from util.FileManager import FileManager, ConfigManager
        from os import listdir
        from os.path import isfile, join
        import re

        fm = FileManager("TRF", "log_merge_trf1-2.txt", "erro_merge_trf1-2.txt")
        path = fm.caminho(self.name, self.data, True)
        prefix_name = '_'.join(self.name.split('_')[:-1])

        # verificar qual conjunto de arquivos corresponde as partes de um arquivo
        pdfs = [join(path, f) for f in listdir(path) if re.search(prefix_name+"_[0-9]{1,}\.pdf", f, re.I)]

        saida = join(path, prefix_name+".pdf")

        if len(pdfs) > 1:  # arquivos com só uma parte continuarão com sequencial
            fm.juntar_pdfs(saida, pdfs, apagar_arquivos=True, ordenar=True)


class DownloadTask(AbstractTask):

    # atributos da classe devem ser serializaveis
    def __init__(self, url, name, data):
        #    super(Task, self).__init__()
        self.url = url
        self.name = name
        self.data = data
        # self.processed = False

    def execute(self):
        # este método deve conter tudo o que a tarefa precisa para executar
        # este método faz download de uma url
        from requests import get
        from requests.exceptions import ReadTimeout
        from util.FileManager import FileManager, ConfigManager
        import re

        retry = 3

        fm = FileManager("TRF", "log_download_trf1-2.txt", "erro_download_trf1-2.txt")
        path = fm.caminho(self.name, self.data, True)

        if not os.path.exists(path):
            os.makedirs(path)

        while retry > 0:
            if not fm.ja_baixado(self.name, self.data, modo=False) or not fm.verificar_pdf(os.path.join(path, self.name)):
                try:
                    response = get(self.url, stream=True, timeout=120)
                except ReadTimeout:
                    retry -= 1
                    continue

                # print(response.headers['content-length'])
                if not fm.erro_download(response, "pdf"):
                    with open(os.path.join(path, self.name), "wb") as myfile:
                        try:
                            if not re.search('was not found on this server',response.text,re.I):
                                for chunk in response.iter_content(1024 * 100):  # chunk in bytes, 100 KB
                                    myfile.write(chunk)
                        except:
                            print("timeout")

                    ConfigManager().escreve_log(" [OK] - {URL} ".format(URL=self.url), "TRF",
                                                "log_download_trf1-downloads.txt", verbose=False)

                    retry = 0
                else:
                    ConfigManager().escreve_log(" [ERRO] - {NAME} - {URL} ".format(NAME=self.name, URL=self.url), "TRF",
                                                "log_download_trf1-downloads.txt")
                    time.sleep(5)
                    if not re.search('was not found on this server', response.text, re.I):
                        print(response.headers)
            else:
                ConfigManager().escreve_log("{} já existe. Pulando...".format(self.name), "TRF",  "log_download_trf1-2.txt")

            retry -= 1
        # self.processed = True

def execution_example():

    # cria um gerente com numero de trabalhadores igual ao de cores da maquina
    # pode ser passado valor inteiro para definir o numero de processos
    wm = WorkManager()

    # cria 10 tarefas
    for i in range(0, 10):
        t = DownloadTask("http://ipv4.download.thinkbroadband.com/5MB.zip", i)
        wm.append_task(t)

    print("jobs criados...")

    print("processos inicializados")

    wm.wait()

    print("Finalizado")

    wm.terminate()


if __name__ == '__main__':
    execution_example()