# Divide e reconstrói arquivos (10MB), controla replicação

import random
from core.config import CHUNK_SIZE

class ChunkManager:
    def __init__(self):
        pass

    def dividir_em_chunks(self, arquivo_bytes):
        """
        Divide um arquivo (em bytes) em partes de tamanho CHUNK_SIZE.
        Retorna uma lista de bytes dos chunks.
        """
        chunks = []
        for i in range(0, len(arquivo_bytes), CHUNK_SIZE):
            chunk = arquivo_bytes[i:i + CHUNK_SIZE]
            chunks.append(chunk)
        return chunks

    def gerar_nomes_chunks(self, nome_arquivo_base, total_chunks):
        """
        Gera nomes como 'relatorio_chunk1', 'relatorio_chunk2'
        """
        return [f"{nome_arquivo_base}_chunk{i+1}" for i in range(total_chunks)]

    def sortear_datanodes_para_chunk(self, datanodes_vivos, replicacao):
        """
        Retorna uma lista de URIs de datanodes escolhidos aleatoriamente.
        """
        if len(datanodes_vivos) < replicacao:
            raise Exception("Datanodes vivos insuficientes para replicação")

        return random.sample(datanodes_vivos, replicacao)
