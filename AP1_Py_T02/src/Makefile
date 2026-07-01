.PHONY: help venv install install-dev task1 task2 fmt lint check clean
VENV_DIR = venv

# Определение переменных в зависимости от ОС
ifeq ($(OS),Windows_NT)
    # Windows
    VENV_PIP = $(VENV_DIR)\Scripts\pip
    VENV_PY = $(VENV_DIR)\Scripts\python
    VENV_ACTIVATE = $(VENV_DIR)\Scripts\activate
    PYTHON = python
    PATH_SEP = \\
    RMDIR = rmdir /s /q
    NULL_REDIR = 2>nul || ver >nul
    COMMAND_CHECK = where
else
    # Linux/macOS
    OS_NAME = $(shell uname)
    ifeq ($(OS_NAME),Linux)
        VENV_PIP = $(VENV_DIR)/bin/pip
        VENV_PY = $(VENV_DIR)/bin/python
        VENV_ACTIVATE = $(VENV_DIR)/bin/activate
        PYTHON = python3
        PATH_SEP = /
        RMDIR = rm -rf
        NULL_REDIR = 2>/dev/null || true
        COMMAND_CHECK = command -v
    endif
    ifeq ($(OS_NAME),Darwin)
        VENV_PIP = $(VENV_DIR)/bin/pip
        VENV_PY = $(VENV_DIR)/bin/python
        VENV_ACTIVATE = $(VENV_DIR)/bin/activate
        PYTHON = python3
        PATH_SEP = /
        RMDIR = rm -rf
        NULL_REDIR = 2>/dev/null || true
        COMMAND_CHECK = command -v
    endif
endif

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(VENV_PY) -m pip install -U pip
	$(VENV_PIP) install -r requirements.txt

install-dev: install
	$(VENV_PIP) install -U ruff black

task1: install-dev
	$(VENV_PY) exercise1/main.py

task2: install-dev
	$(VENV_PY) exercise2/main.py

fmt: install-dev
	@$(COMMAND_CHECK) $(VENV_PY) $(NULL_REDIR) || (echo "Error: Python not found in venv" && exit 1)
	$(VENV_PY) -m black exercise1 exercise2

lint: install-dev
	@$(COMMAND_CHECK) $(VENV_PY) $(NULL_REDIR) || (echo "Error: Python not found in venv" && exit 1)
	$(VENV_PY) -m ruff check exercise1 exercise2

check: fmt lint

clean:
	@$(RMDIR) venv $(NULL_REDIR)
	@$(RMDIR) .ruff_cache $(NULL_REDIR)
	@$(RMDIR) exercise1$(PATH_SEP)__pycache__ $(NULL_REDIR)
	@$(RMDIR) exercise2$(PATH_SEP)__pycache__ $(NULL_REDIR)
	@echo "OK"

# Справка
help:
	@echo "Available commands:"
	@echo "  make venv         - Create virtual environment"
	@echo "  make install      - Install requirements"
	@echo "  make install-dev  - Install dev dependencies (ruff, black)"
	@echo "  make task1        - Run task1"
	@echo "  make task2        - Run task2"
	@echo "  make fmt          - Format code with black"
	@echo "  make lint         - Lint code with ruff"
	@echo "  make check        - Run fmt and lint"
	@echo "  make clean        - Clean up generated files"