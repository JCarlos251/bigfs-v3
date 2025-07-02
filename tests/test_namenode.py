import unittest
from unittest.mock import MagicMock, patch, mock_open
from namenode.namenode import NameNode


class TestNameNodeFalhas(unittest.TestCase):
    def setUp(self):
        self.namenode = NameNode()
        self.namenode.metadados = MagicMock()
        self.namenode.chunk_manager = MagicMock()
        self.namenode.obter_datanodes_vivos = MagicMock(return_value=["mock://dn1"])
        self.namenode.escolher_datanode_com_menos_chunks = MagicMock(return_value="mock://dn1")

    @patch("os.path.exists", return_value=False)
    def test_processar_upload_sem_tempfile(self, _):
        sucesso = self.namenode.processar_arquivo_upload("arquivo.txt")
        self.assertFalse(sucesso)

    @patch("builtins.open", new_callable=mock_open, read_data=b"teste")
    @patch("os.path.exists", return_value=True)
    @patch("os.remove")
    @patch("namenode.namenode.calcular_checksum", return_value="ok")
    @patch("namenode.namenode.Proxy")
    def test_processar_upload_com_sucesso(self, mock_proxy, *_):
        self.namenode.chunk_manager.dividir_em_chunks.return_value = [b"chunk1"]
        self.namenode.chunk_manager.gerar_nomes_chunks.return_value = ["chunk_1"]
        mock_proxy.return_value.__enter__.return_value.salvar_arquivo.return_value = True

        sucesso = self.namenode.processar_arquivo_upload("arquivo.txt")
        self.assertTrue(sucesso)

    def test_delete_arquivo_inexistente(self):
        self.namenode.metadados.obter_chunks_do_arquivo.return_value = None
        sucesso = self.namenode.delete_arquivo("inexistente.txt")
        self.assertFalse(sucesso)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("os.remove")
    def test_enviar_arquivo_em_blocos_com_sucesso(self, *_):
        with patch("datanode.storage_utils.calcular_checksum", return_value="mocked"):
            blocos = list(self.namenode.enviar_arquivo_em_blocos("arquivo.txt"))
            self.assertIsInstance(blocos, list)

    @patch("os.path.exists", return_value=False)
    def test_enviar_arquivo_em_blocos_falha(self, *_):
        with self.assertRaises(FileNotFoundError):
            list(self.namenode.enviar_arquivo_em_blocos("arquivo_nao_existe.txt"))

    @patch("os.remove")
    def test_finalizar_download_ok(self, mock_remove):
        with patch("os.path.exists", return_value=True):
            self.namenode.finalizar_download("arquivo.txt")
            mock_remove.assert_called()

    def test_finalizar_download_erro(self):
        with patch("os.remove", side_effect=Exception("erro")), patch("os.path.exists", return_value=True):
            self.namenode.finalizar_download("arquivo.txt")  # erro silencioso esperado


if __name__ == "__main__":
    unittest.main()
