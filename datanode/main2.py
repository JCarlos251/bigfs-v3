# Inicializa DataNode 2

from datanode.datanode import DataNode
from core.constants import DATANODE_SERVICE_PREFIX, NAMENODE_SERVICE_NAME
from core.network import start_daemon, register_service, get_nameserver
from Pyro5.api import Proxy
from datanode.datanode import HeartbeatSender

def main():
    print("[DataNode2] Iniciando...")

    # Definições
    datanode_id = "2"
    service_name = f"{DATANODE_SERVICE_PREFIX}{datanode_id}"
    storage_dir = "servidor/datanode2"

    try:
        # Criação do daemon Pyro5
        daemon = start_daemon()
        datanode = DataNode(storage_dir)

        # Registro no NameServer
        uri = register_service(service_name, datanode, daemon)
        print(f"[DataNode2] Registrado como {service_name}")
        print(f"[DataNode2] URI: {uri}")

        # Registro no NameNode
        try:
            ns = get_nameserver()
            namenode_uri = ns.lookup(NAMENODE_SERVICE_NAME)
            with Proxy(namenode_uri) as namenode:
                namenode.registrar_datanode(uri)
            print("[DataNode2] Registrado com sucesso no NameNode.")
        except Exception as e:
            print(f"[DataNode2] Erro ao registrar no NameNode: {e}")

        HeartbeatSender(uri).start()

        # Loop do servidor
        print("[DataNode2] Aguardando requisições...")
        daemon.requestLoop()

    except Exception as e:
        print(f"[DataNode2] Falha na inicialização: {e}")

if __name__ == "__main__":
    main()
