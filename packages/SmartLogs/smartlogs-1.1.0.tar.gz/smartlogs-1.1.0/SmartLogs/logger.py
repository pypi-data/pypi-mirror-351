import logging
import sys
from datetime import datetime

from colorama import Fore, Style


class SmartLogger:
    LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA
    }

    def __init__(self, log_file="logs.txt", level="INFO"):
        self.log_file = log_file
        self.level = self.LEVELS.get(level.upper(), logging.INFO)

        # Configuração do logger
        self.logger = logging.getLogger("SmartLogger")
        self.logger.setLevel(self.level)

        # Criar manipulador para arquivo
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.level)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s") # noqa501
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Criar manipulador para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(console_handler)

    def log(self, level, message):
        color = self.COLORS.get(level.upper(), Fore.WHITE)
        formatted_message = f"{color}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {level.upper()}: {message}{Style.RESET_ALL}" # noqa501

        if level.upper() == "DEBUG":
            self.logger.debug(message)
        elif level.upper() == "INFO":
            self.logger.info(message)
        elif level.upper() == "WARNING":
            self.logger.warning(message)
        elif level.upper() == "ERROR":
            self.logger.error(message)
        elif level.upper() == "CRITICAL":
            self.logger.critical(message)

        print(formatted_message)

    def debug(self, message):
        self.log("DEBUG", message)

    def info(self, message):
        self.log("INFO", message)

    def warning(self, message):
        self.log("WARNING", message)

    def error(self, message):
        self.log("ERROR", message)

    def critical(self, message):
        self.log("CRITICAL", message)
