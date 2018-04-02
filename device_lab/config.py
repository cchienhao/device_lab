import os
import logging

from sqlalchemy.engine.url import URL
from utils.misc import new_random_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 8888))
DEBUG_MODE = os.environ.get("MODE", "PROD") == "DEBUG"

DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME", "device_lab")

DB_URL = URL(
    drivername="mysql+pymysql",
    host=DB_HOST,
    username=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)

STATIC_PATH = os.environ.get("STATIC_PATH", os.path.join(os.path.dirname(__file__), "static"))

TORNADO_SETTINGS = {
    "static_path": STATIC_PATH,
    "debug": DEBUG_MODE,
}

API_BASE_URL = os.environ.get('API_BASE_URL', r'/device_lab/api/v1/')
STATIC_BASE_URL = os.environ.get('STATIC_BASE_URL', r'/device_lab/static/')


# service related configure
LOCK_SECRET = os.environ.get("LOCK_SECRET", new_random_string(20))
