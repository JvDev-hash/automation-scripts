'''
Script de automação de criação de um cluster Swarm + o deploy de service usando um compose
O Cluster é formado por duas máquinas linux: 1 manager e 1 worker
Foi utilizado dotenv para configuração das variáveis sensíveis como endereço e senhas das máquinas,
paramiko para acesso via ssh e os + subprocess para utilizar as variáveis de ambiente/execução dos comandos locais
'''
from dotenv import load_dotenv
import os
import paramiko
import subprocess

load_dotenv()

managerAddr = os.getenv("MANAGER_ADDR")

# Criação do cluster e geração do código para juntar-se ao cluster criado
output = subprocess.check_output("sudo docker swarm init --advertise-addr " + managerAddr, shell=True)

output = subprocess.check_output("sudo docker swarm join-token worker", shell=True)

output = output.decode("utf-8")

print(output)

# Obtenção do comando de join
joinCommand = output.split("command:",1)[1]

username = os.getenv("WORKER_USER")
userpass = os.getenv("WORKER_PASS")
hostname = os.getenv("WORKER_URL")

# Acesso via ssh, usando o Paramiko, à segunda máquina e execução do comando para ela juntar-se ao cluster
try:
    port = '22'
    
    client = paramiko.SSHClient()
    
    # Foi removido a necessidade de checagem das chaves pois eram máquinas na mesma rede,
    # além de não ter a necessidade atual dessa conexão ser completamente segura
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
         
    client.connect(hostname, port=22, username=username, password=userpass)
         
    (stdin, stdout, stderr) = client.exec_command(joinCommand)
         
    cmd_output = stderr.read()
    print('log printing: ', joinCommand, cmd_output)
finally:
    client.close()

# Deploy do service utilizando o compose
output = subprocess.check_output("sudo docker stack deploy -c docker-compose.yml webservices", shell=True)

output = output.decode("utf-8")

print(output)
