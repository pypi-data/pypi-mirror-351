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

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    'FncLogger',
    'LogLevel',
    'LogMode',
    'OutputFormat',
    'get_logger',
    'setup_basic_logger'
]
