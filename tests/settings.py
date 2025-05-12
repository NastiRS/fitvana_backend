from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    TEST_DB_USERNAME: str
    TEST_DB_PASSWORD: str
    TEST_DB_HOST: str
    TEST_DB_PORT: str
    TEST_DB_NAME: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


test_db_settings = TestSettings()
