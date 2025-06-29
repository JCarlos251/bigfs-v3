# CHUNK_SIZE, REPLICATION_FACTOR, PATHS

CHUNK_SIZE = 10 * 1024 * 1024  # 1 MB por chunk
REPLICATION_FACTOR = 3         # Número de cópias de cada chunk
HEARTBEAT_INTERVAL = 3         # Segundos entre cada heartbeat
HEARTBEAT_TIMEOUT = 600        # 10 minutos = 600 segundos