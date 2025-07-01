import unittest
from unittest.mock import MagicMock, patch, mock_open
from cliente.main_cliente import Cliente


class TestClienteFalhas(unittest.TestCase):
    def setUp(self):
        self.cliente = Cliente()
        self.cliente.namenode = MagicMock()

    def test_listar_arquivos_vazio(self):
        self.cliente.namenode.listar_arquivos.return_value = []
        self.cliente.listar_arquivos()

    def test_upload_arquivo_nao_encontrado(self):
        with patch("builtins.open", side_effect=FileNotFoundError()):
            self.cliente.namenode.listar_arquivos.return_value = []
            self.cliente.upload("upload inexistente.txt")

    def test_upload_arquivo_existente(self):
        self.cliente.namenode.listar_arquivos.return_value = ["arquivo.txt"]
        self.cliente.upload("upload arquivo.txt")

    def test_download_com_checksum_invalido(self):
        self.cliente.namenode.reconstruir_arquivo_para_download.return_value = True
        self.cliente.namenode.enviar_arquivo_em_blocos.return_value = [
            (b"dados_corrompidos", "checksum_errado")
        ]

        with patch("cliente.main_cliente.calcular_checksum", return_value="outro_checksum"):
            with patch("builtins.open", mock_open()) as m:
                with patch("os.remove") as mock_remove:
                    self.cliente.download("download arquivo_remoto.txt")
                    mock_remove.assert_called()

    def test_deletar_cancelado_usuario(self):
        with patch("builtins.input", return_value="n"):
            self.cliente.deletar("delete arquivo_remoto.txt")

    def test_deletar_confirmado_sucesso(self):
        self.cliente.namenode.delete_arquivo.return_value = True
        with patch("builtins.input", return_value="s"):
            self.cliente.deletar("delete arquivo_remoto.txt")

    def test_download_falha_reconstrucao(self):
        self.cliente.namenode.reconstruir_arquivo_para_download.return_value = False
        self.cliente.download("download inexistente.txt")


if __name__ == "__main__":
    unittest.main()
