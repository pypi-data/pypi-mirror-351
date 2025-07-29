run:
    uv run pystruction

test:
    uv run coverage run -m pytest

lint:
    uvx ruff check --fix

doclint:
    uvx ruff pydoclint src tests

type:
    uvx mypy --strict src tests
    uvx pyright

precommit:
    uvx pre-commit autoupdate --repo https://github.com/pre-commit/pre-commit-hooks
    uvx pre-commit autoupdate --repo https://github.com/astral-sh/ruff-pre-commit
    uvx pre-commit run --all-files
