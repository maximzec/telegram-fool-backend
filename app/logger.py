import logging

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO
)

# Получение логгера
logger = logging.getLogger("app_logger")
