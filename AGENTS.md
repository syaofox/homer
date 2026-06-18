# Homer Project Guide

## Commands

```bash
# Run tests
uv run pytest

# Run tests with verbose
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=app

# Type checking
uv run mypy .

# Lint checking
uv run ruff check .

# Auto-fix lint issues
uv run ruff check --fix .

# Run the application
uv run python main.py

# Run data migration (JSON to SQLite)
uv run python migrate.py

# Update dependencies after changing pyproject.toml
uv lock && uv sync

# Add dev dependency
uv add --dev <package>
```

## Project Structure

- `app/` - Application package
  - `blueprints/main.py` - Route handlers
  - `core/validators.py` - Input validation functions
  - `services/db_service.py` - Database access layer
  - `database.py` - SQLite connection and schema
  - `config.py` - App configuration
  - `utils.py` - SVG icons, version, text utilities
- `main.py` - Entry point
- `migrate.py` - JSON → SQLite migration script
- `tests/` - Pytest test suite
- `config/` - Runtime data (db, images, JSON config)

## Coding Conventions

- Python 3.13+, strict mypy mode
- Use `dict`/`list` instead of `Dict`/`List`
- Use `X | None` instead of `Optional[X]`
- Use `collections.abc` types instead of `typing` equivalents
- Line length: 100
- All functions must have type annotations
- Tests use `conftest.py` for shared fixtures (temp database isolation)
