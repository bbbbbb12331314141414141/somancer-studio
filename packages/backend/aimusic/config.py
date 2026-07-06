"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment."""

    # Database
    database_url: str = "sqlite:///./sonmancer.db"

    # Ollama
    ollama_host: str = "http://localhost:11434"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Logging
    log_level: str = "INFO"
    debug: bool = False

    # Environment
    environment: str = "development"

    # Audio
    audio_sample_rate: int = 48000
    audio_bit_depth: int = 24
    audio_buffer_size: int = 2048

    # GPU
    cuda_enabled: bool = False
    gpu_memory_gb: int = 8

    # Paths
    projects_dir: str = "./projects"
    exports_dir: str = "./exports"
    temp_dir: str = "./tmp"
    soundfont_dir: str = "./soundfonts"

    # Feature flags
    enable_ai: bool = True
    enable_audio: bool = True
    enable_plugins: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
