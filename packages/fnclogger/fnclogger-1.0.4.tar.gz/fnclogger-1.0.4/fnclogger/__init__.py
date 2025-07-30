"""
FncLogger - простой и мощный логгер для Python
"""

from .logger import (
    FncLogger,
    LogLevel,
    LogMode,
    OutputFormat,
    get_logger,
    setup_basic_logger
)

__version__ = "1.0.4"
__author__ = "plv88"
__email__ = "devplv88@gmail.com"

__all__ = [
    'FncLogger',
    'LogLevel',
    'LogMode',
    'OutputFormat',
    'get_logger',
    'setup_basic_logger'
]
