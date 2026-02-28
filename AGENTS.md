# AGENTS.md - Agent Coding Guidelines for Homer

## Project Overview

Homer is a Flask-based web application providing a navigation dashboard with configuration management. It uses Python 3.13+, SQLite database, and can be run via Docker or directly with Python.

## Environment Management

- **Tool**: [uv](https://docs.astral.sh/uv/) for Python virtual environment and dependency management
- **Version**: uv 0.9.11+
- **Always use `uv run` prefix** for any Python command execution

## Build/Development Commands

```bash
# Sync dependencies from pyproject.toml
uv sync

# Run the Flask application
uv run python main.py

# Run Flask in debug mode (development)
uv run flask run --debug
```

### Linting & Formatting

```bash
# Run ruff linter (checks code quality)
uvx ruff check .

# Run ruff with auto-fix
uvx ruff check . --fix

# Run ruff formatter
uvx ruff format .
```

### Testing

```bash
# Run all tests with pytest
uv run pytest

# Run a single test file
uv run pytest tests/test_file.py

# Run a specific test function
uv run pytest tests/test_file.py::test_function_name

# Run tests with verbose output
uv run pytest -v

# Run tests matching a pattern
uv run pytest -k "test_pattern"
```

## Code Style Guidelines

### Imports
Order imports in each file:
1. Standard library
2. Third-party packages
3. Local application imports

```python
# Standard library
import json
import os
from pathlib import Path
from typing import Any, Optional, Dict, List

# Third-party
import aiosqlite
from flask import Blueprint, render_template

# Local
from app.config import config as app_config
from app.services import db_service
```

### Naming Conventions
- **Functions/variables**: snake_case (e.g., `get_version()`, `db_path`)
- **Classes**: PascalCase (e.g., `Database`, `AppConfig`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_CONTENT_LENGTH`)
- **Private members**: prefix with underscore (e.g., `_ensure_db_dir()`)

### Type Hints
Always use type hints for function parameters and return values:
```python
def get_version() -> str:
    ...

def init_db(db_path: Optional[str] = None) -> None:
    ...
```

### Docstrings
Use docstrings for all public functions and classes. Chinese documentation is acceptable:
```python
def get_db() -> Database:
    """获取数据库实例的便捷函数"""
    ...
```

### Error Handling
- Use try/except with proper logging
- Re-raise exceptions after logging
- Return appropriate HTTP status codes in Flask routes

```python
try:
    return f(*args, **kwargs)
except FileNotFoundError as e:
    logger.error(f"文件未找到: {e}")
    return jsonify({"error": "配置文件未找到"}), 404
except Exception as e:
    logger.error(f"未知错误: {e}")
    return jsonify({"error": "服务器内部错误"}), 500
```

### Logging
Use module-level loggers:
```python
logger = logging.getLogger(__name__)
```

### Async Code
- Use `aiosqlite` for async database operations
- Use `async def` and `await` appropriately
- Keep sync and async code separate

### Database
- Use context managers for database connections:
```python
@contextmanager
def get_cursor(self):
    conn = self.connection
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        cursor.close()
```

### Flask Routes
- Use blueprints for route organization
- Apply error handlers as decorators
- Return JSON with proper status codes for API endpoints

### Configuration
- Use environment variables for configuration
- Provide sensible defaults
- Validate configuration on startup

## Project Structure

```
homer/
├── app/
│   ├── __init__.py        # Flask app initialization
│   ├── config.py          # Configuration management
│   ├── database.py        # Database management class
│   ├── utils.py           # Utility functions
│   ├── blueprints/        # Flask blueprints
│   ├── core/              # Core business logic
│   ├── services/         # Service layer
│   ├── static/            # Static assets
│   └── templates/         # Jinja2 templates
├── config/                # Configuration files (runtime)
├── main.py                # Application entry point
├── migrate.py             # Data migration script
└── pyproject.toml         # Project dependencies
```

## Key Dependencies

- Flask 3.1.0+ - Web framework
- aiosqlite 0.22.0+ - Async SQLite
- waitress 2.1.2+ - Production WSGI server
- pypinyin 0.54.0+ - Chinese pinyin conversion
- ruff - Linting (run via uvx)

## Docker Development

```bash
# Build Docker image
docker build -t homer .

# Run container
docker run -d -p 8080:8080 -v ./config:/config homer
```
