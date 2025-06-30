import threading
import time
import random
from Pyro5.api import Proxy
from core.config import REPLICATION_FACTOR

class Replicador2(threading.Thread):
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
                print(f"[Replicador2] Erro durante replicação: {e}")
            time.sleep(self.intervalo)

    def replicar_chunks(self):
        arquivos = self.namenode.metadados.listar_arquivos()
        datanodes_vivos = [str(uri) for uri in self.namenode.obter_datanodes_vivos()]

        for arquivo in arquivos:
            chunks = self.namenode.metadados.obter_chunks_do_arquivo(arquivo)
            atualizado = False

            for chunk_name, uris_existentes in chunks.items():
                # Converte para strings para comparação segura
                uris_existentes = [str(u) for u in uris_existentes]

                if len(uris_existentes) >= REPLICATION_FACTOR:
                    continue

                # Remove os datanodes que já têm o chunk
                candidatos = list(set(datanodes_vivos) - set(uris_existentes))
                faltam = REPLICATION_FACTOR - len(uris_existentes)

                # Sem origem ativa? Pula o chunk
                origens_possiveis = [u for u in uris_existentes if u in datanodes_vivos]
                if not origens_possiveis:
                    print(f"[Replicador2] Nenhuma origem ativa para {chunk_name}")
                    continue

                origem_uri = origens_possiveis[0]
                random.shuffle(candidatos)  # Balanceamento

                # Debug temporário
                print(f"[Replicador2] Chunk: {chunk_name} | Origem: {origem_uri} | Candidatos: {candidatos}")

                novos_uris = []

                try:
                    with Proxy(origem_uri) as origem:
                        dados, checksum = origem.ler_arquivo(chunk_name)

                    for uri_destino in candidatos[:faltam]:
                        try:
                            with Proxy(uri_destino) as destino:
                                destino.salvar_arquivo(chunk_name, dados, checksum)
                            novos_uris.append(str(uri_destino))
                            print(f"[Replicador2] Replicado {chunk_name} de {origem_uri} para {uri_destino}")
                        except Exception as e:
                            print(f"[Replicador2] Falha ao replicar {chunk_name} para {uri_destino}: {e}")
                except Exception as e:
                    print(f"[Replicador2] Falha ao ler chunk {chunk_name} de {origem_uri}: {e}")
                    continue

                if novos_uris:
                    chunks[chunk_name] = list(set(uris_existentes + novos_uris))
                    atualizado = True

            if atualizado:
                # Garante que tudo seja serializável
                chunks_serializaveis = {
                    chunk: [str(uri) for uri in uris]
                    for chunk, uris in chunks.items()
                }
                self.namenode.metadados.salvar_metadado(arquivo, chunks_serializaveis)
