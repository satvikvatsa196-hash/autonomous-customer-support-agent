from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Customer Support Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # AI / LLM
    OPENAI_API_KEY: str = ""
    
    # JWT Auth Settings
    SECRET_KEY: str = "supersecretkey_for_internship_project_123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1 day
    
    # ChromaDB
    CHROMA_HOST: str = ""
    CHROMA_PORT: int = 8000
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
