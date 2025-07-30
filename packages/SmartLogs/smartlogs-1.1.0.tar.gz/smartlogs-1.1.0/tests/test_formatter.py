import pytest
from datetime import datetime
from SmartLogs.formatter import (
    SmartFormatter,
    JSONFormatter,
    XMLFormatter,
    YAMLFormatter,
    TableFormatter,
    TemplateFormatter
)

def test_basic_formatting():
    formatter = SmartFormatter()
    message = "Teste de mensagem"
    level = "INFO"
    timestamp = datetime.now()
    
    formatted = formatter.format(message, level, timestamp)
    
    assert message in formatted
    assert level in formatted
    assert timestamp.strftime("%Y-%m-%d") in formatted

def test_json_formatting():
    formatter = JSONFormatter()
    message = "Teste de mensagem"
    level = "INFO"
    timestamp = datetime.now()
    
    formatted = formatter.format(message, level, timestamp)
    
    assert '"message": "Teste de mensagem"' in formatted
    assert '"level": "INFO"' in formatted
    assert '"timestamp":' in formatted

def test_xml_formatting():
    formatter = XMLFormatter()
    message = "Teste de mensagem"
    level = "INFO"
    timestamp = datetime.now()
    
    formatted = formatter.format(message, level, timestamp)
    
    assert "<log>" in formatted
    assert "<message>Teste de mensagem</message>" in formatted
    assert "<level>INFO</level>" in formatted
    assert "<timestamp>" in formatted

def test_yaml_formatting():
    formatter = YAMLFormatter()
    message = "Teste de mensagem"
    level = "INFO"
    timestamp = datetime.now()
    
    formatted = formatter.format(message, level, timestamp)
    
    assert "message: Teste de mensagem" in formatted
    assert "level: INFO" in formatted
    assert "timestamp:" in formatted

def test_table_formatting():
    formatter = TableFormatter()
    message = "Teste de mensagem"
    level = "INFO"
    timestamp = datetime.now()
    
    formatted = formatter.format(message, level, timestamp)
    
    assert "| Timestamp" in formatted
    assert "| Level" in formatted
    assert "| Message" in formatted
    assert "| Teste de mensagem" in formatted
    assert "| INFO" in formatted

def test_template_formatting():
    template = "[{timestamp}] {level}: {message}"
    formatter = TemplateFormatter(template)
    message = "Teste de mensagem"
    level = "INFO"
    timestamp = datetime.now()
    
    formatted = formatter.format(message, level, timestamp)
    
    assert message in formatted
    assert level in formatted
    assert timestamp.strftime("%Y-%m-%d") in formatted

def test_conditional_formatting():
    formatter = SmartFormatter()
    message = "Teste de mensagem"
    level = "ERROR"
    timestamp = datetime.now()
    
    # Teste com nível ERROR
    formatted = formatter.format(message, level, timestamp)
    assert "ERROR" in formatted
    
    # Teste com nível INFO
    formatted = formatter.format(message, "INFO", timestamp)
    assert "INFO" in formatted

def test_emoji_formatting():
    formatter = SmartFormatter(use_emojis=True)
    message = "Teste de mensagem"
    
    # Teste com diferentes níveis
    assert "✅" in formatter.format(message, "INFO", datetime.now())
    assert "⚠️" in formatter.format(message, "WARNING", datetime.now())
    assert "❌" in formatter.format(message, "ERROR", datetime.now())
    assert "🚨" in formatter.format(message, "CRITICAL", datetime.now())
    assert "🔍" in formatter.format(message, "DEBUG", datetime.now())

def test_custom_style_formatting():
    formatter = SmartFormatter(
        styles={
            "INFO": {"color": "green", "bold": True},
            "ERROR": {"color": "red", "italic": True}
        }
    )
    message = "Teste de mensagem"
    
    # Teste com estilo personalizado
    formatted = formatter.format(message, "INFO", datetime.now())
    assert "\x1b[32m" in formatted  # Código ANSI para verde
    assert "\x1b[1m" in formatted   # Código ANSI para negrito
    
    formatted = formatter.format(message, "ERROR", datetime.now())
    assert "\x1b[31m" in formatted  # Código ANSI para vermelho
    assert "\x1b[3m" in formatted   # Código ANSI para itálico 