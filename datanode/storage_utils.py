# Leitura/escrita segura em disco

import os
import hashlib

def salvar_chunk(diretorio, nome_chunk, dados):
    """
    Salva um chunk como arquivo binário no disco.
    """
    caminho = os.path.join(diretorio, nome_chunk)
    with open(caminho, "wb") as f:
        f.write(dados)

def carregar_chunk(diretorio, nome_chunk):
    """
    Carrega os dados binários de um chunk salvo em disco.
    """
    caminho = os.path.join(diretorio, nome_chunk)
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Chunk não encontrado: {nome_chunk}")
    with open(caminho, "rb") as f:
        return f.read()

def deletar_chunk(diretorio, nome_chunk):
    """
    Deleta o arquivo de chunk, se existir.
    """
    caminho = os.path.join(diretorio, nome_chunk)
    if os.path.exists(caminho):
        os.remove(caminho)

def calcular_checksum(dados):
    """
    Calcula o checksum SHA-256 dos dados fornecidos.
    """
    sha = hashlib.sha256()
    sha.update(dados)
    return sha.hexdigest()
