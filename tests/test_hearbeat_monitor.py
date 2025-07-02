import unittest
from unittest.mock import MagicMock, patch
from namenode.heartbeat_monitor import HeartbeatMonitor
import time

class TestHeartbeatMonitor(unittest.TestCase):
    def setUp(self):
        self.mock_namenode = MagicMock()
        self.mock_namenode.datanodes_ativos = {
            "uri1": time.time() - 10,
            "uri2": time.time() - 100  # inativo
        }
        self.mock_namenode.lock = MagicMock()
        self.mock_namenode.metadados.metadados = {
            "arquivo1": {
                "chunk1": ["uri1", "uri2"],
                "chunk2": ["uri2"]
            }
        }
        self.mock_namenode.metadados.lock = MagicMock()

        self.monitor = HeartbeatMonitor(self.mock_namenode)

    @patch("time.sleep", return_value=None)
    def test_run_remove_datanode_inativo(self, _):
        # Executa apenas uma iteração do loop
        with patch.object(self.monitor, "_remover_uri_dos_metadados") as mock_remover:
            with self.assertLogs(level="INFO"):
                try:
                    self.monitor.run()
                except:
                    pass  # ignora loop infinito simulado

            mock_remover.assert_called_with("uri2")

    def test_remover_uri_dos_metadados(self):
        self.mock_namenode.metadados._salvar_em_disco = MagicMock()

        self.monitor._remover_uri_dos_metadados("uri2")

        metadados = self.mock_namenode.metadados.metadados
        self.assertEqual(metadados["arquivo1"]["chunk1"], ["uri1"])
        self.assertEqual(metadados["arquivo1"]["chunk2"], [])
        self.mock_namenode.metadados._salvar_em_disco.assert_called_once()


if __name__ == "__main__":
    unittest.main()
