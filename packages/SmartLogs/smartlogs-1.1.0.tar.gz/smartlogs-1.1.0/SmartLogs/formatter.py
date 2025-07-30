import json
import yaml
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseFormatter(ABC):
    """Classe base para todos os formatadores."""
    
    @abstractmethod
    def format(self, message: str, level: str, timestamp: datetime) -> str:
        """Formata a mensagem de log."""
        pass

class SmartFormatter(BaseFormatter):
    """Formatador padrão com suporte a cores e emojis."""
    
    EMOJIS = {
        "DEBUG": "🔍",
        "INFO": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🚨"
    }
    
    COLORS = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "magenta"
    }
    
    def __init__(self, use_emojis: bool = False, styles: Optional[Dict[str, Dict[str, Any]]] = None):
        self.use_emojis = use_emojis
        self.styles = styles or {}
    
    def format(self, message: str, level: str, timestamp: datetime) -> str:
        """Formata a mensagem com timestamp, nível e estilo."""
        level = level.upper()
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # Adiciona emoji se habilitado
        emoji = self.EMOJIS.get(level, "") if self.use_emojis else ""
        
        # Aplica estilo personalizado ou padrão
        style = self.styles.get(level, {"color": self.COLORS.get(level, "white")})
        
        # Constrói a mensagem formatada
        formatted = f"[{timestamp_str}] {emoji} {level}: {message}"
        
        # Aplica estilos
        if style.get("color"):
            formatted = f"\033[{self._get_color_code(style['color'])}m{formatted}\033[0m"
        if style.get("bold"):
            formatted = f"\033[1m{formatted}\033[0m"
        if style.get("italic"):
            formatted = f"\033[3m{formatted}\033[0m"
        
        return formatted
    
    def _get_color_code(self, color: str) -> str:
        """Retorna o código ANSI para a cor especificada."""
        colors = {
            "black": "30",
            "red": "31",
            "green": "32",
            "yellow": "33",
            "blue": "34",
            "magenta": "35",
            "cyan": "36",
            "white": "37"
        }
        return colors.get(color.lower(), "37")

class JSONFormatter(BaseFormatter):
    """Formatador que gera logs em formato JSON."""
    
    def format(self, message: str, level: str, timestamp: datetime) -> str:
        """Formata a mensagem como JSON."""
        log_data = {
            "timestamp": timestamp.isoformat(),
            "level": level.upper(),
            "message": message
        }
        return json.dumps(log_data)

class XMLFormatter(BaseFormatter):
    """Formatador que gera logs em formato XML."""
    
    def format(self, message: str, level: str, timestamp: datetime) -> str:
        """Formata a mensagem como XML."""
        return f"""<log>
    <timestamp>{timestamp.isoformat()}</timestamp>
    <level>{level.upper()}</level>
    <message>{message}</message>
</log>"""

class YAMLFormatter(BaseFormatter):
    """Formatador que gera logs em formato YAML."""
    
    def format(self, message: str, level: str, timestamp: datetime) -> str:
        """Formata a mensagem como YAML."""
        log_data = {
            "timestamp": timestamp.isoformat(),
            "level": level.upper(),
            "message": message
        }
        return yaml.dump(log_data, default_flow_style=False)

class TableFormatter(BaseFormatter):
    """Formatador que gera logs em formato de tabela."""
    
    def format(self, message: str, level: str, timestamp: datetime) -> str:
        """Formata a mensagem como tabela."""
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"""| Timestamp | Level | Message |
|-----------|-------|---------|
| {timestamp_str} | {level.upper()} | {message} |"""

class TemplateFormatter(BaseFormatter):
    """Formatador que usa um template personalizado."""
    
    def __init__(self, template: str):
        self.template = template
    
    def format(self, message: str, level: str, timestamp: datetime) -> str:
        """Formata a mensagem usando o template especificado."""
        return self.template.format(
            timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            level=level.upper(),
            message=message
        ) 