from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ndonga_buzness API"
    debug: bool = True
    database_url: str = "sqlite:///./ndonga_buzness.db"
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = "change_me_to_a_long_random_value"
    whatsapp_app_secret: str = ""
    whatsapp_api_version: str = "v27.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
