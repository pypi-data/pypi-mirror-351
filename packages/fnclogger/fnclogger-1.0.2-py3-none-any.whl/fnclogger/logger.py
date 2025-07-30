"""
FncLogger - простой и мощный логгер для Python приложений

Поддерживает:
- Цветной вывод в консоль (опционально с Rich)
- Ротацию файлов
- JSON форматирование
- Гибкую конфигурацию
- Thread-safe операции
"""

import logging
import json
import re
import threading
from datetime import datetime
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Optional, Union, Any


class LogLevel(Enum):
    """Уровни логирования"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogMode(Enum):
    """Режимы вывода логов"""
    CONSOLE_ONLY = "console"
    FILE_ONLY = "file"
    BOTH = "both"


class OutputFormat(Enum):
    """Форматы вывода"""
    TEXT = "text"
    JSON = "json"


# Rich - основная зависимость
from rich.console import Console
from rich.logging import RichHandler


class JSONFormatter(logging.Formatter):
    """Форматтер для JSON логов"""

    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Добавляем информацию об исключении, если есть
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Добавляем дополнительные поля
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        return json.dumps(log_data, ensure_ascii=False)


class ColorFormatter(logging.Formatter):
    """Простой цветной форматтер без Rich"""

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'  # Reset
    }

    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class FncLogger:
    """
    Простой и мощный логгер с поддержкой множественных режимов вывода
    """

    _instances: Dict[str, 'FncLogger'] = {}
    _lock = threading.Lock()

    # Паттерн для очистки ANSI и Rich тегов
    ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')
    RICH_PATTERN = re.compile(r'\[/?[^\]]+\]')

    def __new__(cls, name: str, **kwargs):
        """Thread-safe синглтон"""
        with cls._lock:
            if name not in cls._instances:
                instance = super().__new__(cls)
                cls._instances[name] = instance
            return cls._instances[name]

    def __init__(
            self,
            name: str,
            mode: LogMode = LogMode.BOTH,
            level: LogLevel = LogLevel.INFO,
            console_level: Optional[LogLevel] = None,
            file_level: Optional[LogLevel] = None,
            log_dir: Optional[Union[str, Path]] = None,
            file_format: OutputFormat = OutputFormat.TEXT,
            console_format: OutputFormat = OutputFormat.TEXT,
            use_rich: bool = True,
            max_file_size: int = 10 * 1024 * 1024,  # 10MB
            backup_count: int = 5,
            date_format: str = "%Y-%m-%d %H:%M:%S",
            custom_format: Optional[str] = None,
            encoding: str = 'utf-8'
    ):
        """
        Инициализация логгера

        Args:
            name: Имя логгера
            mode: Режим вывода (консоль/файл/оба)
            level: Базовый уровень логирования
            console_level: Уровень для консоли (по умолчанию как level)
            file_level: Уровень для файла (по умолчанию как level)
            log_dir: Директория для файлов логов
            file_format: Формат файловых логов
            console_format: Формат консольных логов
            use_rich: Использовать Rich для цветного вывода
            max_file_size: Максимальный размер файла лога
            backup_count: Количество backup файлов
            date_format: Формат даты и времени
            custom_format: Кастомный формат сообщений
            encoding: Кодировка файлов
        """

        # Предотвращаем повторную инициализацию
        if hasattr(self, '_initialized'):
            return

        self.name = name
        self.mode = mode
        self.console_level = console_level or level
        self.file_level = file_level or level
        self.file_format = file_format
        self.console_format = console_format
        self.use_rich = use_rich  # Rich всегда доступен
        self.encoding = encoding

        # Настройка директории логов
        if log_dir is None:
            self.log_dir = Path.cwd() / 'logs'
        else:
            self.log_dir = Path(log_dir)

        # Создаем директорию если не существует
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise RuntimeError(f"Нет прав для создания директории логов: {e}")

        # Rich консоль для цветного вывода (создаем ДО настройки обработчиков)
        self.console = Console()  # Rich всегда доступен

        # Настройка основного логгера
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        self.logger.handlers.clear()  # Очищаем существующие обработчики

        # Настройка форматтеров
        self._setup_formatters(date_format, custom_format)

        # Настройка обработчиков
        self._setup_handlers(max_file_size, backup_count)

        self._initialized = True

    def _setup_formatters(self, date_format: str, custom_format: Optional[str]):
        """Настройка форматтеров"""

        # Базовый формат
        base_format = custom_format or "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s"

        # Текстовые форматтеры
        self.text_formatter = logging.Formatter(base_format, datefmt=date_format)
        self.color_formatter = ColorFormatter(base_format, datefmt=date_format)

        # JSON форматтер
        self.json_formatter = JSONFormatter()

        # Rich форматтер (всегда доступен)
        self.rich_handler_formatter = logging.Formatter("%(message)s")

    def _setup_handlers(self, max_file_size: int, backup_count: int):
        """Настройка обработчиков логов"""

        # Файловый обработчик
        if self.mode in [LogMode.FILE_ONLY, LogMode.BOTH]:
            log_file = self.log_dir / f"{self.name}.log"

            # Используем RotatingFileHandler для контроля размера
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding=self.encoding
            )

            file_handler.setLevel(self.file_level.value)

            if self.file_format == OutputFormat.JSON:
                file_handler.setFormatter(self.json_formatter)
            else:
                file_handler.setFormatter(self.text_formatter)

            self.logger.addHandler(file_handler)

        # Консольный обработчик
        if self.mode in [LogMode.CONSOLE_ONLY, LogMode.BOTH]:
            if self.use_rich:
                console_handler = RichHandler(
                    console=self.console,
                    rich_tracebacks=True,
                    markup=True,
                    show_time=False,
                    show_path=False
                )
                console_handler.setFormatter(self.rich_handler_formatter)
            else:
                console_handler = logging.StreamHandler()
                if self.console_format == OutputFormat.JSON:
                    console_handler.setFormatter(self.json_formatter)
                else:
                    console_handler.setFormatter(self.color_formatter)

            console_handler.setLevel(self.console_level.value)
            self.logger.addHandler(console_handler)

    def _clean_message(self, message: str) -> str:
        """Очистка сообщения от ANSI и Rich тегов для файла"""
        # Удаляем ANSI escape последовательности
        message = self.ANSI_PATTERN.sub('', message)
        # Удаляем Rich теги
        message = self.RICH_PATTERN.sub('', message)
        return message

    def _log_with_formatting(self, level: LogLevel, console_message: str, file_message: str,
                             extra: Optional[Dict[str, Any]] = None, exc_info: bool = False, **kwargs):
        """Логирование с разным форматированием для консоли и файла"""

        # Подготавливаем extra данные
        log_extra = {}
        if extra:
            log_extra['extra_data'] = extra
            log_extra.update(extra)

        # Логируем в консоль
        if self.mode in [LogMode.CONSOLE_ONLY, LogMode.BOTH]:
            # Создаем временный логгер только для консоли
            console_record = self.logger.makeRecord(
                self.logger.name, level.value, '', 0, console_message,
                (), None, '', log_extra
            )
            console_record.exc_info = exc_info if exc_info else None

            # Отправляем только в консольные обработчики
            for handler in self.logger.handlers:
                if not isinstance(handler, RotatingFileHandler):
                    if console_record.levelno >= handler.level:
                        handler.handle(console_record)

        # Логируем в файл (очищенное сообщение)
        if self.mode in [LogMode.FILE_ONLY, LogMode.BOTH]:
            # Создаем запись для файла
            file_record = self.logger.makeRecord(
                self.logger.name, level.value, '', 0, file_message,
                (), None, '', log_extra
            )
            file_record.exc_info = exc_info if exc_info else None

            # Отправляем только в файловые обработчики
            for handler in self.logger.handlers:
                if isinstance(handler, RotatingFileHandler):
                    if file_record.levelno >= handler.level:
                        handler.handle(file_record)

    def _log(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None,
             exc_info: bool = False, **kwargs):
        """Внутренний метод логирования"""

        # Для обычных сообщений используем то же сообщение для консоли и файла
        self._log_with_formatting(level, message, message, extra, exc_info, **kwargs)

    # Основные методы логирования
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Отладочное сообщение"""
        self._log(LogLevel.DEBUG, message, extra, **kwargs)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Информационное сообщение"""
        self._log(LogLevel.INFO, message, extra, **kwargs)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Предупреждение"""
        self._log(LogLevel.WARNING, message, extra, **kwargs)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None,
              exc_info: bool = False, **kwargs):
        """Ошибка"""
        self._log(LogLevel.ERROR, message, extra, exc_info=exc_info, **kwargs)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None,
                 exc_info: bool = True, **kwargs):
        """Критическая ошибка"""
        self._log(LogLevel.CRITICAL, message, extra, exc_info=exc_info, **kwargs)

    # Методы с цветным выводом
    def success(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Сообщение об успехе (зеленый)"""
        console_message = f"[bold green]✓[/bold green] {message}" if self.use_rich else f"✓ {message}"
        file_message = f"✓ {message}"
        self._log_with_formatting(LogLevel.INFO, console_message, file_message, extra, **kwargs)

    def highlight(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Выделенное сообщение (синий)"""
        console_message = f"[bold blue]→[/bold blue] {message}" if self.use_rich else f"→ {message}"
        file_message = f"→ {message}"
        self._log_with_formatting(LogLevel.INFO, console_message, file_message, extra, **kwargs)

    def alert(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Предупреждение (желтый)"""
        console_message = f"[bold yellow]⚠[/bold yellow] {message}" if self.use_rich else f"⚠ {message}"
        file_message = f"⚠ {message}"
        self._log_with_formatting(LogLevel.WARNING, console_message, file_message, extra, **kwargs)

    def fail(self, message: str, extra: Optional[Dict[str, Any]] = None,
             exc_info: bool = False, **kwargs):
        """Ошибка (красный)"""
        console_message = f"[bold red]✗[/bold red] {message}" if self.use_rich else f"✗ {message}"
        file_message = f"✗ {message}"
        self._log_with_formatting(LogLevel.ERROR, console_message, file_message, extra, exc_info=exc_info, **kwargs)

    # Утилитарные методы
    def set_level(self, level: LogLevel):
        """Изменение уровня логирования"""
        self.logger.setLevel(level.value)
        return self

    @classmethod
    def get_logger(cls, name: str, **kwargs) -> 'FncLogger':
        """Получение экземпляра логгера"""
        return cls(name, **kwargs)


# Convenience функции для быстрого использования
def get_logger(name: str = "app", **kwargs) -> FncLogger:
    """Быстрое получение логгера с настройками по умолчанию"""
    return FncLogger.get_logger(name, **kwargs)


def setup_basic_logger(name: str = "app", level: str = "INFO") -> FncLogger:
    """Настройка базового логгера"""
    return FncLogger(
        name=name,
        level=LogLevel[level.upper()],
        mode=LogMode.BOTH,
        use_rich=True  # Rich всегда доступен
    )


# Пример использования
if __name__ == "__main__":
    # Создание логгера
    logger = get_logger("test_app")

    # Базовые сообщения
    logger.debug("Отладочное сообщение")
    logger.info("Информационное сообщение")
    logger.warning("Предупреждение")
    logger.error("Ошибка")

    # Цветные сообщения
    logger.success("Операция выполнена успешно!")
    logger.highlight("Важная информация")
    logger.alert("Внимание! Что-то требует проверки")
    logger.fail("Критическая ошибка в системе")

    # С дополнительными данными
    logger.info("Пользователь вошел в систему", extra={
        "user_id": 123,
        "ip": "192.168.1.1",
        "browser": "Chrome"
    })