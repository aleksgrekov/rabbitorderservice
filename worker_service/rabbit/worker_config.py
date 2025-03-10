from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitConfig(BaseSettings):
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_LOCAL_HOST_NAME: str
    RABBITMQ_LOCAL_PORT: int
    WORKER_RABBITMQ_QUEUE: str

    @property
    def url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_DEFAULT_USER}:"
            f"{self.RABBITMQ_DEFAULT_PASS}@"
            f"{self.RABBITMQ_LOCAL_HOST_NAME}:"
            f"{self.RABBITMQ_LOCAL_PORT}/"
        )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent
        / ".env",  # Путь к файлу .env
        extra="ignore",  # Игнорировать лишние переменные окружения
    )


rabbit_config = RabbitConfig()
