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

def ajuda():
    print("Comandos disponíveis:")
    print("  ls                                    Lista os arquivos no sistema")
    print("  upload <arquivo_local> [nome_remoto]  Envia arquivo ao sistema")
    print("  download <arquivo_remoto> [destino]   Baixa arquivo do sistema")
    print("  delete <arquivo_remoto>               Remove arquivo do sistema")
    print("  clear                                 Limpar terminal")
    print("  exit                                  Encerra o cliente")

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')