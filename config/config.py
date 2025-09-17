# config/config.py
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import os, logging

load_dotenv(find_dotenv(filename=".env"), override=False)

def env(name, default=None, *, required=False, cast=str):
    v = os.getenv(name, default)
    if required and (v is None or v == ""):
        raise RuntimeError(f"{name} is required but missing")
    if v is None:
        return None
    if cast is bool:
        return str(v).lower() in {"1", "true", "yes", "on"}
    if cast is int:
        return int(v)
    return v  

DATABASE_URL = env("DATABASE_URL", required=True)
LOG_DIR = env("LOG_DIR", "")
LOG_NAME = env("LOG_NAME", "logs.log")
log_file_path = os.path.join(LOG_DIR, LOG_NAME)
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)

QUESTION_TEXT_MAX = 1000
ANSWER_TEXT_MAX = 10000