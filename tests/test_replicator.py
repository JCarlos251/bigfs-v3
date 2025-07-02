import unittest
from unittest.mock import patch, MagicMock
from namenode.replicador import Replicador

class TestReplicador(unittest.TestCase):
    def setUp(self):
        self.mock_namenode = MagicMock()
        self.replicador = Replicador(self.mock_namenode, intervalo=0.1)

    @patch('time.sleep', return_value=None)  # para evitar delay no teste
    def test_run_loop_execucao(self, mock_sleep):
        count = 0

        def replicar_chunks_fake():
            nonlocal count
            count += 1
            if count > 1:
                raise KeyboardInterrupt  # interrompe o loop depois da 2ª execução
            raise Exception("Erro forçado")  # simula erro na 1ª execução

        self.replicador.replicar_chunks = replicar_chunks_fake

        with self.assertRaises(KeyboardInterrupt):
            self.replicador.run()

        self.assertEqual(count, 2)

if __name__ == "__main__":
    unittest.main()
