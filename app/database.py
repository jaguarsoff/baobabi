from databases import Database
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings

database = Database(settings.database_url)
metadata = MetaData()
engine = create_engine(settings.database_url, future=True)
Base = declarative_base()

async def get_session():
    # for simple examples we will use Database queries directly
    return database
