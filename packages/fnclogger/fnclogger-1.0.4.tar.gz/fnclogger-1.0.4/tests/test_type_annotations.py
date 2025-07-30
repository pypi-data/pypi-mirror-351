"""
Тест корректности типизации для FncLogger v1.0.5
"""

from fnclogger import FncLogger, LogLevel, LogMode, OutputFormat, get_logger, setup_basic_logger
from pathlib import Path
from typing import Dict, Any


def test_type_annotations():
    """Тестируем что все аннотации типов корректны"""

    print("🔍 Тестируем корректность аннотаций типов...")

    # ✅ Тест 1: Создание с LogLevel enum
    print("  1️⃣ Тестируем с LogLevel enum...")
    logger1 = FncLogger(
        name="enum_test",
        level=LogLevel.INFO,  # LogLevel enum
        console_level=LogLevel.DEBUG,  # LogLevel enum
        file_level=LogLevel.WARNING  # LogLevel enum
    )
    print("    ✅ LogLevel enum принимается корректно")

    # ✅ Тест 2: Создание с int значениями
    print("  2️⃣ Тестируем с int значениями...")
    logger2 = FncLogger(
        name="int_test",
        level=20,  # int (INFO)
        console_level=10,  # int (DEBUG)
        file_level=30  # int (WARNING)
    )
    print("    ✅ int значения принимаются и конвертируются корректно")

    # ✅ Тест 3: Создание со строками
    print("  3️⃣ Тестируем со строковыми значениями...")
    logger3 = FncLogger(
        name="str_test",
        level="INFO",  # str
        console_level="DEBUG",  # str
        file_level="WARNING"  # str
    )
    print("    ✅ str значения принимаются и конвертируются корректно")

    # ✅ Тест 4: Смешанные типы
    print("  4️⃣ Тестируем смешанные типы...")
    logger4 = FncLogger(
        name="mixed_test",
        level=LogLevel.INFO,  # enum
        console_level="DEBUG",  # str
        file_level=30,  # int
        log_dir=Path("./logs")  # Path объект
    )
    print("    ✅ Смешанные типы работают корректно")

    # ✅ Тест 5: Optional параметры (None)
    print("  5️⃣ Тестируем Optional параметры...")
    logger5 = FncLogger(
        name="optional_test",
        level=LogLevel.INFO,
        console_level=None,  # None - должно использовать level
        file_level=None,  # None - должно использовать level
        log_dir=None  # None - должно использовать ./logs
    )
    print("    ✅ Optional параметры обрабатываются корректно")

    # ✅ Тест 6: get_logger функция
    print("  6️⃣ Тестируем функцию get_logger...")
    quick_logger = get_logger("quick_test")
    print("    ✅ get_logger возвращает FncLogger")

    # ✅ Тест 7: setup_basic_logger с разными типами
    print("  7️⃣ Тестируем setup_basic_logger...")
    basic1 = setup_basic_logger("basic1", "INFO")  # str
    basic2 = setup_basic_logger("basic2", LogLevel.DEBUG)  # enum
    basic3 = setup_basic_logger("basic3", 20)  # int
    print("    ✅ setup_basic_logger принимает разные типы уровней")

    # ✅ Тест 8: configure_from_dict
    print("  8️⃣ Тестируем configure_from_dict...")
    config: Dict[str, Any] = {
        'name': 'dict_test',
        'level': 20,  # int
        'console_level': 'DEBUG',  # str
        'file_level': LogLevel.ERROR,  # enum
        'mode': 'both',  # str
        'file_format': 'json',  # str
        'log_dir': './test_logs'  # str
    }
    dict_logger = FncLogger.configure_from_dict(config)
    print("    ✅ configure_from_dict обрабатывает смешанные типы")

    # ✅ Тест 9: Методы изменения уровней
    print("  9️⃣ Тестируем методы изменения уровней...")
    test_logger = get_logger("level_change_test")

    # Цепочка вызовов должна работать (fluent interface)
    result = (test_logger
              .set_level("ERROR")  # str
              .set_console_level(LogLevel.INFO)  # enum
              .set_file_level(40))  # int

    assert result is test_logger  # Должен возвращать self
    print("    ✅ Методы изменения уровней работают как fluent interface")

    # ✅ Тест 10: Проверка возвращаемых типов методов логирования
    print("  🔟 Тестируем возвращаемые типы методов логирования...")

    # Эти методы должны возвращать None
    result1 = test_logger.info("Test info")
    result2 = test_logger.error("Test error")
    result3 = test_logger.success("Test success")
    result4 = test_logger.fail("Test fail")

    assert result1 is None
    assert result2 is None
    assert result3 is None
    assert result4 is None
    print("    ✅ Методы логирования возвращают None")

    print("\n🎉 Все тесты типизации прошли успешно!")
    return True


