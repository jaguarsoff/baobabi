from pydantic import BaseSettings

class Settings(BaseSettings):
    bot_token: str
    admin_id: int | None = None
    database_url: str = 'sqlite+aiosqlite:///./poizon.db'
    class Config:
        env_file = '.env'

settings = Settings()
