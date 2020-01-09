import attr

from rororo import BaseSettings, env_factory


@attr.dataclass(frozen=True, slots=True)
class Settings(BaseSettings):
    pets_app_key: str = env_factory("PETS_APP_KEY", "pets")
