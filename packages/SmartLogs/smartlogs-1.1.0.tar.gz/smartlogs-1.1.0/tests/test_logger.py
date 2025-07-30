import os
import unittest

from SmartLogs.logger import SmartLogger


class TestSmartLogger(unittest.TestCase):
    """
    Testes unitários para o SmartLogger.
    """
    def setUp(self):
        """Configuração inicial para os testes."""
        self.logger = SmartLogger(log_file="test_logs.txt", level="DEBUG")

    def test_log_info(self):
        """Testa se o logger consegue registrar uma mensagem INFO."""
        self.logger.info("Teste de log INFO")
        with open("test_logs.txt", "r") as file:
            logs = file.read()
        self.assertIn("INFO", logs)
        self.assertIn("Teste de log INFO", logs)

    def test_log_error(self):
        """Testa se o logger consegue registrar uma mensagem ERROR."""
        self.logger.error("Teste de log ERROR")
        with open("test_logs.txt", "r") as file:
            logs = file.read()
        self.assertIn("ERROR", logs)
        self.assertIn("Teste de log ERROR", logs)

    def test_log_debug(self):
        """Testa se o logger consegue registrar uma mensagem DEBUG."""
        self.logger.debug("Teste de log DEBUG")
        with open("test_logs.txt", "r") as file:
            logs = file.read()
        self.assertIn("DEBUG", logs)
        self.assertIn("Teste de log DEBUG", logs)

    def tearDown(self):
        """Remove o arquivo de log após os testes."""
        if os.path.exists("test_logs.txt"):
            os.remove("test_logs.txt")


if __name__ == "__main__":
    unittest.main()
