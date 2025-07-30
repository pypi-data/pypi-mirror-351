import os
import sys
import pytest
from SmartLogs.logger import SmartLogger
from SmartLogs.debug import DebugLogger

def test_stack_trace():
    logger = DebugLogger()
    
    def inner_function():
        logger.debug_with_stack("Teste de stack trace")
    
    def outer_function():
        inner_function()
    
    # Captura a saída do logger
    with pytest.raises(SystemExit) as excinfo:
        outer_function()
    
    # Verifica se a mensagem contém informações da stack trace
    assert "inner_function" in str(excinfo.value)
    assert "outer_function" in str(excinfo.value)

def test_environment_variables():
    logger = DebugLogger()
    
    # Define algumas variáveis de ambiente para teste
    os.environ["TEST_VAR_1"] = "test_value_1"
    os.environ["TEST_VAR_2"] = "test_value_2"
    
    # Captura a saída do logger
    with pytest.raises(SystemExit) as excinfo:
        logger.log_environment_variables(["TEST_VAR_1", "TEST_VAR_2"])
    
    # Verifica se as variáveis de ambiente foram logadas
    output = str(excinfo.value)
    assert "TEST_VAR_1" in output
    assert "test_value_1" in output
    assert "TEST_VAR_2" in output
    assert "test_value_2" in output

def test_profiling():
    logger = DebugLogger()
    
    @logger.profile
    def slow_function():
        import time
        time.sleep(0.1)
        return "done"
    
    # Captura a saída do logger
    with pytest.raises(SystemExit) as excinfo:
        slow_function()
    
    # Verifica se o profiling foi logado
    output = str(excinfo.value)
    assert "slow_function" in output
    assert "took" in output
    assert "seconds to execute" in output

def test_variable_inspection():
    logger = DebugLogger()
    
    test_var = "test_value"
    test_dict = {"key": "value"}
    test_list = [1, 2, 3]
    
    # Captura a saída do logger
    with pytest.raises(SystemExit) as excinfo:
        logger.inspect_variables(locals())
    
    # Verifica se as variáveis foram logadas
    output = str(excinfo.value)
    assert "test_var" in output
    assert "test_value" in output
    assert "test_dict" in output
    assert "key" in output
    assert "test_list" in output
    assert "1" in output 