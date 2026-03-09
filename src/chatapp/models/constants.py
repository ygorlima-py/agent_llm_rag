from dotenv import load_dotenv
import os

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER', 'not found')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'not found')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'not found')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'not found')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 'not found')
TABLE_NAME = os.getenv('TABLE_NAME', 'not found')

CONNECTION_STRING = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}"
    f":{POSTGRES_PORT}/{POSTGRES_DB}"
)