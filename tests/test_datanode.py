import unittest
from unittest.mock import patch, MagicMock
from datanode.datanode import DataNode, HeartbeatSender

class TestDataNode(unittest.TestCase):
    def setUp(self):
        self.storage_dir = "test_storage"

        # Patches para evitar acesso real ao sistema de arquivos
        patcher_listdir = patch("datanode.datanode.os.listdir", return_value=[])
        patcher_makedirs = patch("datanode.datanode.os.makedirs")
        self.mock_listdir = patcher_listdir.start()
        self.mock_makedirs = patcher_makedirs.start()
        self.addCleanup(patcher_listdir.stop)
        self.addCleanup(patcher_makedirs.stop)

        self.datanode = DataNode(self.storage_dir)

    @patch("datanode.datanode.salvar_chunk")
    @patch("datanode.datanode.calcular_checksum", return_value="abc123")
    def test_salvar_arquivo_sucesso(self, mock_checksum, mock_salvar):
        resultado = self.datanode.salvar_arquivo("chunk1", b"dados", "abc123")
        self.assertTrue(resultado)

    @patch("datanode.datanode.calcular_checksum", return_value="errado")
    def test_salvar_arquivo_checksum_invalido(self, _):
        with self.assertRaises(ValueError):
            self.datanode.salvar_arquivo("chunk1", b"dados", "abc123")

    @patch("datanode.datanode.deletar_chunk")
    def test_delete_arquivo_sucesso(self, mock_deletar):
        resultado = self.datanode.delete_arquivo("chunk1")
        self.assertTrue(resultado)

    @patch("datanode.datanode.carregar_chunk", return_value=b"conteudo")
    @patch("datanode.datanode.calcular_checksum", return_value="abc123")
    def test_ler_arquivo_sucesso(self, _, __):
        dados, checksum = self.datanode.ler_arquivo("chunk1")
        self.assertEqual(dados, b"conteudo")
        self.assertEqual(checksum, "abc123")

    @patch("datanode.datanode.os.listdir", return_value=["arq1", "arq2"])
    @patch("datanode.datanode.os.remove")
    def test_limpar_todos_os_chunks(self, mock_remove, _):
        self.datanode.limpar_todos_os_chunks()
        self.assertEqual(mock_remove.call_count, 2)


class TestHeartbeatSender(unittest.TestCase):
    @patch("datanode.datanode.get_nameserver")
    @patch("datanode.datanode.Proxy")
    @patch("time.sleep", side_effect=[None, Exception("parar")])
    def test_heartbeat_sender_roda(self, _, mock_proxy, mock_ns):
        mock_ns.return_value.lookup.return_value = "mock://namenode"
        heartbeat_mock = MagicMock()
        mock_proxy.return_value.__enter__.return_value.heartbeat = heartbeat_mock

        sender = HeartbeatSender("mock://datanode1")
        try:
            sender.run()
        except Exception:
            pass

        heartbeat_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
