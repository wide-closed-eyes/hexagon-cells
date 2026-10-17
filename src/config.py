from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    LAT_CENTER: float
    LNG_CENTER: float
    RADIUS_KM: float
    RESOLUTION: int

    model_config = SettingsConfigDict(env_file="test.env", extra="ignore")


config = Config()
