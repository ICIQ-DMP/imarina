# Makefile for imarina-load-researchers
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
ifneq ($(shell command -v python3.14 2> /dev/null),)
    PYTHON_BIN ?= python3.14
else
    PYTHON_BIN ?= python
endif

VENV_DIR   ?= venv
VENV_BIN   ?= $(VENV_DIR)/bin
PYTHON     := $(VENV_BIN)/python
PIP        := $(VENV_BIN)/pip

PKG_NAME   := imarina_load_researchers
DOCKER_IMAGE := aleixmt/imarina-load-researchers

DEV_STAMP := $(VENV_DIR)/.dev-installed


# ---- helpers --------------------------------------------------------------

# Create virtualenv
$(VENV_BIN)/python:
	@$(PYTHON_BIN) -m venv "$(VENV_DIR)"
	@$(PYTHON_BIN) -m pip install --upgrade pip

# Install runtime dependencies (creates imarina-load-researchers executable)
$(VENV_BIN)/imarina-load-researchers: $(VENV_BIN)/python pyproject.toml
	@$(PIP) install -e .

# Install dev dependencies
# We use PKG-INFO as the target because pip updates it when dependencies change.
# This avoids the loop where 'make fmt && make lint' rebuilds twice because binaries
# like 'bin/ruff' might not have their timestamp updated by pip if they are already present.
$(DEV_STAMP): pyproject.toml $(VENV_BIN)/python
	@$(PIP) install -e "."
	@$(PIP) install -e ".[dev]"
	@touch $(DEV_STAMP)

.git/hooks/pre-commit: $(DEV_STAMP)
	@$(VENV_BIN)/pre-commit install

.git/hooks/commit-msg: $(DEV_STAMP)
	@$(VENV_BIN)/pre-commit install --hook-type commit-msg

.git/hooks/pre-push: $(DEV_STAMP)
	@$(VENV_BIN)/pre-commit install --hook-type pre-push

# Install build tool
$(VENV_BIN)/pyproject-build: $(VENV_BIN)/python
	@$(PIP) install build

# Phony aliases
venv: $(VENV_BIN)/python  ## Create virtualenv
	@echo "✅ venv ready at $(VENV_DIR)"

install: $(VENV_BIN)/imarina-load-researchers  ## Install package in editable mode

hooks: .git/hooks/pre-commit .git/hooks/commit-msg .git/hooks/pre-push  ## Install git hooks

dev: $(DEV_STAMP) hooks ## Install package and dev dependencies

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
run: install  ## Run the imarina-load-researchers CLI (python -m imarina_load_researchers)
	@$(PYTHON) -m $(PKG_NAME) $(CMD)

run-build: install
	@$(PYTHON) -m $(PKG_NAME) build --input-dir "services/onedrive/data/_Projects/imarina-load-researchers/runtime/input" --a3-input "services/onedrive/data/_Projects/imarina-load-researchers/runtime/a3/2026-07-17_12-00-00__listado_personal_A3.xlsx" --imarina-input "services/onedrive/data/_Projects/imarina-load-researchers/runtime/uploads/2026-07-27_12-00-00__icl_ag_personal_12539.xlsx


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
