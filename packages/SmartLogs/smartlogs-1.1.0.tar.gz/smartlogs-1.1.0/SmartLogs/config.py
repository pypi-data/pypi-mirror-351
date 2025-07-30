import os


class Config:
    """
    Configurações globais do SmartLogger.
    """
    LOG_FILE = os.getenv("SMARTLOGS_LOG_FILE", "logs.txt")  # Nome do arquivo de log padrão # noqa501
    LOG_LEVEL = os.getenv("SMARTLOGS_LOG_LEVEL", "INFO")  # Nível de log padrão # noqa501
    ENABLE_CONSOLE_LOG = os.getenv("SMARTLOGS_ENABLE_CONSOLE", "True").lower() == "true"  # Ativar logs no console # noqa501
    ENABLE_FILE_LOG = os.getenv("SMARTLOGS_ENABLE_FILE", "True").lower() == "true"  # Ativar logs em arquivo # noqa501
    ENABLE_SLACK_LOG = os.getenv("SMARTLOGS_ENABLE_SLACK", "False").lower() == "true"  # Enviar logs para o Slack # noqa501
    ENABLE_TELEGRAM_LOG = os.getenv("SMARTLOGS_ENABLE_TELEGRAM", "False").lower() == "true"  # Enviar logs para o Telegram # noqa501
    SLACK_WEBHOOK_URL = os.getenv("SMARTLOGS_SLACK_WEBHOOK", "")  # URL do webhook do Slack # noqa501
    TELEGRAM_BOT_TOKEN = os.getenv("SMARTLOGS_TELEGRAM_BOT_TOKEN", "")  # Token do bot do Telegram # noqa501
    TELEGRAM_CHAT_ID = os.getenv("SMARTLOGS_TELEGRAM_CHAT_ID", "")  # ID do chat do Telegram    TELEGRAM_CHAT_ID = os.getenv("SMARTLOGS_TELEGRAM_CHAT_ID", "")  # ID do chat do Telegram # noqa501
