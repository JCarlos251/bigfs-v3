 # CLI simples: upload/download/list/delete
# cliente/main.py

import os
from Pyro5.api import locate_ns, Proxy, config
from core.constants import NAMENODE_SERVICE_NAME
from cliente.utils import calcular_checksum, ajuda, limpar_terminal

config.SERIALIZER = "msgpack"

def main():
    ns = locate_ns()
    uri_namenode = ns.lookup(NAMENODE_SERVICE_NAME)
    namenode = Proxy(uri_namenode)

    print("=== BigFS - Sistema de Arquivos Distribuído ===")
    print("Digite 'help' para ver os comandos disponíveis.")

    while True:
        try:
            comando = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando cliente.")
            break

        if comando == "exit":
            break

        elif comando == "help":
            ajuda()

        elif comando == "clear":
            limpar_terminal()

        elif comando == "ls":
            arquivos = namenode.listar_arquivos()
            if arquivos:
                print("Arquivos disponíveis:")
                for f in arquivos:
                    print(f" - {f}")
            else:
                print("Nenhum arquivo encontrado.")

        elif comando.startswith("upload "):
            partes = comando.split()
            if len(partes) < 2:
                print("Uso: upload <arquivo_local> [nome_remoto]")
                continue

            caminho_local = partes[1]
            nome_remoto = partes[2] if len(partes) > 2 else os.path.basename(caminho_local)

            try:
                with open(caminho_local, "rb") as f:
                    print(f"[Cliente] Enviando '{nome_remoto}' para o NameNode em blocos de 64KB...")
                    while True:
                        bloco = f.read(64 * 1024)
                        if not bloco:
                            break
                        checksum = calcular_checksum(bloco)
                        namenode.receber_bloco(nome_remoto, bloco, checksum)

                # Após enviar tudo, solicitar o processamento
                sucesso = namenode.processar_arquivo_upload(nome_remoto)
                if sucesso:
                    print(f"[Cliente] Upload de '{nome_remoto}' concluído com sucesso.")
                else:
                    print("[Cliente] Falha ao processar upload no NameNode.")

            except Exception as e:
                print(f"[Cliente] Erro durante upload: {e}")

        elif comando.startswith("download"):
            partes = comando.split()
            if len(partes) < 2:
                print("Uso: download <arquivo_remoto> [destino_local]")
                continue

            nome_remoto = partes[1]
            # destino_local = partes[2] if len(partes) > 2 else nome_remoto

            pasta_destino = os.path.join("cliente/arquivos_download_cliente")
            os.makedirs(pasta_destino, exist_ok=True)

            destino_local = os.path.join(pasta_destino, os.path.basename(partes[2]) if len(partes) > 2 else nome_remoto)


            try:
                print(f"[Cliente] Solicitando reconstrução do arquivo '{nome_remoto}' ao NameNode...")
                sucesso = namenode.reconstruir_arquivo_para_download(nome_remoto)
                if not sucesso:
                    print("[Cliente] Falha na reconstrução do arquivo.")
                    continue
                
                
                print("[Cliente] Recebendo arquivo em blocos de 64KB...")
                with open(destino_local, "wb") as f_out:
                    for bloco, checksum in namenode.enviar_arquivo_em_blocos(nome_remoto):
                        if calcular_checksum(bloco) != checksum:
                            print("[Cliente] Checksum inválido em um dos blocos. Abortando.")
                            f_out.close()
                            os.remove(destino_local)
                            break
                        f_out.write(bloco)

                namenode.finalizar_download(nome_remoto)
                print(f"[Cliente] Download completo: {destino_local}")

            except Exception as e:
                print(f"[Cliente] Erro no download: {e}")

        elif comando.startswith("delete "):
            partes = comando.split()
            if len(partes) < 2:
                print("Uso: delete <arquivo_remoto>")
                continue

            nome_remoto = partes[1]
            try:
                confirmacao = input(f"Tem certeza que deseja deletar '{nome_remoto}'? (s/n): ")
                if confirmacao.lower() != "s":
                    print("Operação cancelada.")
                    continue

                sucesso = namenode.delete_arquivo(nome_remoto)
                if sucesso:
                    print(f"[Cliente] Arquivo '{nome_remoto}' deletado com sucesso.")
                else:
                    print("[Cliente] Falha ao deletar o arquivo.")

            except Exception as e:
                print(f"[Cliente] Erro ao tentar deletar: {e}")


        else:
            print("Comando desconhecido. Digite 'help'.")

if __name__ == "__main__":
    main()
