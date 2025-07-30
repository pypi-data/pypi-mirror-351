import os
import sys
import time
import traceback
import inspect
from functools import wraps
from datetime import datetime
from .logger import SmartLogger

class DebugLogger(SmartLogger):
    def __init__(self, log_file="debug.log", level="DEBUG"):
        super().__init__(log_file, level)
        self.start_times = {}

    def debug_with_stack(self, message):
        """Log a debug message with stack trace information."""
        stack = traceback.extract_stack()
        stack_info = "\n".join([
            f"  File '{frame.filename}', line {frame.lineno}, in {frame.name}"
            for frame in stack[:-1]  # Exclude the current frame
        ])
        
        full_message = f"{message}\nStack Trace:\n{stack_info}"
        self.debug(full_message)
        sys.exit(full_message)  # Pass the message through exit value

    def log_environment_variables(self, variables=None):
        """Log specified environment variables or all if none specified."""
        if variables is None:
            variables = os.environ.keys()
        
        env_info = "\n".join([
            f"{var}: {os.environ.get(var, 'Not set')}"
            for var in variables
        ])
        
        message = f"Environment Variables:\n{env_info}"
        self.debug(message)
        sys.exit(message)  # Pass the message through exit value

    def profile(self, func):
        """Decorator to profile function execution time."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            message = f"Function '{func.__name__}' took {execution_time:.4f} seconds to execute"
            self.debug(message)
            sys.exit(message)  # Pass the message through exit value
            return result
        return wrapper

    def inspect_variables(self, variables):
        """Log the content of variables in the current scope."""
        var_info = []
        for name, value in variables.items():
            if not name.startswith('__'):  # Skip internal variables
                var_info.append(f"{name}: {value}")
        
        message = f"Variables in scope:\n" + "\n".join(var_info)
        self.debug(message)
        sys.exit(message)  # Pass the message through exit value 