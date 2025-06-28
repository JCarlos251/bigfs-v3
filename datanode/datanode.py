# Classe com salvar/deletar chunk, validar checksum

import os
from Pyro5.api import expose
from datanode.storage_utils import salvar_chunk, deletar_chunk, carregar_chunk, calcular_checksum

@expose
class DataNode:
    def __init__(self, storage_dir):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

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
