from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitConfig(BaseSettings):
    """Конфигурация для подключения к RabbitMQ."""

    # Параметры подключения
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_LOCAL_HOST_NAME: str
    RABBITMQ_LOCAL_PORT: int

    # Переменные окружения для счетчика попыток отправки сообщения
    X_RETRIES_HEADER: str
    ATTEMPTS_COUNT: int
    CRITICAL_ATTEMPTS_VALUE: int

    # Очереди RabbitMQ
    ORDERS_RABBITMQ_QUEUE: str
    NOTIFICATION_RABBITMQ_QUEUE: str

    @property
    def url(self) -> str:
        """
        Формирует и возвращает URL для подключения к RabbitMQ.
        """
        return (
            f"amqp://{self.RABBITMQ_DEFAULT_USER}:"
            f"{self.RABBITMQ_DEFAULT_PASS}@"
            f"{self.RABBITMQ_LOCAL_HOST_NAME}:"
            f"{self.RABBITMQ_LOCAL_PORT}/"
        )

    # Конфигурация чтения переменных из .env файла
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",  # Путь к файлу .env
        extra="ignore",  # Игнорировать лишние переменные окружения
    )


rabbit_config = RabbitConfig()
