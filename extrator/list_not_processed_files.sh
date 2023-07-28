#!/bin/bash
export PYTHONPATH=$PYTHONPATH:/mnt/dmlocal/projetos/ProjetoBPC
export PYTHONPATH=$PYTHONPATH:/mnt/dmlocal/projetos/ProjetoBPC/acompanhamento_processual
export PYTHONPATH=$PYTHONPATH:/mnt/dmlocal/projetos/ProjetoBPC/conversao
export PYTHONPATH=$PYTHONPATH:/mnt/dmlocal/projetos/ProjetoBPC/extrator
export PYTHONPATH=$PYTHONPATH:/mnt/dmlocal/projetos/ProjetoBPC/pdjus
export PYTHONPATH=$PYTHONPATH:/mnt/dmlocal/projetos/ProjetoBPC/robosdiarios
export PYTHONPATH=$PYTHONPATH:/mnt/dmlocal/projetos/ProjetoBPC/scripts_linux
export PYTHONPATH=$PYTHONPATH:/mnt/dmlocal/projetos/ProjetoBPC/util
export PYTHONPATH=$PYTHONPATH:/mnt/dmlocal/projetos/ProjetoBPC/validador
DIR=$(dirname $0)
cd $DIR
cd ..

python3 -m extrator.ExtratorTRF listar $1
