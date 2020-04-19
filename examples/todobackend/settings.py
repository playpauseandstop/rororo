import environ

from rororo.settings import BaseSettings


@environ.config(prefix=None, frozen=True)
class Settings(BaseSettings):
    redis_url: str = environ.var(
        name="REDIS_URL", default="redis://localhost:6379/0"
    )

    redis_data_key: str = environ.var(
        name="REDIS_DATA_KEY", default="rororo:todobackend"
    )
