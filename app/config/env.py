from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = Field(default="Sistema Inteligente de Atencion al Cliente")
    APP_VERSION: str = Field(default="0.1.0")
    APP_ENV: Literal["local", "dev", "test", "prod"] = Field(default="local")

    API_HOST: str = Field(default="127.0.0.1")
    API_PORT: int = Field(default=3001)

    AI_MODE: Literal["mock", "openai"] = Field(default="mock")
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-5.4-mini")
    OPENAI_MAX_OUTPUT_TOKENS: int = Field(default=500)
    OPENAI_TIMEOUT_SECONDS: int = Field(default=30)
    AI_USE_OPENAI_ANALYSIS: bool = Field(default=False)
    AI_USE_OPENAI_REPLY: bool = Field(default=False)

    DATABASE_URL: str = Field(default="sqlite:///./app/data/customer_service.sqlite3")

    MAX_INPUT_CHARS: int = Field(default=2000)
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    CORS_ORIGINS: str = Field(default="*")

    @property
    def is_openai_enabled(self) -> bool:
        return self.AI_MODE == "openai"

    @property
    def should_use_openai_analysis(self) -> bool:
        return self.AI_MODE == "openai" and self.AI_USE_OPENAI_ANALYSIS

    @property
    def should_use_openai_reply(self) -> bool:
        return self.AI_MODE == "openai" and self.AI_USE_OPENAI_REPLY

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]

        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()
