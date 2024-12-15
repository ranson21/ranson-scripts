.PHONY: help install deploy clean check-env

# Variables
PYTHON := python3
PIP := pip3
VENV := .venv
BIN := $(VENV)/bin
ACTIVATE := . $(VENV)/bin/activate

help:
	@echo "Available commands:"
	@echo "  make install    - Create virtual environment and install dependencies"
	@echo "  make deploy     - Deploy workflows to all repositories"
	@echo "  make clean      - Remove virtual environment and cached files"
	@echo "  make check-env  - Verify GitHub token is set"

check-env:
	@if [ -z "$(GITHUB_TOKEN)" ]; then \
		echo "Error: GITHUB_TOKEN is not set"; \
		echo "Please set it with: export GITHUB_TOKEN='your-token'"; \
		exit 1; \
	fi

$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip

install: $(VENV)
	$(BIN)/pip install PyGithub

deploy: check-env install
	$(BIN)/python deploy_workflows.py

clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf *.pyc