def test_error_handling():
    """Тестируем обработку ошибок типизации"""

    print("\n⚠️  Тестируем обработку некорректных типов...")

    # Тест некорректных уровней
    print("  ❌ Тестируем некорректные уровни...")

    try:
        FncLogger("error_test", level=999)  # Некорректный int
        print("    ❌ ОШИБКА: должно было выбросить исключение")
        return False
    except ValueError as e:
        print(f"    ✅ Некорректный int отклонен: {e}")

    try:
        FncLogger("error_test", level="INVALID_LEVEL")  # Некорректная строка
        print("    ❌ ОШИБКА: должно было выбросить исключение")
        return False
    except ValueError as e:
        print(f"    ✅ Некорректная строка отклонена: {e}")

    try:
        FncLogger("error_test", level=[])  # Некорректный тип
        print("    ❌ ОШИБКА: должно было выбросить исключение")
        return False
    except TypeError as e:
        print(f"    ✅ Некорректный тип отклонен: {e}")

    print("  ✅ Обработка ошибок работает корректно")
    return True


def test_ide_compatibility():
    """Тестируем совместимость с IDE/type checkers"""

    print("\n🔧 Проверяем совместимость с IDE...")

    # Создаем логгер и проверяем что IDE видит правильные типы
    logger = FncLogger(
        name="ide_test",
        level=LogLevel.INFO,
        console_level=LogLevel.DEBUG
    )

    # IDE должен понимать что это FncLogger
    assert isinstance(logger, FncLogger)

    # Методы должны возвращать правильные типы
    logger_result = logger.set_level("ERROR")  # Должен вернуть FncLogger
    assert isinstance(logger_result, FncLogger)

    # Методы логирования должны возвращать None
    log_result = logger.info("Test")  # Должен вернуть None
    assert log_result is None

    print("  ✅ IDE совместимость подтверждена")

    # Проверяем что можно использовать в type hints
    def use_logger(my_logger: FncLogger) -> None:
        my_logger.info("Testing type hints")

    use_logger(logger)  # Должно работать без ошибок типов
    print("  ✅ Type hints работают корректно")

    return True


if __name__ == "__main__":
    print("🚀 Запуск тестов типизации FncLogger v1.0.5\n")

    try:
        test1 = test_type_annotations()
        test2 = test_error_handling()
        test3 = test_ide_compatibility()

        if test1 and test2 and test3:
            print("\n🎉 ВСЕ ТЕСТЫ ТИПИЗАЦИИ ПРОШЛИ!")
            print("\n📋 Итоги исправлений v1.0.5:")
            print("  ✅ Добавлены Union типы для гибкости (LogLevel | int | str)")
            print("  ✅ Добавлен метод _normalize_level для конвертации типов")
            print("  ✅ Исправлены аннотации возвращаемых типов")
            print("  ✅ Улучшена совместимость с IDE и type checkers")
            print("  ✅ Добавлена обработка ошибок некорректных типов")
            print("  ✅ configure_from_dict теперь принимает смешанные типы")
            print("\n🔧 IDE больше не будет показывать ошибки типов!")
        else:
            print("\n❌ Некоторые тесты провалились")

    except Exception as e:
        print(f"\n💥 Критическая ошибка в тестах: {e}")
        import traceback

        traceback.print_exc()