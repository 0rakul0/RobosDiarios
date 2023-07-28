from bs4 import BeautifulSoup as bs
from collections import defaultdict

import sys
import re

class montar_dicionario_do_processo(object):
    '''
        Classe para tratar as informacoes de uma pagina do TRF5 para processos 
        RPV.
    '''
    
    def __init__(self, html):
        '''
        Args:
            html (tipo: html string): String contendo o codigo HTML da pagina RPV do TRF5
            regex_aba_processo (tipo: list): Lista contendo "regular expression objects" utilizados para extrair informacoes da aba processo
            regex_aba_dados (tipo: list): Lista contendo "regular expression objects" utilizados para extrair informacoes da aba dados
            regex_aba_partes (tipo: list): Lista contendo "regular expression objects" utilizados para extrair informacoes da aba partes
            regex_aba_fases (tipo: list): Lista contendo "regular expression objects" utilizados para extrair informacoes da aba fases
        '''
        
        self.html = html
        
        self.regex_aba_processo = [re.compile(r'(\d+)\s+(RPV\s+\d+)\s+PROC.\sORIG.\s+(\d+)', re.MULTILINE | re.DOTALL)] 
    
        self.regex_aba_dados = [re.compile(pattern, re.MULTILINE | re.DOTALL) for pattern in                                     
                                                [r"(ASSUNTO)\.+:\s(.+?)\n",
                                                r"(ORIGEM)\.+:\s(.+?)\n",
                                                r"(LOCALIDADE)\.+:\s(.+?)\n",
                                                r"(TIPO)\.+:\s(.+?)\n",
                                                r"(DATA AUTUACAO)\.+:\s(.+?)\n",
                                                r"(DATA DISTRIB)\s+?\.+:\s(.+?)\n",
                                                r"(DATA LIQUIDACAO)\.+:\s(.+?)\n",
                                                r"(ELEMENTO DESPESA)\.+:\s(.+?)\n"
                                                ]
                        ]
                                                
        self.regex_aba_partes = [re.compile(pattern, re.MULTILINE | re.DOTALL) for pattern in                                     
                                                [
                                                r"(Deprec):\s(.+?)\n",
                                                r"(Reqte):\s(.+?)\n",
                                                r"(Reqdo):\s(.+?)\n"
                                                ]
                        ]
                                                
        self.regex_aba_fases = [re.compile(r'(DATA):\s(.+?)\s+(FASE):\s(.+?)\n', re.MULTILINE | re.DOTALL)]

        

    def limpar_espaços(self, texto):
        '''
            Metodo para separar as linhas de uma string e retirar os espacos
            em branco no inicio de cada linha
        Args:
            texto (tipo: string): string com multiplas linhas.
            
        Returns:
            linhas_do_texto (tipo: list): Lista contendo cada linha do texto
            passado para o metodo ordenada de acordo com a localizacao da linha
            no texto.
        '''
        
        texto = texto.splitlines()
        
        linhas_do_texto = []
        
        for linha in texto:
            linhas_do_texto.append(linha.strip())
    
        return linhas_do_texto
    
    def checar_advogados_das_partes(self, linhas_do_texto):
        '''
            Metodo para separar os advogados de cada parte
        Args:
            linhas_do_texto (tipo: list): Lista contendo cada linha do texto
            que deve ser processado.
        Return:
            advogados (tipo: list): Lista de tuples (x,y):
                x - Identificacao da parte do advogado
                y - Nome do advogado
        '''
        advogados = []
        for (idx,linha) in enumerate(linhas_do_texto):
            i = 0
            if linha.startswith('Adv'):
                while True:
                    if linhas_do_texto[idx - i].startswith('Reqte'):
                        advogados.append(('Adv_Reqte', re.sub(r'Adv: ', '', linhas_do_texto[idx])))
                        break
                    elif linhas_do_texto[idx - i].startswith('Reqdo'):
                        advogados.append(('Adv_Reqdo', re.sub(r'Adv: ', '', linhas_do_texto[idx])))
                        break
                    else:
                        i += 1
                        continue
        return advogados
    
    def checar_observacao_das_fases(self, linhas_do_texto):
        '''
            Metodo para identificar as observacao de cada fase
        Arg:
            linhas_do_texto (tipo: list): Lista contendo cada linha do texto
            que deve ser processado.
        Return:
            observacao (tipo: list): Lista contendo as observacoes na ordem
            em que elas aparecem na pagina. Se uma fase nao possui observacao
            o index referente a fase e preenchido com "Fase sem observacao".
        '''
        observacao = []
        for (idx,linha) in enumerate(linhas_do_texto):
            if linha.startswith('DATA'):
                try:
                    if linhas_do_texto[idx + 1].startswith('OBSERVACAO'):
                        m = re.match(r'OBSERVACAO:\s+(.*)',linhas_do_texto[idx + 1])
                        observacao.append(m[1])   
                    else:
                        observacao.append('Fase sem observacao')
                except IndexError:
                    observacao.append('Fase sem observacao')
                      
        return observacao
    
    

    def extrair_tabela_de_conteudo(self):
        '''
            Metodo para extrair as tabelas html que contem as informacoes
            sobre os processos
        Return:
            tabela (tipo: BeautifulSoup Object): BeautifulSoup Object contendo 
            as tabelas de informacoes do processo
        '''
        
        soup = bs(self.html, 'html5lib')
    
        tabela = soup.find_all('table')
    
        try:
            if len(tabela[0].select('tr > th')) != len(tabela[0].select('tr > td > pre')):
                raise IndexError
        except IndexError:
            input("A página parece não corresponder a um processo RPV. Verificar \
                  alterações na estrutura da página. Aperte Enter para finalizar o \
                  programa")
            sys.exit()
            
        return tabela

    def montar_dicionario(self, table):
        '''
            Metodo para montar um dicionario do processo
        Arg:
            table (tipo: BeautifulSoup Object): Tabela contendo as informacoes
            do processo
        Return:
            processo (tipo: defautdict(list)): Dicionario contendo informacoes
            sobre o processo
        '''
        
        processo = defaultdict(list)
        
        
        for row in table[0].select('tr > th'):
            if row.get_text() == 'PROCESSO':
                for regex in self.regex_aba_processo:
                    for (v1,v2,v3) in regex.findall(table[0].select('tr > td > pre')[0].get_text()):
                        processo['NPU'].append(v1)
                        processo['ClASSE'].append(v2)
                        processo['PROC._ORIG.'].append(v3)
                        
            if row.get_text() == 'DADOS':
                for regex in self.regex_aba_dados:
                    for (k,v) in regex.findall(table[0].select('tr > td > pre')[1].get_text()):
                        processo[k].append(v)
                        
            if row.get_text() == 'PARTES':
                for regex in self.regex_aba_partes:
                    for (k,v) in regex.findall(table[0].select('tr > td > pre')[2].get_text()):
                        processo[k].append(v)
                partes = table[0].select('tr > td > pre')[2].get_text()
                linhas_das_partes = self.limpar_espaços(partes)
                for (k,v) in self.checar_advogados_das_partes(linhas_das_partes):
                    processo[k].append(v)
                
                        
            if row.get_text() == 'FASES':
                for regex in self.regex_aba_fases:
                    for (_, v2, k, v3) in regex.findall(table[0].select('tr > td > pre')[3].get_text()):
                        processo[k].append(v3 + ' Data: ' + v2 )
                fases = table[0].select('tr > td > pre')[3].get_text()
                linhas_das_fases = self.limpar_espaços(fases)
                processo['OBSERVACAO'] = self.checar_observacao_das_fases(linhas_das_fases)
                
        return processo
    
    def executar(self):
        '''
            Metodo para executar todos os metodos da classe e retornar
            um dicionario do processo
        Return:
            dicionario_do_processo (tipo: defautdict(list)): Dicionario 
            contendo informacoes sobre o processo
        '''
        tabela = self.extrair_tabela_de_conteudo()
        dicionario_do_processo = self.montar_dicionario(tabela)
        return dicionario_do_processo
        