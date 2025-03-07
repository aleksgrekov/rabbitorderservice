from pydantic_settings import BaseSettings


class Base(BaseSettings):
    RABBITMQ_DEFAULT_USER: str = "user"
    RABBITMQ_DEFAULT_PASS: str = "password"
    RABBITMQ_LOCAL_HOST_NAME: str = "localhost"
    RABBITMQ_LOCAL_PORT: int = 5672
    RABBITMQ_QUEUE: str = "orders_queue"

    @property
    def rabbit_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_DEFAULT_USER}:"
            f"{self.RABBITMQ_DEFAULT_PASS}@"
            f"{self.RABBITMQ_LOCAL_HOST_NAME}:"
            f"{self.RABBITMQ_LOCAL_PORT}/"
        )


base_config = Base()
