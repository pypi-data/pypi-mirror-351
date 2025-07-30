# h7-logger-manager

Core utility classes for logging management in Python projects.

## Installation

```bash
pip install h7-logger-manager
```

## Features

- Centralized logging configuration
- Automatic log file rotation
- Console and file logging
- Support for multiple named loggers
- Timestamp-based log file naming

## Usage

```python
from h7_logger_manager import LoggerManager

# Get default logger
logger = LoggerManager.setup_logger()

# Log messages at different levels
logger.debug("Debug message - only appears in log file")
logger.info("Info message - appears in console and log file")
logger.warning("Warning message")
logger.error("Error message")

# Create a custom named logger with specific file prefix
custom_logger = LoggerManager.setup_logger("my_module", "custom_prefix")
custom_logger.info("This goes to a separate log file")
```

## Requirements

- Python 3.7+
- h7-file-finder
- h7-env-manager

## License

MIT License - Copyright (c) 2025 Roger Mori
