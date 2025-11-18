from pydantic import BaseSettings

class Settings(BaseSettings):
    bot_token: 8288012104:AAEy_eFaSjwG8DGBQaRPQGy2cG3pFpCzTqE
    admin_id: 8254985499
    database_url: str = 'sqlite+aiosqlite:///./poizon.db'
    class Config:
        env_file = '.env'

settings = Settings()
