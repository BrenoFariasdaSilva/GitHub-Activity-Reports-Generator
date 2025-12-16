# Variables
VENV := venv
OS := $(shell uname 2>/dev/null || echo Windows)

# Detect correct Python and Pip commands based on OS
ifeq ($(OS), Windows) # Windows
	PYTHON := $(VENV)/Scripts/python.exe
	PIP := $(VENV)/Scripts/pip.exe
	PYTHON_CMD := python
	CLEAR_CMD := cls
	TIME_CMD :=
else # Unix-like
	PYTHON := $(VENV)/bin/python3
	PIP := $(VENV)/bin/pip
	PYTHON_CMD := python3
	CLEAR_CMD := clear
	TIME_CMD := time
endif

# Default date range (can be overridden from CLI)
SINCE ?= 2000-01-01
ifeq ($(OS), Windows)
UNTIL ?= $(shell powershell -command "Get-Date -Format 'yyyy-MM-dd'")
else
UNTIL ?= $(shell date +%Y-%m-%d)
endif

# Main target that runs the scripts
all: run

# Main Scripts:
run: dependencies
	$(CLEAR_CMD)
	$(TIME_CMD) $(PYTHON) ./main.py --since $(SINCE) --until $(UNTIL)

# Create virtual environment if missing
$(VENV):
	@echo "Creating virtual environment..."
	$(PYTHON_CMD) -m venv $(VENV)

dependencies: $(VENV)
	@echo "Installing/Updating Python dependencies..."
	$(PIP) install --upgrade -r requirements.txt

# Generate requirements.txt from current venv
generate_requirements: $(VENV)
	$(PIP) freeze > requirements.txt

# Clean artifacts
clean:
	rm -rf $(VENV) || rmdir /S /Q $(VENV) 2>nul
	find . -type f -name '*.pyc' -delete || del /S /Q *.pyc 2>nul
	find . -type d -name '__pycache__' -delete || rmdir /S /Q __pycache__ 2>nul

.PHONY: all run clean dependencies generate_requirements
