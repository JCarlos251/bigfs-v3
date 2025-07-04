import os
from Pyro5.api import locate_ns, Proxy, config
from core.constants import NAMENODE_SERVICE_NAME
from cliente.utils import calcular_checksum, ajuda, limpar_terminal

config.SERIALIZER = "msgpack"

class Cliente:
    def __init__(self):
        self.namenode = None

    def conectar_namenode(self):
        try:
            ns = locate_ns()
            uri_namenode = ns.lookup(NAMENODE_SERVICE_NAME)
            self.namenode = Proxy(uri_namenode)
        except Exception as e:
            print(f"[Cliente] Erro ao conectar ao NameNode: {e}")
            raise

    def iniciar(self):
        try:
            self.conectar_namenode()
        except Exception:
            print("[Cliente] Não foi possível iniciar por falha na conexão com o NameNode.")
            return

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
                self.listar_arquivos()

            elif comando.startswith("upload "):
                self.upload(comando)

            elif comando.startswith("download"):
                self.download(comando)

            elif comando.startswith("delete "):
                self.deletar(comando)

            else:
                print("Comando desconhecido. Digite 'help'.")

    def listar_arquivos(self):
        try:
            arquivos = self.namenode.listar_arquivos()
            if arquivos:
                print("Arquivos disponíveis:")
                for f in arquivos:
                    print(f" - {f}")
            else:
                print("Nenhum arquivo encontrado.")
        except Exception as e:
            print(f"[Cliente] Erro ao listar arquivos: {e}")

    def upload(self, comando):
        partes = comando.split()
        if len(partes) < 2:
            print("Uso: upload <arquivo_local> [nome_remoto]")
            return

        caminho_local = partes[1]
        nome_remoto = os.path.basename(caminho_local)

        try:
            arquivos_existentes = self.namenode.listar_arquivos()
            if nome_remoto in arquivos_existentes:
                print("Já existe um arquivo com esse nome, renomeie seu arquivo ou delete o atual para fazer o upload novamente.")
                return

            with open(caminho_local, "rb") as f:
                print(f"[Cliente] Enviando '{nome_remoto}' para o NameNode em blocos de 64KB...")
                while True:
                    # envia blocos de 60 KB + checksum
                    bloco = f.read(60 * 1024)
                    if not bloco:
                        break
                    checksum = calcular_checksum(bloco)
                    self.namenode.receber_bloco(nome_remoto, bloco, checksum)

            sucesso = self.namenode.processar_arquivo_upload(nome_remoto)
            if sucesso:
                print(f"[Cliente] Upload de '{nome_remoto}' concluído com sucesso.")
            else:
                print("[Cliente] Falha ao processar upload no NameNode.")
        except FileNotFoundError:
            print(f"[Cliente] Arquivo local '{caminho_local}' não encontrado.")
        except Exception as e:
            print(f"[Cliente] Erro durante upload: {e}")

    def download(self, comando):
        partes = comando.split()
        if len(partes) < 2:
            print("Uso: download <arquivo_remoto>")
            return

        nome_remoto = partes[1]
        pasta_destino = os.path.join("cliente/arquivos_download_cliente")
        os.makedirs(pasta_destino, exist_ok=True)
        destino_local = os.path.join(pasta_destino, os.path.basename(partes[2]) if len(partes) > 2 else nome_remoto)

        try:
            print(f"[Cliente] Solicitando reconstrução do arquivo '{nome_remoto}' ao NameNode...")
            sucesso = self.namenode.reconstruir_arquivo_para_download(nome_remoto)
            if not sucesso:
                print("[Cliente] Falha na reconstrução do arquivo.")
                return

            print("[Cliente] Recebendo arquivo em blocos de 64KB...")
            with open(destino_local, "wb") as f_out:
                for bloco, checksum in self.namenode.enviar_arquivo_em_blocos(nome_remoto):
                    if calcular_checksum(bloco) != checksum:
                        print("[Cliente] Checksum inválido em um dos blocos. Abortando.")
                        f_out.close()
                        os.remove(destino_local)
                        return
                    f_out.write(bloco)

            self.namenode.finalizar_download(nome_remoto)
            print(f"[Cliente] Download completo: {destino_local}")

        except Exception as e:
            print(f"[Cliente] Erro no download: {e}")

    def deletar(self, comando):
        partes = comando.split()
        if len(partes) < 2:
            print("Uso: delete <arquivo_remoto>")
            return

        nome_remoto = partes[1]
        try:
            confirmacao = input(f"Tem certeza que deseja deletar '{nome_remoto}'? (s/n): ")
            if confirmacao.lower() != "s":
                print("Operação cancelada.")
                return

            sucesso = self.namenode.delete_arquivo(nome_remoto)
            if sucesso:
                print(f"[Cliente] Arquivo '{nome_remoto}' deletado com sucesso.")
            else:
                print("[Cliente] Falha ao deletar o arquivo.")

        except Exception as e:
            print(f"[Cliente] Erro ao tentar deletar: {e}")


if __name__ == "__main__":
    cliente = Cliente()
    cliente.iniciar()
