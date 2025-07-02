# Inicializa o daemon e registra o serviço

# ANTES DE RODAR ESSE ARQUIVO CERTIFICAR QUE ESTÁ RODANDO O NAMESERVER DO PYRO5
# python -m Pyro5.nameserver

from namenode.namenode import NameNode
from core.constants import NAMENODE_SERVICE_NAME
from core.network import start_daemon, register_service

def main():
    print("[NameNode] Iniciando...")

    try:
        # Criar daemon Pyro5
        daemon = start_daemon()

        # Criar instância do NameNode (exposto via Pyro)
        namenode = NameNode()

        # Registrar no NameServer
        uri = register_service(NAMENODE_SERVICE_NAME, namenode, daemon)

        print(f"[NameNode] Registrado como {NAMENODE_SERVICE_NAME}")
        print(f"[NameNode] URI: {uri}")
        print("[NameNode] Aguardando requisições...")

        daemon.requestLoop()

    except Exception as e:
        print(f"[NameNode] Falha na inicialização: {e}")

if __name__ == "__main__":
    main()
