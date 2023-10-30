from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_DATABASE: str

config = Settings(_env_file=".env")
