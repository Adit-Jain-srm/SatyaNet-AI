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

    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384
    seed_data_path: str = "../data"

    model_config = {"env_file": ("../.env", ".env"), "extra": "ignore"}


settings = Settings()
