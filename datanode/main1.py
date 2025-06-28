# Inicializa DataNode 1

from datanode.datanode import DataNode
from core.constants import DATANODE_SERVICE_PREFIX
from core.network import start_daemon, register_service

def main():
    print("[DataNode] Iniciando...")

    # Criar daemon Pyro5
    daemon = start_daemon()

    # Criar instância do DataNode (exposto via Pyro)
    datanode = DataNode()

    # Registrar no NameServer
    uri = register_service(DATANODE_SERVICE_PREFIX, datanode, daemon)

    print(f"[DataNode] Registrado como {DATANODE_SERVICE_PREFIX}")
    print(f"[DataNode] URI: {uri}")
    print("[DataNode] Aguardando requisições...")

    daemon.requestLoop()

if __name__ == "__main__":
    main()
