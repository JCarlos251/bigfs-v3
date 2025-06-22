import os
from Pyro5.api import expose, Daemon, locate_ns

@expose
class DataNode:
    def __init__(self, storage_dir):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def salvar_arquivo(self, nome_arquivo, dados_bytes):
        return

    def delete_arquivo(self, nome_arquivo):
        return

def main():
    storage_dir = "servidor/datanode1"
    datanode = DataNode(storage_dir)
    daemon = Daemon()
    ns = locate_ns()
    uri = daemon.register(datanode)
    ns.register("filesystem.datanode1", uri)

    # Registrar no Namenode
    try:
        namenode_uri = ns.lookup("filesystem.namenode")
        from Pyro5.api import Proxy
        with Proxy(namenode_uri) as namenode:
            namenode.registrar_datanode(uri)
    except Exception as e:
        print(f"Erro ao registrar no namenode: {e}")

    print("Datanode 1 rodando...")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
