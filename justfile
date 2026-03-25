# List all available commands:
default:
    @just --list

# install dependencies and sync the lockfile
install:
    uv sync


# code checks
check: lint format-check type-check

lint:
    uv run ruff check .

lint-fix:
    uv run ruff check . --fix

# proper formatting
format-check:
    uv run ruff format . --check

format:
    uv run ruff format .

# static check with mypy
type-check:
    uv run ruff check . 
    uv run mypy .

# TESTING
test:
    uv run pytest tests/

# DEVELOPMENT
api:
    uv run uvicorn api.main:app --reload --port 8000

ui:
    uv run streamlit run ui/app.py 

local-setup:
    docker-compose up -d

# CLEANUP
clean:
    rm -rf .venv .mypy_cache .pytest_cache build/ dist/ *.egg-info
    find . -type d -name "__pycache__" -exec rm -rf {} +
