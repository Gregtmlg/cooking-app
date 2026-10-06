from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cooking App"
    debug: bool = False
    database_url: str = "sqlite:///./cooking.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # Cookie de session transmis uniquement sur HTTPS.
    # True par défaut (prod) ; surchargé à False en dev via .env si le cookie
    # ne se pose pas sur http://localhost.
    session_cookie_secure: bool = True


settings = Settings()
