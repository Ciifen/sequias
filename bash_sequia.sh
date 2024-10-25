#!/bin/bash
readonly envFile="/var/py/volunclima/scripts/prediccion/venv/bin/activate"
source ${envFile}
cd /var/py/volunclima/monitor/
python3.9 mapaSequia.py
python3.9 mapaSequia_sin_brasil.py
sshpass -p ******* scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/monitor/salidas/MON-SEQ_01.jpeg ruta_en_el_servidor_de_destino/MON-SEQ_01.jpeg
sshpass -p ******* scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/monitor/salidas/MON-SEQ_03.jpeg ruta_en_el_servidor_de_destino/MON-SEQ_03.jpeg
sshpass -p ******* scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/monitor/salidas/MON-SEQ_06.jpeg ruta_en_el_servidor_de_destino/MON-SEQ_06.jpeg
sshpass -p ******* scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/monitor/salidas/MON-SEQ_09.jpeg ruta_en_el_servidor_de_destino/MON-SEQ_09.jpeg
sshpass -p ******* scp -P **** -o StrictHostKeyChecking=no /var/py/volunclima/monitor/salidas/MON-SEQ_12.jpeg ruta_en_el_servidor_de_destino/MON-SEQ_12.jpeg
