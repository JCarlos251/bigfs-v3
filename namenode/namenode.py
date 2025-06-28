# Coordena todas as operações: escrita, leitura, deleção

import threading
import time
from Pyro5.api import expose

from core.config import REPLICATION_FACTOR, HEARTBEAT_TIMEOUT
from core.constants import DATANODE_SERVICE_PREFIX
from namenode.metadados import Metadados
from namenode.chunk_manager import ChunkManager

@expose
class NameNode:
    def __init__(self):
        self.lock = threading.Lock()
        self.datanodes_ativos = {}  # {uri: timestamp_ultimo_heartbeat}
        self.metadados = Metadados()
        self.chunk_manager = ChunkManager()

    # ---------------------------
    # Registro e Heartbeat
    # ---------------------------

    def registrar_datanode(self, datanode_uri):
        with self.lock:
            self.datanodes_ativos[datanode_uri] = time.time()
            print(f"[NameNode] DataNode registrado: {datanode_uri}")
            return True

    def heartbeat(self, datanode_uri):
        with self.lock:
            self.datanodes_ativos[datanode_uri] = time.time()

    def obter_datanodes_vivos(self):
        agora = time.time()
        with self.lock:
            return [uri for uri, ts in self.datanodes_ativos.items()
                    if agora - ts < HEARTBEAT_TIMEOUT]

    # ---------------------------
    # Operações principais
    # ---------------------------

    def listar_arquivos(self):
        return self.metadados.listar_arquivos()

    def solicitar_datanodes_para_escrita(self, num_chunks):
        vivos = self.obter_datanodes_vivos()
        if len(vivos) < REPLICATION_FACTOR:
            raise Exception("Não há datanodes suficientes vivos")

        # Define quais datanodes serão usados para cada chunk
        chunks_datanodes = []
        for _ in range(num_chunks):
            escolhidos = self.chunk_manager.sortear_datanodes_para_chunk(vivos, REPLICATION_FACTOR)
            chunks_datanodes.append(escolhidos)
        return chunks_datanodes

    def registrar_chunks_arquivo(self, nome_arquivo, chunks_mapeados):
        # Exemplo: chunks_mapeados = {chunk1: [dn1, dn2, dn3], chunk2: [...]}
        self.metadados.salvar_metadado(nome_arquivo, chunks_mapeados)

    def localizar_datanodes_do_arquivo(self, nome_arquivo):
        return self.metadados.obter_chunks_do_arquivo(nome_arquivo)

    def delete_arquivo(self, nome_arquivo):
        chunks = self.metadados.obter_chunks_do_arquivo(nome_arquivo)
        if not chunks:
            raise Exception("Arquivo não encontrado")

        from Pyro5.api import Proxy
        for chunk, datanodes in chunks.items():
            for dn_uri in datanodes:
                try:
                    with Proxy(dn_uri) as datanode:
                        datanode.delete_arquivo(chunk)
                except Exception as e:
                    print(f"[WARN] Falha ao deletar {chunk} de {dn_uri}: {e}")

        self.metadados.remover_arquivo(nome_arquivo)
        return True
