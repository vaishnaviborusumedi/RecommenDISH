from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "RecommenDISH"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=True, env="DEBUG")
    secret_key: str = Field(default="dev-secret", env="SECRET_KEY")

    database_url: str = Field(
        default="sqlite:///./recommandish.db",
        env="DATABASE_URL"
    )

    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    llm_model: str = "claude-sonnet-4-20250514"
    llm_max_tokens: int = 1024

    models_dir: str = "app/ml/saved_models"
    models_dir: str = "app/ml/saved_models"
    kmeans_model_path: str = "app/ml/saved_models/kmeans.joblib"
    scaler_path: str = "app/ml/saved_models/scaler.joblib"
    rules_path: str = "app/ml/saved_models/assoc_rules.joblib"
    n_recommendations: int = 5
    min_support: float = 0.05
    min_confidence: float = 0.3
    n_clusters: int = 5

    class Config:
        env_file = ".env"


settings = Settings()