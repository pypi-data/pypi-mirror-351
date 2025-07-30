# EMR-Py

A collection of utilities for now to:
- encode data.
- logging.
- Integrating with Telegram bots—designed for use in trading and data science workflows.

---

## Project Structure

```
src/emrpy/
    encoders.py           # Utilities for encoding categorical data using scikit-learn
    decorators.py         # Function decorators for timing and memory profiling
    telegrambot.py        # Async Telegram bot for sending trading notifications
    logging/
        logger_config.py  # High-level logger configuration utilities
tests/
    test_encoders.py      # Unit tests for encoding functionality
    test_logger_config.py # Unit tests for logger configuration
    test_telegram_bot.py  # Integration tests for the Telegram bot
.github/
    actions/
        setup/action.yml  # Custom GitHub Action for installing dependencies
    workflows/
        code-quality.yml  # CI workflow for formatting, linting, and testing
```

---

## Main Functionalities

- **Data Encoding** (`encoders.py`):
  Provides a robust function to encode categorical columns in pandas DataFrames using `sklearn`'s `OrdinalEncoder`, with special handling for unknown and missing values.

- **Decorators** (`decorators.py`):
  Includes decorators to measure function execution time and memory usage, useful for profiling and debugging.

- **Telegram Trading Bot** (`telegrambot.py`):
  An async-first Telegram bot to send trading notifications, alerts, and bulk messages, with error handling and logging built-in. Uses the `python-telegram-bot` library.

- **Logging Utilities** (`logging/logger_config.py`):
  Easy-to-configure, colored, and optionally rotating log files, suitable for both scripts and Jupyter notebooks.
