import os
from Pyro5.api import locate_ns, Proxy, config

#tt new-release

config.SERIALIZER = "msgpack"

def main():
    ns = locate_ns()
    uri_namenode = ns.lookup("filesystem.namenode")
    namenode = Proxy(uri_namenode)

    print("Shell - Sistema de Arquivos Distribuído (Arquivo inteiro)")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    while True:
        command = input(">>> ").strip()

        if command == "exit":
            break

        elif command == "help":
                print("Comandos disponíveis:")
                print("  ls                                     Lista os arquivos do servidor")
                print("  upload <arquivo_local> [destino_remoto]    Envia arquivo para o servidor")
                print("  download <arquivo_remoto> [destino_local]    Faz o download de um arquivo do servidor")
                print("  delete <arquivo_remoto>                Deleta um arquivo no servidor")
                print("  exit                                   Sai do shell")
                print("  help                                   Mostra este menu")

        elif command == "ls":
            arquivos = namenode.listar_arquivos()
            if arquivos:
                print("Arquivos no sistema:")
                for f in arquivos:
                    print(f" - {f}")
            else:
                print("Nenhum arquivo encontrado.")

        elif command.startswith("upload "):
            print("upload em construção")

        elif command.startswith("download"):
            print("download em construção")

        elif command.startswith("delete "):
            print("delete em construção")


        else:
            print("Comando desconhecido.")

if __name__ == "__main__":
    main()
