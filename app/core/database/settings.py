from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str
    DB_PASSWORD: str
    DB_USERNAME: str
    DB_HOST: str
    DB_PORT: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


db_settings = Settings()
