# Funções simples: leitura de arquivo local, checksum

import os
import hashlib

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
    print("  upload <arquivo_local>                Envia arquivo ao sistema")
    print("  download <arquivo_remoto>             Baixa arquivo do sistema")
    print("  delete <arquivo_remoto>               Remove arquivo do sistema")
    print("  clear                                 Limpar terminal")
    print("  exit                                  Encerra o cliente")

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')