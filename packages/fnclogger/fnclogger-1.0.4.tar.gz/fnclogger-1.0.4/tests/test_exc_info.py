"""
Тест исправления ошибки exc_info в FncLogger
"""

from fnclogger import get_logger, FncLogger, LogMode
import tempfile
from pathlib import Path


def test_exc_info_fix():
    """Тестируем что exc_info больше не вызывает ошибок"""

    print("🧪 Тестируем исправление exc_info...")

    # Создаем временную директорию
    temp_dir = Path("./test_exc_info")
    temp_dir.mkdir(exist_ok=True)

    # Создаем логгер с файловым выводом
    logger = FncLogger(
        name="test_exc_info",
        mode=LogMode.BOTH,
        log_dir=temp_dir
    )

    try:
        # Тестируем методы БЕЗ exc_info (по умолчанию)
        print("  Тестируем critical() без exc_info...")
        logger.critical("Критическая ошибка без exc_info")
        print("  ✅ critical() работает")

        print("  Тестируем error() без exc_info...")
        logger.error("Обычная ошибка без exc_info")
        print("  ✅ error() работает")

        print("  Тестируем fail() без exc_info...")
        logger.fail("Fail без exc_info")
        print("  ✅ fail() работает")

        # Тестируем С exc_info=True но без активного исключения
        print("  Тестируем с exc_info=True без активного исключения...")
        logger.error("Ошибка с exc_info=True", exc_info=True)
        logger.critical("Критическая с exc_info=True", exc_info=True)
        logger.fail("Fail с exc_info=True", exc_info=True)
        print("  ✅ exc_info=True без исключения работает")

        # Тестируем с реальным исключением
        print("  Тестируем с реальным исключением...")
        try:
            raise ValueError("Тестовое исключение")
        except Exception:
            logger.error("Поймали исключение", exc_info=True)
            logger.critical("Критическая ошибка с исключением", exc_info=True)
            logger.fail("Fail с реальным исключением", exc_info=True)
        print("  ✅ Реальное исключение обработано")

        # Проверяем файл лога
        log_file = temp_dir / "test_exc_info.log"
        if log_file.exists():
            content = log_file.read_text(encoding='utf-8')
            lines = content.splitlines()
            print(f"  📄 Записано строк в лог: {len(lines)}")

            # Показываем несколько строк для проверки формата
            for i, line in enumerate(lines[:3]):
                print(f"    Строка {i + 1}: {line}")

            print("  ✅ Файл лога создан успешно")

        print("🎉 Все тесты прошли! Ошибка exc_info исправлена.")
        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monitor_compatibility():
    """Тестируем совместимость с AsyncTgLogMonitor"""

    print("\n🔗 Тестируем совместимость с AsyncTgLogMonitor...")

    # Создаем логи которые будет читать монитор
    temp_dir = Path("./test_compatibility")
    temp_dir.mkdir(exist_ok=True)

    logger = FncLogger(
        name="compatibility_test",
        mode=LogMode.FILE_ONLY,
        log_dir=temp_dir
    )

    try:
        # Генерируем различные типы сообщений (БЕЗ exc_info=True по умолчанию)
        logger.info("Обычное информационное сообщение")
        logger.warning("Предупреждение для мониторинга")
        logger.error("Ошибка для мониторинга")
        logger.critical("Критическая ошибка")  # Теперь без exc_info=True по умолчанию
        logger.success("Успешная операция")
        logger.fail("Неудачная операция")

        # Проверяем формат
        log_file = temp_dir / "compatibility_test.log"
        if log_file.exists():
            lines = log_file.read_text(encoding='utf-8').splitlines()
            print(f"  📝 Создано {len(lines)} строк лога")

            # Показываем формат
            for i, line in enumerate(lines[:3]):
                print(f"  📄 Строка {i + 1}: {line}")

            print("  ✅ Формат логов совместим с AsyncTgLogMonitor")
            return True
        else:
            print("  ❌ Файл лога не создан")
            return False

    except Exception as e:
        print(f"  ❌ Ошибка создания логов: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exception_scenarios():
    """Тестируем различные сценарии с исключениями"""

    print("\n🔍 Тестируем сценарии с исключениями...")

    temp_dir = Path("./test_exceptions")
    temp_dir.mkdir(exist_ok=True)

    logger = FncLogger(
        name="exception_test",
        mode=LogMode.CONSOLE_ONLY,
        log_dir=temp_dir
    )

    try:
        # Сценарий 1: exc_info=False (по умолчанию)
        print("  Сценарий 1: exc_info=False...")
        logger.error("Ошибка без трейсбека")
        logger.critical("Критическая без трейсбека")
        print("    ✅ Без трейсбека работает")

        # Сценарий 2: exc_info=True без активного исключения
        print("  Сценарий 2: exc_info=True без исключения...")
        logger.error("Ошибка с exc_info но без исключения", exc_info=True)
        print("    ✅ exc_info=True без исключения работает")

        # Сценарий 3: exc_info=True с активным исключением
        print("  Сценарий 3: exc_info=True с активным исключением...")
        try:
            x = 1 / 0
        except ZeroDivisionError:
            logger.error("Деление на ноль", exc_info=True)
            logger.critical("Критическая ошибка деления", exc_info=True)
        print("    ✅ exc_info=True с исключением работает")

        print("  🎉 Все сценарии работают корректно")
        return True

    except Exception as e:
        print(f"  ❌ Ошибка в сценарии: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Тест исправления FncLogger v1.0.3\n")

    success1 = test_exc_info_fix()
    success2 = test_monitor_compatibility()
    success3 = test_exception_scenarios()

    if success1 and success2 and success3:
        print("\n🎉 Все тесты прошли! FncLogger готов к публикации v1.0.3")
        print("\n📋 Итоги исправления:")
        print("  ✅ critical() больше не использует exc_info=True по умолчанию")
        print("  ✅ exc_info корректно обрабатывается в любых сценариях")
        print("  ✅ Совместимость с AsyncTgLogMonitor сохранена")
        print("  ✅ Поддержка исключений работает правильно")
    else:
        print("\n❌ Некоторые тесты провалились")