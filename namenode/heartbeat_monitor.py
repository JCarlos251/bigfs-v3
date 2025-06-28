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
            time.sleep(HEARTBEAT_INTERVAL)
            agora = time.time()

            with self.namenode.lock:
                ativos_antes = len(self.namenode.datanodes_ativos)
                inativos = [uri for uri, ts in self.namenode.datanodes_ativos.items()
                            if agora - ts > HEARTBEAT_TIMEOUT]

                for uri in inativos:
                    print(f"[Heartbeat] DataNode inativo detectado: {uri}")
                    del self.namenode.datanodes_ativos[uri]

                ativos_depois = len(self.namenode.datanodes_ativos)
                if ativos_antes != ativos_depois:
                    print(f"[Heartbeat] DataNodes ativos atualizados: {ativos_depois}")
