import logging
from logging.handlers import TimedRotatingFileHandler
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

LOG_FORMAT = (
    "%(asctime)s | %(message)s"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))

# Tạo handler cho file
# File handler: xoay file theo ngày, giữ 7 ngày
file_handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",   # reset log lúc 00:00 mỗi ngày
    interval=1,
    backupCount=1,     # giữ tối đa 7 file log cũ
    encoding="utf-8",
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler],
)

logger = logging.getLogger("app")