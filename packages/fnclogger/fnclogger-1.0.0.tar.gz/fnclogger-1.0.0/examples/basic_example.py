"""
Базовый пример использования FncLogger
"""

from fnclogger import get_logger


def main():
    # Создание логгера
    logger = get_logger("example_app")

    print("=== Тест FncLogger ===")

    # Основные методы
    logger.debug("Отладочное сообщение")
    logger.info("Информационное сообщение")
    logger.warning("Предупреждение")
    logger.error("Ошибка")

    # Цветные методы
    logger.success("Операция выполнена успешно!")
    logger.highlight("Важная информация")
    logger.alert("Требуется внимание")
    logger.fail("Критическая ошибка")

    # С дополнительными данными
    logger.info("Пользователь вошел в систему", extra={
        "user_id": 123,
        "email": "user@example.com"
    })

    print("=== Тест завершен ===")


if __name__ == "__main__":
    main()