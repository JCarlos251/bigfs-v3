# Gerencia estrutura de metadados (dicionário em memória e persistência no disco)

import json
import os
from threading import Lock

METADADOS_PATH = "namenode_db.json"  # Local onde o dicionário será persistido

class Metadados:
    def __init__(self):
        self.metadados = {}
        self.lock = Lock()
        self._carregar_de_disco()

    def _carregar_de_disco(self):
        if os.path.exists(METADADOS_PATH):
            try:
                with open(METADADOS_PATH, "r") as f:
                    self.metadados = json.load(f)
                    print(f"[Metadados] Metadados carregados com sucesso.")
            except Exception as e:
                print(f"[Metadados] Falha ao carregar metadados: {e}")

    def _salvar_em_disco(self):
        try:
            with open(METADADOS_PATH, "w") as f:
                json.dump(self.metadados, f, indent=4)
        except Exception as e:
            print(f"[Metadados] Erro ao salvar metadados: {e}")

    def salvar_metadado(self, nome_arquivo, chunks_datanodes):
        """
        chunks_datanodes = {
            "relatorio_chunk1": ["dn1", "dn2", "dn3"],
            "relatorio_chunk2": ["dn2", "dn3", "dn4"],
        }
        """
        with self.lock:
            self.metadados[nome_arquivo] = chunks_datanodes
            self._salvar_em_disco()

    def obter_chunks_do_arquivo(self, nome_arquivo):
        with self.lock:
            return self.metadados.get(nome_arquivo, None)

    def remover_arquivo(self, nome_arquivo):
        with self.lock:
            if nome_arquivo in self.metadados:
                del self.metadados[nome_arquivo]
                self._salvar_em_disco()

    def listar_arquivos(self):
        with self.lock:
            return list(self.metadados.keys())
