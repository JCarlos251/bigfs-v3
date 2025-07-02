import threading
import time
import random
from Pyro5.api import Proxy
from core.config import REPLICATION_FACTOR

class Replicador(threading.Thread):
    def __init__(self, namenode, intervalo=10):
        super().__init__()
        self.namenode = namenode
        self.intervalo = intervalo
        self.daemon = True  # Finaliza com o processo principal

    def run(self):
        while True:
            try:
                self.replicar_chunks()
            except Exception as e:
                print(f"[Replicador] Erro durante replicação: {e}")
            time.sleep(self.intervalo)

    def replicar_chunks(self):
        try:
            arquivos = self.namenode.metadados.listar_arquivos()
            datanodes_vivos = [str(uri) for uri in self.namenode.obter_datanodes_vivos()]
        except Exception as e:
            print(f"[Replicador] Falha ao obter arquivos ou datanodes vivos: {e}")
            return

        for arquivo in arquivos:
            try:
                chunks = self.namenode.metadados.obter_chunks_do_arquivo(arquivo)
            except Exception as e:
                print(f"[Replicador] Falha ao obter chunks do arquivo '{arquivo}': {e}")
                continue

            atualizado = False

            for chunk_name, uris_existentes in chunks.items():
                try:
                    uris_existentes = [str(u) for u in uris_existentes]
                    uris_existentes = [u for u in uris_existentes if u in datanodes_vivos]

                    # === [1] Corrige excesso de réplicas ===
                    if len(uris_existentes) > REPLICATION_FACTOR:
                        excedentes = uris_existentes[REPLICATION_FACTOR:]
                        for uri in excedentes:
                            try:
                                with Proxy(uri) as datanode:
                                    datanode.delete_arquivo(chunk_name)
                                print(f"[Replicador] Réplica excedente {chunk_name} removida de {uri}")
                            except Exception as e:
                                print(f"[Replicador] Falha ao remover réplica excedente de {uri}: {e}")
                        uris_existentes = uris_existentes[:REPLICATION_FACTOR]
                        chunks[chunk_name] = uris_existentes
                        atualizado = True

                    # === [2] Corrige falta de réplicas ===
                    elif len(uris_existentes) < REPLICATION_FACTOR:
                        faltam = REPLICATION_FACTOR - len(uris_existentes)
                        candidatos = list(set(datanodes_vivos) - set(uris_existentes))
                        origens_possiveis = [u for u in uris_existentes if u in datanodes_vivos]

                        if not origens_possiveis:
                            print(f"[Replicador] Nenhuma origem ativa para {chunk_name}")
                            continue

                        origem_uri = origens_possiveis[0]
                        random.shuffle(candidatos)

                        try:
                            with Proxy(origem_uri) as origem:
                                dados, checksum = origem.ler_arquivo(chunk_name)
                        except Exception as e:
                            print(f"[Replicador] Falha ao ler chunk {chunk_name} de {origem_uri}: {e}")
                            continue

                        novos_uris = []
                        for uri_destino in candidatos[:faltam]:
                            try:
                                with Proxy(uri_destino) as destino:
                                    destino.salvar_arquivo(chunk_name, dados, checksum)
                                novos_uris.append(str(uri_destino))
                                print(f"[Replicador] Replicado {chunk_name} de {origem_uri} para {uri_destino}")
                            except Exception as e:
                                print(f"[Replicador] Falha ao replicar {chunk_name} para {uri_destino}: {e}")

                        if novos_uris:
                            uris_existentes += novos_uris
                            chunks[chunk_name] = uris_existentes
                            atualizado = True

                except Exception as e:
                    print(f"[Replicador] Erro ao processar chunk '{chunk_name}' do arquivo '{arquivo}': {e}")
                    continue

            if atualizado:
                try:
                    chunks_serializaveis = {
                        chunk: [str(uri) for uri in uris]
                        for chunk, uris in chunks.items()
                    }
                    self.namenode.metadados.salvar_metadado(arquivo, chunks_serializaveis)
                except Exception as e:
                    print(f"[Replicador] Falha ao salvar metadados para '{arquivo}': {e}")
