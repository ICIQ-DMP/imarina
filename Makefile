# Makefile for imarina
# Usage examples:
#   make venv
#   make lint
#   make fmt
#   make test
#   make run CMD="run -f demo.nds --debug"
#   make clean

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c


# ---- config ---------------------------------------------------------------

# Check if python3.11 exists, otherwise default to python
ifneq ($(shell command -v python3.11 2> /dev/null),)
    PYTHON_BIN ?= python3.11
else
    PYTHON_BIN ?= python
endif

VENV_DIR   ?= venv
VENV_BIN   ?= $(VENV_DIR)/bin
PYTHON     := $(VENV_BIN)/python
PIP        := $(VENV_BIN)/pip

PKG_NAME   := imarina
DOCKER_IMAGE := mariopique/imarina-load

DEV_STAMP := $(VENV_DIR)/.dev-installed


# ---- helpers --------------------------------------------------------------

# Create virtualenv
$(VENV_BIN)/python:
	@$(PYTHON_BIN) -m venv "$(VENV_DIR)"
	@$(PYTHON_BIN) -m pip install --upgrade pip

# Install runtime dependencies (creates imarina executable)
$(VENV_BIN)/imarina: $(VENV_BIN)/python pyproject.toml
	@$(PIP) install -e .

# Install dev dependencies
# We use PKG-INFO as the target because pip updates it when dependencies change.
# This avoids the loop where 'make fmt && make lint' rebuilds twice because binaries
# like 'bin/ruff' might not have their timestamp updated by pip if they are already present.
$(DEV_STAMP): pyproject.toml $(VENV_BIN)/python
	@$(PIP) install -e "."
	@$(PIP) install -e ".[dev]"
	@touch $(DEV_STAMP)

# Install build tool
$(VENV_BIN)/pyproject-build: $(VENV_BIN)/python
	@$(PIP) install build

# Phony aliases
venv: $(VENV_BIN)/python  ## Create virtualenv
	@echo "✅ venv ready at $(VENV_DIR)"

install: $(VENV_BIN)/imarina  ## Install package in editable mode

dev: $(DEV_STAMP)  ## Install package and dev dependencies

# ---- quality --------------------------------------------------------------

lint: dev  ## Run static checks (ruff + mypy)
	@$(VENV_BIN)/ruff check .
	@$(VENV_BIN)/mypy src

fmt: dev  ## Auto-format (black + ruff --fix)
	@$(VENV_BIN)/black src tests
	@$(VENV_BIN)/ruff check --fix .

test: dev  ## Run tests
	@PYTHONPATH=src PYTHONUNBUFFERED=1 $(VENV_BIN)/pytest -s -v

# ---- run ------------------------------------------------------------------

# Pass arguments to the CLI via CMD, e.g.:
#   make run CMD="run -f demo.nds --debug"
CMD ?= --help
run: install  ## Run the imarina CLI (python -m imarina)
	@$(PYTHON) -m $(PKG_NAME) $(CMD)

# ---- docker ---------------------------------------------------------------

docker-build:  ## Build the Docker image
	@sudo docker build . -t $(DOCKER_IMAGE) --progress=plain

docker-push:  ## Push the Docker image
	@sudo docker push $(DOCKER_IMAGE)

# ---- maintenance ----------------------------------------------------------

clean:  ## Remove build/test artifacts
	@rm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info "$(VENV_DIR)"

# ---- meta -----------------------------------------------------------------

.PHONY: lint fmt test run clean help dist install docker-build docker-push

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .+$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
