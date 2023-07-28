import os
import glob

def merge_csv(path_merged_file, path_files, file_name,  recursive=False):
    '''
    :param path_merged_file: caminho onde vai ficar o arquivo de resultado (recomendado utilizar uma pasta diferente de onde esão os arquivos para merge)
    :param path_files: caminho onde se encontram os arquivos para serem juntados
    :param file_name: nome do arquivo merge
    :param recursive: flag para abrir pastas dentro de pastas
    '''

    if not os.path.exists(path_merged_file):
        os.mkdir(path_merged_file)

    if recursive:
        all_filenames = [i for i in glob.iglob (path_files + '/**')]
    else:
        all_filenames = [i for i in os.listdir(os.path.abspath(path_files)) if not os.path.isdir(i)]

    for file in all_filenames:
        if not '.csv' in file:
            os.rename(path_files+'\\'+file, path_files+'\\'+file+'.csv')
            file = file+'.csv'
        print('Fazendo merge do arquivo {}'.format(file))
        with open(path_merged_file+'\\'+file_name, 'a+', encoding='utf-8') as f:
            try:
                f.write(''.join(open(path_files+'\\'+file+('.csv' if '.csv' not in file else ''), encoding='utf-8')))
            except:
                for line in open(path_files+'\\'+file+('.csv' if '.csv' not in file else ''), encoding='utf-8').readlines():
                    f.write(line)

        f.close()

merge_csv('C:\\Users\\e7609043\\Desktop\\spark\\Resultado','C:\\Users\\e7609043\\Desktop\\spark\\resultado_IPEA_mencoes_dou_2010_2020','IPEA_mencoes_dou_2010_2020.csv')
