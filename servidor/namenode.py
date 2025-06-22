import threading
from Pyro5.api import expose, Daemon, locate_ns, Proxy

@expose
class NameNode:
    def __init__(self):
        self.lock = threading.Lock()
        self.datanodes = set()  # URIs dos datanodes
        self.arquivos = {}      # {nome_arquivo: [datanode_uri, ...]}

    def registrar_datanode(self, datanode_uri):
        with self.lock:
            self.datanodes.add(datanode_uri)
            print(f"Datanode registrado: {datanode_uri}")
            return True

    def listar_arquivos(self):
        return

    def solicitar_datanodes_para_escrita(self):
        return

    def localizar_datanodes_do_arquivo(self):
        return

    def delete_arquivo(self):
        return

def main():
    daemon = Daemon()
    ns = locate_ns()
    namenode = NameNode()
    uri = daemon.register(namenode)
    ns.register("filesystem.namenode", uri)

    print("Namenode rodando...")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
