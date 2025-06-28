# Funções simples: leitura de arquivo local, checksum

import os
import hashlib

def ler_arquivo_local(caminho):
    """
    Lê um arquivo do disco local e retorna seu conteúdo em bytes.
    """
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    with open(caminho, "rb") as f:
        return f.read()

def salvar_arquivo_local(caminho, dados):
    """
    Salva os dados recebidos em disco local (modo binário).
    """
    with open(caminho, "wb") as f:
        f.write(dados)

def calcular_checksum(dados):
    """
    Calcula o checksum SHA-256 de dados binários.
    """
    sha = hashlib.sha256()
    sha.update(dados)
    return sha.hexdigest()
