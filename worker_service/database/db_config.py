from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    """
    Класс для управления настройками подключения к базе данных Postgres.

    Все параметры, такие как хост, порт, имя пользователя, пароль и база данных,
    загружаются из переменных окружения или файла `.env`.
    """

    DB_HOST: str
    DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    def db_url(self, driver: Optional[str] = None) -> str:
        """
        Формирует строку URL для подключения к базе данных Postgres.

        :param driver: Необязательный параметр для указания драйвера подключения.
        :return: Строка, содержащая полный URL для подключения к базе данных Postgres.
        """
        # Формирование строки подключения с учетом драйвера (если указан)
        return "postgresql{driver}://{user}:{password}@{host}:{port}/{name}".format(
            driver=f"+{driver}" if driver else "",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            name=self.POSTGRES_DB,
        )

    # Настройки для загрузки из .env файла и игнорирования лишних переменных окружения
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent
        / ".env",  # Путь к .env файлу
        extra="ignore",  # Игнорировать переменные окружения, которых нет в классе
    )


db_settings: DBSettings = DBSettings()
