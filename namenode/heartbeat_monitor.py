# Verifica DataNodes ativos (heartbeat + timeout)

import threading
import time
from core.config import HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT

class HeartbeatMonitor(threading.Thread):
    def __init__(self, namenode):
        super().__init__(daemon=True)
        self.namenode = namenode

    def run(self):
        while True:
            try:
                time.sleep(HEARTBEAT_INTERVAL)
                agora = time.time()

                with self.namenode.lock:
                    try:
                        ativos_antes = len(self.namenode.datanodes_ativos)
                        inativos = [
                            uri for uri, ts in self.namenode.datanodes_ativos.items()
                            if agora - ts > HEARTBEAT_TIMEOUT
                        ]

                        for uri in inativos:
                            print(f"[Heartbeat] DataNode inativo detectado: {uri}")
                            del self.namenode.datanodes_ativos[uri]
                            self._remover_uri_dos_metadados(str(uri))

                        ativos_depois = len(self.namenode.datanodes_ativos)
                        if ativos_antes != ativos_depois:
                            print(f"[Heartbeat] DataNodes ativos atualizados: {ativos_depois}")

                    except Exception as e:
                        print(f"[Heartbeat] Erro ao processar datanodes ativos: {e}")

            except Exception as e:
                print(f"[Heartbeat] Erro no loop de heartbeat: {e}")

    def _remover_uri_dos_metadados(self, uri_removido):
        alteracoes = 0
        try:
            with self.namenode.metadados.lock:
                for nome_arquivo, chunks in self.namenode.metadados.metadados.items():
                    for chunk, uris in chunks.items():
                        if uri_removido in uris:
                            chunks[chunk] = [u for u in uris if u != uri_removido]
                            alteracoes += 1
                            print(f"[Heartbeat] URI {uri_removido} removida de {chunk} ({nome_arquivo})")

                if alteracoes > 0:
                    self.namenode.metadados._salvar_em_disco()
        except Exception as e:
            print(f"[Heartbeat] Erro ao remover URI dos metadados: {e}")
