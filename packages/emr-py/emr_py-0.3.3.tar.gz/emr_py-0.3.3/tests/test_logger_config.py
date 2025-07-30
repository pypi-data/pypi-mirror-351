"""Unit tests for emrpy.logutils.

Run with:
    pytest -q
"""

from __future__ import annotations

import logging
from pathlib import Path

from emrpy.logging import configure, get_logger

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _has_handler(logger: logging.Logger, typ: type) -> bool:  # pragma: no cover
    return any(isinstance(h, typ) for h in logger.handlers)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_get_logger_returns_null_handler():
    """Every namespaced logger must start with a NullHandler."""
    logger = get_logger("emrpy.test")
    assert _has_handler(logger, logging.NullHandler)


def test_configure_adds_console_once():
    """Repeated configure() calls should not duplicate handlers."""
    logger = configure(name="emrpy.test_console", rotate_bytes=0)
    console_count_first = sum(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    # Second call should be a no‑op
    configure(name="emrpy.test_console", rotate_bytes=0)
    console_count_second = sum(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    assert console_count_first == 1  # exactly one console handler
    assert console_count_second == console_count_first  # unchanged after repeat


def test_configure_is_idempotent(tmp_path: Path):
    """configure() should not add new handlers on subsequent calls."""
    log_dir = tmp_path / "logs"
    logger = configure(name="emrpy.idemp", log_dir=log_dir)
    handler_count = len(logger.handlers)

    # Re‑invoke with same parameters
    configure(name="emrpy.idemp", log_dir=log_dir)
    assert len(logger.handlers) == handler_count
