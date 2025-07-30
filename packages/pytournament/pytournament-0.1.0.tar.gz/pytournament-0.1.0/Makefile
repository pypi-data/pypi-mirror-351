# Define the Python files to check
PYTHON_FILES = $(shell find ./src -name "*.py")

# Define the commands
MYPY = mypy
ISORT = isort
BLACK = black
RUFF = ruff
PRE_COMMIT = pre-commit

# Default target
.PHONY: format lint mypy pre-commit check clean test help

check: format lint mypy pre-commit test

# Run ruff format
format:
	$(RUFF) format .

# Run ruff check
lint:
	$(RUFF) check . --fix

# Run mypy
mypy:
	$(MYPY) .

# Clean up any temporary files (optional)
clean:
	find . -name "*.pyc" -delete

# Run tests
test:
	pytest --cov=src --cov-report=term-missing

.PHONY: pre-commit
pre-commit:
	$(PRE_COMMIT) run --all-files
