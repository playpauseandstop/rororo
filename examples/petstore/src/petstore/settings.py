import environ

from rororo import BaseSettings


@environ.config(prefix="", frozen=True)
class Settings(BaseSettings):
    pets_app_key: str = environ.var(name="PETS_APP_KEY", default="pets")
