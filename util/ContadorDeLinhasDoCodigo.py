from glob import glob
from pygount import SourceAnalysis, ProjectSummary
import re


def contador_de_linhas_projeto():
    sumario = ProjectSummary()
    paths = glob("/home/e7609043/PycharmProjects/IpeaJUS/robosdiarios/*.py")

    for source_path in paths:
        source_analysis = SourceAnalysis.from_file(source_path, "pygount")
        sumario.add(source_analysis)

    lista_dados_projeto = str(sumario.language_to_language_summary_map['Python']).split(',')
    lista_dados_projeto.pop(0)

    [print(re.sub('^\s+|\)', '', informacao)) for informacao in lista_dados_projeto]

