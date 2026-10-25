import logging, logging.handlers
from pathlib import Path

_LOG_DIR  = Path("logs")
_FORMATTER = logging.Formatter("%(asctime)s  %(levelname)-8s  %(name)-28s  %(message)s", "%H:%M:%S")

def setup_logger(level: int = logging.INFO) -> None:
    _LOG_DIR.mkdir(exist_ok=True)
    root = logging.getLogger()
    root.setLevel(level)
    if root.handlers:
        return
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(_FORMATTER)
    root.addHandler(ch)
    fh = logging.handlers.RotatingFileHandler(_LOG_DIR/"genecraft.log", maxBytes=1_048_576, backupCount=3)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_FORMATTER)
    root.addHandler(fh)
    logging.getLogger("pygame").setLevel(logging.WARNING)
