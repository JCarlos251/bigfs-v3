# Serviço que mantém fator de replicação fixo (3)

import threading
import time
from core.config import REPLICATION_FACTOR
from datanode.storage_utils import calcular_checksum
from Pyro5.api import Proxy

class Replicador(threading.Thread):
    def __init__(self, namenode, intervalo=5):
        super().__init__(daemon=True)
        self.namenode = namenode
        self.intervalo = intervalo  #  5 segundos

    def run(self):
        while True:
            time.sleep(self.intervalo)

            with self.namenode.lock:
                arquivos = self.namenode.metadados.metadados.copy()

            for arquivo, chunks in arquivos.items():
                for chunk_name, datanodes_existentes in chunks.items():
                    try:
                        vivos = self.namenode.obter_datanodes_vivos()

                        faltando = REPLICATION_FACTOR - len(datanodes_existentes)
                        '''if faltando <= 0:
                            continue  # Já está com o número correto de réplicas'''

                        # Calcular diferença de replicação
                        diff = REPLICATION_FACTOR - len(datanodes_existentes)

                        if diff == 0:
                            continue  # Nada a fazer

                        elif diff > 0:
                            # ========== REPLICA ==========
                            # Encontrar DataNodes disponíveis que ainda não têm o chunk
                            candidatos = [uri for uri in vivos if uri not in datanodes_existentes]
                            if len(candidatos) < faltando:
                                print(f"[Replicador] Não há DataNodes suficientes para replicar {chunk_name}")
                                continue

                            origem_uri = datanodes_existentes[0]  # qualquer dos existentes
                            with Proxy(origem_uri) as origem_dn:
                                dados, checksum = origem_dn.ler_arquivo(chunk_name)

                            novos_datanodes = candidatos[:faltando]
                            for destino_uri in novos_datanodes:
                                try:
                                    with Proxy(destino_uri) as destino_dn:
                                        destino_dn.salvar_arquivo(chunk_name, dados, checksum)
                                    datanodes_existentes.append(destino_uri)
                                    print(f"[Replicador] Chunk {chunk_name} replicado para {destino_uri}")
                                except Exception as e:
                                    print(f"[Replicador] Falha ao replicar {chunk_name} para {destino_uri}: {e}")

                        elif diff < 0:
                            # ========== REMOVE EXCEDENTES ==========
                            excedentes = datanodes_existentes[REPLICATION_FACTOR:]  # Ex: [dn4, dn5]
                            for dn_uri in excedentes:
                                try:
                                    with Proxy(dn_uri) as dn:
                                        dn.delete_arquivo(chunk_name)
                                    print(f"[Replicador] Réplica excedente de {chunk_name} removida de {dn_uri}")
                                except Exception as e:
                                    print(f"[Replicador] Falha ao remover réplica excedente {chunk_name} de {dn_uri}: {e}")

                            datanodes_existentes = datanodes_existentes[:REPLICATION_FACTOR]

                        # Atualizar metadados
                        with self.namenode.lock:
                            self.namenode.metadados.metadados[arquivo][chunk_name] = datanodes_existentes
                            self.namenode.metadados._salvar_em_disco()

                    except Exception as e:
                        print(f"[Replicador] Erro ao verificar chunk {chunk_name}: {e}")
