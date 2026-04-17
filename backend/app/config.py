from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-12-01-preview"

    azure_translator_key: str = ""
    azure_translator_region: str = "eastus"
    azure_translator_endpoint: str = "https://api.cognitive.microsofttranslator.com"

    google_factcheck_api_key: str = ""
    news_api_key: str = ""

    brightdata_api_token: str = ""
    brightdata_serp_zone: str = "serp_api1"

    external_http_timeout_seconds: float = 20.0
    external_http_retries: int = 3
    openai_timeout_seconds: float = 45.0
    openai_retries: int = 2
    qdrant_timeout_seconds: float = 20.0
    qdrant_retries: int = 2

    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384
    seed_data_path: str = "../data"

    model_config = {"env_file": ("../.env", ".env"), "extra": "ignore"}


settings = Settings()
