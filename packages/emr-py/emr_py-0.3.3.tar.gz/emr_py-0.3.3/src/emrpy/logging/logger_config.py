"""High‑level logging utilities for **emrpy**.

Usage
=====
**In a Python script or CLI**
```python
# download_binance.py
from emrpy.logutils.logger_config import configure, get_logger

# One‑time global setup – matches old scripts_logger defaults
configure(
    level="INFO",
    log_dir="logs",                   # the same folder the old helper used
    filename="binance_dl.log",        # name it however you like
    rotate_bytes=2 * 1024 * 1024,     # 2 MB rotation
    backups=1,                        # keep one rotated backup
)

log = get_logger(__name__)            # anywhere in your codebase
log.info("This is information …")

```

**In a Jupyter notebook**
```python
from emrpy.logutils.logger_config import configure, get_logger

# console‑only: no file writes, no rotation
configure(level="INFO", rotate_bytes=0, backups=0)
log = get_logger(__name__)
log.info("Notebook cell executed ✔")
```

Public API
----------
- `get_logger(name="emrpy")` → Returns a namespaced logger seeded with a *NullHandler*.
- `configure(...)` → Attaches colourised console + (optional) rotating file handler(s) **without** mutating the root logger.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Union

try:
    # Multi‑process‑safe rotating handler; falls back if optional extra missing.
    from concurrent_log_handler import ConcurrentRotatingFileHandler as _RFH  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – optional dependency missing
    from logging.handlers import RotatingFileHandler as _RFH  # type: ignore

__all__ = [
    "get_logger",
    "configure",
]

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_FMT = "%(asctime)s %(levelname)s ▶ %(name)s: %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_DIR_ENV = "EMRPY_LOG_DIR"


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def get_logger(name: str = "emrpy") -> logging.Logger:
    """Return a namespaced logger seeded with :class:`logging.NullHandler`."""
    logger = logging.getLogger(name)
    if not any(isinstance(h, logging.NullHandler) for h in logger.handlers):
        logger.addHandler(logging.NullHandler())
    return logger


def _has_handler(logger: logging.Logger, handler_type: type) -> bool:
    """Check if *logger* already has a handler of *handler_type*."""
    return any(isinstance(h, handler_type) for h in logger.handlers)


def configure(
    name: str = "emrpy",
    *,
    level: int | str = logging.INFO,
    log_dir: Union[str, os.PathLike, None] | None = None,
    filename: str = "emrpy.log",
    rotate_bytes: int = 5_000_000,  # 5 MB (set to 0 to disable file handler)
    backups: int = 3,
    fmt: str = DEFAULT_FMT,
    datefmt: str = DEFAULT_DATEFMT,
    coloured_console: bool = True,
) -> logging.Logger:
    """Attach console + (optional) rotating file handler to *one* logger.

    Calling `configure()` more than once is a no‑op – handy in notebooks or
    multi‑import scenarios.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # -------------------------------------------------------------
    # Prevent duplicate configuration on subsequent calls.
    # -------------------------------------------------------------
    if _has_handler(logger, _RFH if rotate_bytes else logging.StreamHandler):
        return logger

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # ---------------------------- console ------------------------
    console = logging.StreamHandler()
    console.setLevel(level)
    if coloured_console:
        try:
            from colorlog import ColoredFormatter  # optional extra

            console.setFormatter(ColoredFormatter("%(log_color)s" + fmt, datefmt))
        except ModuleNotFoundError:
            console.setFormatter(formatter)
    else:
        console.setFormatter(formatter)
    logger.addHandler(console)

    # ---------------------------- file ---------------------------
    if rotate_bytes > 0:
        log_dir_path = Path(log_dir or os.getenv(DEFAULT_LOG_DIR_ENV, "logs")).expanduser()
        log_dir_path.mkdir(parents=True, exist_ok=True)

        file_handler = _RFH(
            filename=str(log_dir_path / filename),
            mode="a",
            maxBytes=rotate_bytes,
            backupCount=backups,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
