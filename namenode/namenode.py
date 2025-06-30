# Coordena todas as operações: escrita, leitura, deleção

import threading
import time
import os
from Pyro5.api import expose, config
from core.config import REPLICATION_FACTOR, HEARTBEAT_TIMEOUT
from namenode.metadados import Metadados
from namenode.chunk_manager import ChunkManager
from namenode.heartbeat_monitor import HeartbeatMonitor
from namenode.replicador import Replicador
from datanode.storage_utils import calcular_checksum
from Pyro5.api import Proxy

from namenode.replicador2 import Replicador2

config.SERIALIZER = "msgpack"


import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from Pyro5.api import Proxy

@expose
class NameNode:
    def __init__(self):
        self.lock = threading.Lock()
        self.datanodes_ativos = {}  # {uri: timestamp_ultimo_heartbeat}
        self.metadados = Metadados()
        self.chunk_manager = ChunkManager()
        self.heartbeat_monitor = HeartbeatMonitor(self)
        self.heartbeat_monitor.start()
        # self.replicador = Replicador(self)
        # self.replicador.start()

        self.replicador = Replicador2(self)
        self.replicador.start()

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
        print(self.datanodes_ativos)
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

    def localizar_datanodes_do_arquivo(self, nome_arquivo):
        return self.metadados.obter_chunks_do_arquivo(nome_arquivo)

    def delete_arquivo(self, nome_arquivo):
        chunks = self.metadados.obter_chunks_do_arquivo(nome_arquivo)
        if not chunks:
            raise Exception("Arquivo não encontrado.")

        from Pyro5.api import Proxy
        for chunk, datanodes in chunks.items():
            for dn_uri in datanodes:
                try:
                    with Proxy(dn_uri) as datanode:
                        datanode.delete_arquivo(chunk)
                except Exception as e:
                    print(f"[NameNode] Falha ao deletar {chunk} de {dn_uri}: {e}")

        self.metadados.remover_arquivo(nome_arquivo)
        print(f"[NameNode] Metadados removidos para '{nome_arquivo}'")
        return True


    def receber_bloco(self, nome_arquivo, bloco_bytes, checksum_cliente):
        """
        Recebe blocos de 64KB enviados pelo cliente.
        Cada bloco é validado e gravado sequencialmente no disco.
        """
        from datanode.storage_utils import calcular_checksum

        if calcular_checksum(bloco_bytes) != checksum_cliente:
            raise ValueError("Checksum inválido no bloco recebido")

        os.makedirs("tmp_uploads", exist_ok=True)
        caminho = os.path.join("tmp_uploads", nome_arquivo)

        with open(caminho, "ab") as f:
            f.write(bloco_bytes)

    
    def processar_arquivo_upload(self, nome_arquivo):
        """
        Após receber todos os blocos, divide o arquivo em chunks, envia aos datanodes
        e atualiza os metadados.
        """

        caminho_temp = os.path.join("tmp_uploads", nome_arquivo)

        if not os.path.exists(caminho_temp):
            print("[NameNode] Arquivo temporário não encontrado.")
            return False

        try:
            with open(caminho_temp, "rb") as f:
                dados = f.read()

            # checksum = calcular_checksum(dados)

            chunks_bytes = self.chunk_manager.dividir_em_chunks(dados)
            nomes_chunks = self.chunk_manager.gerar_nomes_chunks(nome_arquivo, len(chunks_bytes))   

            datanodes_vivos = self.obter_datanodes_vivos()

            if not datanodes_vivos:
                print("[NameNode] Nenhum DataNode disponível.")
                return False
            
            chunks_datanodes = {}

             # Envia cada chunk para um datanode diferente (ou em round-robin)
            for i, chunk_data in enumerate(chunks_bytes):
                chunk_name = nomes_chunks[i]
                checksum = calcular_checksum(chunk_data)

                # Escolhe um datanode round-robin 
                uri_datanode = datanodes_vivos[i % len(datanodes_vivos)]

                try:
                    with Proxy(uri_datanode) as datanode:
                        datanode.salvar_arquivo(chunk_name, chunk_data, checksum)
                    chunks_datanodes[chunk_name] = [str(uri_datanode)]
                except Exception as e:
                    print(f"[NameNode] Falha ao enviar {chunk_name} para {uri_datanode}: {e}")
            
            # Salva os metadados do arquivo (nome do arquivo original → mapeamento de chunks)
            self.metadados.salvar_metadado(nome_arquivo, chunks_datanodes)

            # Remove o arquivo temporário
            os.remove(caminho_temp)
            print(f"[NameNode] Upload finalizado e metadados atualizados para '{nome_arquivo}'.")

            return True

        except Exception as e:
            print(f"[NameNode] Erro ao processar upload: {e}")
            return False


    

    def reconstruir_arquivo_para_download(self, nome_arquivo):
        chunks_info = self.metadados.obter_chunks_do_arquivo(nome_arquivo)
        if not chunks_info:
            raise Exception("Arquivo não encontrado.")

        os.makedirs("tmp_downloads", exist_ok=True)
        caminho_saida = os.path.join("tmp_downloads", nome_arquivo)

        def baixar_chunk(chunk_name, datanodes):
            for dn_uri in datanodes:
                try:
                    with Proxy(dn_uri) as datanode:
                        dados, checksum = datanode.ler_arquivo(chunk_name)
                        if calcular_checksum(dados) != checksum:
                            print(f"[NameNode] Checksum inválido do chunk {chunk_name} de {dn_uri}")
                            continue
                        print(f"[NameNode] Chunk {chunk_name} baixado de {dn_uri}")
                        return chunk_name, dados
                except Exception as e:
                    print(f"[NameNode] Falha ao baixar chunk {chunk_name} de {dn_uri}: {e}")
            raise Exception(f"Falha em todos os DataNodes para o chunk {chunk_name}")

        resultados = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            futuros = [executor.submit(baixar_chunk, chunk_name, datanodes)
                    for chunk_name, datanodes in chunks_info.items()]

            for futuro in as_completed(futuros):
                chunk_name, dados = futuro.result()
                resultados[chunk_name] = dados

        # Ordena os chunks pelo nome para escrever em sequência
        with open(caminho_saida, "wb") as f_saida:
            for chunk_name in sorted(resultados.keys()):
                f_saida.write(resultados[chunk_name])

        print(f"[NameNode] Arquivo {nome_arquivo} reconstruído com sucesso em {caminho_saida}")
        return True

    '''
    def reconstruir_arquivo_para_download(self, nome_arquivo):
        """
        Reagrupa os chunks de um arquivo a partir dos DataNodes,
        salva o arquivo completo em tmp_downloads/ e retorna True/False.
        """
        chunks_info = self.metadados.obter_chunks_do_arquivo(nome_arquivo)
        if not chunks_info:
            raise Exception("Arquivo não encontrado.")

        os.makedirs("tmp_downloads", exist_ok=True)
        caminho_saida = os.path.join("tmp_downloads", nome_arquivo)

        with open(caminho_saida, "wb") as f_saida:
            for chunk_name in sorted(chunks_info.keys()):
                datanodes = chunks_info[chunk_name]
                sucesso = False

                # tenta no primeiro datanode da lista, se não for possível, tentará o próximo
                for dn_uri in datanodes:
                    try:
                        with Proxy(dn_uri) as datanode:
                            dados, checksum = datanode.ler_arquivo(chunk_name)
                            if calcular_checksum(dados) != checksum:
                                print(f"[NameNode] Checksum inválido do chunk {chunk_name} de {dn_uri}")
                                continue
                            f_saida.write(dados)
                            sucesso = True
                            break
                    except Exception as e:
                        print(f"[NameNode] Falha ao baixar chunk {chunk_name} de {dn_uri}: {e}")
                if not sucesso:
                    raise Exception(f"Falha em todos os DataNodes para o chunk {chunk_name}")

        return True
        '''

    def enviar_arquivo_em_blocos(self, nome_arquivo):
        """
        Generator: Envia o arquivo reconstruído em blocos de 64KB com checksum.
        """
        caminho = os.path.join("tmp_downloads", nome_arquivo)
        if not os.path.exists(caminho):
            raise FileNotFoundError("Arquivo temporário de download não encontrado.")

        with open(caminho, "rb") as f:
            while True:
                bloco = f.read(64 * 1024)
                if not bloco:
                    break
                from datanode.storage_utils import calcular_checksum
                checksum = calcular_checksum(bloco)
                yield bloco, checksum

    def finalizar_download(self, nome_arquivo):
        """
        Remove o arquivo temporário de download.
        """
        caminho = os.path.join("tmp_downloads", nome_arquivo)
        if os.path.exists(caminho):
            os.remove(caminho)
