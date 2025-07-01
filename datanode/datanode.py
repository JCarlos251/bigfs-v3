# Classe com salvar/deletar chunk, validar checksum

import os
from Pyro5.api import expose
from datanode.storage_utils import salvar_chunk, deletar_chunk, carregar_chunk, calcular_checksum
import threading
import time
from core.constants import NAMENODE_SERVICE_NAME
from core.config import HEARTBEAT_INTERVAL
from core.network import get_nameserver
from Pyro5.api import Proxy, config

config.SERIALIZER = "msgpack"

@expose
class DataNode:
    def __init__(self, storage_dir):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

        # Limpa todos os chunks ao iniciar
        self.limpar_todos_os_chunks()
        print(f"[DataNode] Diretório limpo: {self.storage_dir}")

    def salvar_arquivo(self, nome_chunk, dados_bytes, checksum_esperado):
        """
        Salva o chunk em disco e valida o checksum.
        """
        checksum_calculado = calcular_checksum(dados_bytes)

        if checksum_calculado != checksum_esperado:
            raise ValueError(f"Checksum inválido para {nome_chunk}")

        salvar_chunk(self.storage_dir, nome_chunk, dados_bytes)
        print(f"[DataNode] Chunk salvo com sucesso: {nome_chunk}")
        return True

    def delete_arquivo(self, nome_chunk):
        """
        Remove um chunk do armazenamento local.
        """
        deletar_chunk(self.storage_dir, nome_chunk)
        print(f"[DataNode] Chunk deletado: {nome_chunk}")
        return True

    def ler_arquivo(self, nome_chunk):
        """
        Lê um chunk e retorna seus dados e checksum para validação no cliente.
        """
        dados = carregar_chunk(self.storage_dir, nome_chunk)
        checksum = calcular_checksum(dados)
        return dados, checksum
    
    def limpar_todos_os_chunks(self):
        arquivos = os.listdir(self.storage_dir)
        for nome in arquivos:
            caminho = os.path.join(self.storage_dir, nome)
            try:
                os.remove(caminho)
                print(f"[DataNode] Chunk removido: {caminho}")
            except Exception as e:
                print(f"[DataNode] Erro ao remover {caminho}: {e}")

class HeartbeatSender(threading.Thread):
    def __init__(self, datanode_uri):
        super().__init__(daemon=True)
        self.datanode_uri = datanode_uri

    def run(self):
        try:
            ns = get_nameserver()
            namenode_uri = ns.lookup(NAMENODE_SERVICE_NAME)

            while True:
                time.sleep(HEARTBEAT_INTERVAL)
                try:
                    with Proxy(namenode_uri) as namenode:
                        namenode.heartbeat(str(self.datanode_uri))
                        print(f"[HeartbeatSender] Heartbeat enviado para {namenode_uri}")
                except Exception as e:
                    print(f"[HeartbeatSender] Falha ao enviar heartbeat: {e}")

        except Exception as e:
            print(f"[HeartbeatSender] Erro ao iniciar envio de heartbeat: {e}")