import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the app folder if present (local development convenience)
env_path = Path(__file__).resolve().parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Fallbacks if env vars are not set
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/rickmorty')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
RICK_API_BASE = os.getenv('RICK_API_BASE', 'https://rickandmortyapi.com/api')
RATE_LIMIT = os.getenv('RATE_LIMIT', '100/minute')

# Pagination defaults
try:
    PAGE_SIZE = int(os.getenv('PAGE_SIZE', '50'))
except ValueError:
    PAGE_SIZE = 50

# Secret key (if your app uses sessions)
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-me-in-prod')