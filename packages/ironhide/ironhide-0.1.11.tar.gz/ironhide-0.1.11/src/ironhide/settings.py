from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""
    default_model: str = "gpt-4o-mini"
    openai_audio_to_text_model_id: str = "whisper-1"

    # General
    log_level: str = ""
    timeout: int = 30


settings = Settings()
