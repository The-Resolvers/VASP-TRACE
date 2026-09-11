from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VASP Trace Engine"
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "vasp_trace"
    BLOCKCHAIR_API_KEY: str | None = None
    
    class Config:
        env_file = ".env"

settings = Settings()
