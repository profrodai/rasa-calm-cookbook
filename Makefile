# Terminal colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)
BLUE   := $(shell tput -Txterm setaf 4)
RED    := $(shell tput -Txterm setaf 1)

# Project settings
PYTHON_VERSION := 3.11
VENV_NAME := .venv
PROJECT_NAME := rasa-calm-cookbook
REPO_ROOT := $(shell pwd)
PYTHON := $(REPO_ROOT)/$(VENV_NAME)/bin/python
UV := $(shell which uv)

# Recipe settings
RECIPE_LEVELS := level-1-basic level-2-intermediate level-3-advanced
RECIPE_TARGET ?= basic-tutorial
RECIPE_LEVEL ?= level-1-basic
RECIPE_PATH := recipes/$(RECIPE_LEVEL)/$(RECIPE_TARGET)

# Test settings
PYTEST_ARGS ?= -v
COVERAGE_THRESHOLD := 85

help: ## Show this help message
	@echo ''
	@echo '${YELLOW}Rasa CALM Cookbook - Development Guide${RESET}'
	@echo ''
	@echo '${YELLOW}Quick Start:${RESET}'
	@echo '  Setup:        ${GREEN}make setup${RESET}              - Create venv + install Rasa + dev tools + basic deps'
	@echo '  Recipe:       ${GREEN}make recipe RECIPE_TARGET=basic-tutorial${RESET} - Work with specific recipe'
	@echo '  Activate:     ${GREEN}source .venv/bin/activate${RESET} - Activate environment'
	@echo ''
	@echo '${YELLOW}Recipe Management:${RESET}'
	@echo '  List:         ${GREEN}make list-recipes${RESET}       - Show all available recipes'
	@echo '  Validate:     ${GREEN}make validate-recipe${RESET}    - Validate recipe structure'
	@echo '  Test Recipe:  ${GREEN}make test-recipe${RESET}        - Test specific recipe'
	@echo '  New Recipe:   ${GREEN}make new-recipe RECIPE_TARGET=my-recipe RECIPE_LEVEL=level-1-basic${RESET}'
	@echo ''
	@echo '${YELLOW}Rasa Commands:${RESET}'
	@echo '  Train:        ${GREEN}make train${RESET}              - Train Rasa model in current recipe'
	@echo '  Shell:        ${GREEN}make shell${RESET}              - Start Rasa shell'
	@echo '  Inspect:      ${GREEN}make inspect${RESET}            - Start Rasa inspector'
	@echo '  Run:          ${GREEN}make run${RESET}                - Start Rasa server'
	@echo '  Test E2E:     ${GREEN}make test-e2e${RESET}           - Run end-to-end tests'
	@echo ''
	@echo '${YELLOW}Development:${RESET}'
	@echo '  Format:       ${GREEN}make format${RESET}             - Format all code'
	@echo '  Lint:         ${GREEN}make lint${RESET}               - Run linters'
	@echo '  Test:         ${GREEN}make test${RESET}               - Run all tests'
	@echo '  Clean:        ${GREEN}make clean${RESET}              - Clean build artifacts'
	@echo ''
	@echo '${YELLOW}Available Targets:${RESET}'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${YELLOW}%-15s${GREEN}%s${RESET}\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''

# Environment setup
.PHONY: check-uv
check-uv: ## Check if uv is installed
	@if ! command -v uv > /dev/null 2>&1; then \
	  echo "${RED}Error: uv is not installed. Please install it first:${RESET}"; \
	  echo "curl -LsSf https://astral.sh/uv/install.sh | sh"; \
	  exit 1; \
	fi
	@echo "${GREEN}✓ uv is installed${RESET}"

.PHONY: env
env: check-uv ## Create virtual environment using uv
	@echo "${BLUE}Creating virtual environment with Python $(PYTHON_VERSION)...${RESET}"
	$(UV) venv --python $(PYTHON_VERSION)
	@echo "${GREEN}Virtual environment created. Activate it with:${RESET}"
	@echo "source $(VENV_NAME)/bin/activate"

.PHONY: install-core
install-core: ## Install core Rasa dependencies
	@echo "${BLUE}Installing core Rasa dependencies...${RESET}"
	@if [ ! -f "$(PYTHON)" ]; then \
	  echo "${YELLOW}Virtual environment not found. Creating it first...${RESET}"; \
	  make env; \
	fi
	$(UV) pip install rasa-pro rasa-sdk --python $(REPO_ROOT)/$(VENV_NAME)/bin/python
	@echo "${GREEN}Core dependencies installed successfully${RESET}"

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "${BLUE}Installing development dependencies...${RESET}"
	$(UV) pip install pytest pytest-cov pytest-asyncio ruff mypy isort black pre-commit --python $(REPO_ROOT)/$(VENV_NAME)/bin/python
	@echo "${GREEN}Development dependencies installed successfully${RESET}"

.PHONY: install-basic
install-basic: ## Install basic recipe dependencies
	@echo "${BLUE}Installing basic recipe dependencies...${RESET}"
	$(UV) pip install openai --python $(REPO_ROOT)/$(VENV_NAME)/bin/python
	@echo "${GREEN}Basic dependencies installed successfully${RESET}"

.PHONY: install-intermediate
install-intermediate: ## Install intermediate recipe dependencies
	@echo "${BLUE}Installing intermediate recipe dependencies...${RESET}"
	@echo "${YELLOW}Note: Skipping pyaudio (requires system libraries)${RESET}"
	@echo "For full voice support, run: ${GREEN}make install-system-deps && make install-voice-full${RESET}"
	$(UV) pip install openai websockets aiohttp faiss-cpu qdrant-client pymilvus sentence-transformers --python $(REPO_ROOT)/$(VENV_NAME)/bin/python
	@echo "${GREEN}Intermediate dependencies installed successfully${RESET}"

.PHONY: install-voice-full
install-voice-full: ## Install full voice dependencies (requires system libraries)
	@echo "${BLUE}Installing full voice dependencies...${RESET}"
	$(UV) pip install websockets aiohttp pyaudio --python $(REPO_ROOT)/$(VENV_NAME)/bin/python
	@echo "${GREEN}Full voice dependencies installed${RESET}"

.PHONY: install-advanced
install-advanced: ## Install advanced recipe dependencies
	@echo "${BLUE}Installing advanced recipe dependencies...${RESET}"
	$(UV) pip install openai azure-cognitiveservices-speech azure-storage-blob websockets aiohttp \
		faiss-cpu qdrant-client pymilvus sentence-transformers docker kubernetes redis psycopg2-binary \
		--python $(REPO_ROOT)/$(VENV_NAME)/bin/python
	@echo "${GREEN}Advanced dependencies installed successfully${RESET}"

.PHONY: install-all
install-all: ## Install all dependencies
	@echo "${BLUE}Installing all dependencies...${RESET}"
	@echo "${YELLOW}Note: Voice dependencies (pyaudio) require system libraries${RESET}"
	@echo "If installation fails, run: ${GREEN}make install-system-deps${RESET}"
	$(UV) pip install rasa-pro rasa-sdk openai azure-cognitiveservices-speech azure-storage-blob \
		websockets aiohttp faiss-cpu qdrant-client pymilvus sentence-transformers \
		docker kubernetes redis psycopg2-binary \
		pytest pytest-cov pytest-asyncio ruff mypy isort black pre-commit \
		--python $(REPO_ROOT)/$(VENV_NAME)/bin/python || \
	(echo "${RED}Installation failed. Try: make install-system-deps${RESET}" && exit 1)
	@echo "${GREEN}All dependencies installed successfully${RESET}"

.PHONY: install-system-deps
install-system-deps: ## Install system-level dependencies for voice support
	@echo "${BLUE}Installing system dependencies...${RESET}"
	@if command -v brew >/dev/null 2>&1; then \
		echo "Installing PortAudio via Homebrew..."; \
		brew install portaudio; \
	elif command -v apt-get >/dev/null 2>&1; then \
		echo "Installing PortAudio via apt-get..."; \
		sudo apt-get update && sudo apt-get install -y portaudio19-dev; \
	else \
		echo "${YELLOW}Could not detect package manager.${RESET}"; \
		echo "Please install PortAudio manually:"; \
		echo "  macOS: brew install portaudio"; \
		echo "  Ubuntu/Debian: sudo apt-get install portaudio19-dev"; \
		echo "  Fedora: sudo dnf install portaudio-devel"; \
		exit 1; \
	fi
	@echo "${GREEN}System dependencies installed${RESET}"
	@echo "${YELLOW}Now run: make install-all${RESET}"

.PHONY: setup
setup: ## Create environment and install development dependencies
	@echo "${BLUE}Setting up complete development environment...${RESET}"
	make env
	make install-core
	make install-dev
	make install-basic
	@echo ""
	@echo "${GREEN}Setup complete! Development environment ready.${RESET}"
	@echo "${YELLOW}To activate the environment, run:${RESET}"
	@echo "  ${GREEN}source .venv/bin/activate${RESET}"
	@echo ""
	@echo "${YELLOW}To work with a specific recipe:${RESET}"
	@echo "  ${GREEN}make recipe RECIPE_TARGET=basic-tutorial${RESET}"

.PHONY: check-env
check-env: ## Check if virtual environment is active and working
	@echo "${BLUE}Checking environment...${RESET}"
	@if [ ! -f "$(PYTHON)" ]; then \
	  echo "${RED}Virtual environment not found at $(PYTHON)${RESET}"; \
	  echo "Run 'make setup' first"; \
	  exit 1; \
	fi
	@echo "Python: $(PYTHON)"
	@$(PYTHON) --version
	@$(PYTHON) -c "import sys; print(f'Python executable: {sys.executable}')"
	@if $(PYTHON) -c "import rasa" 2>/dev/null; then \
	  echo "${GREEN}✓ Rasa is installed${RESET}"; \
	  $(PYTHON) -c "import rasa; print(f'Rasa version: {rasa.__version__}')"; \
	else \
	  echo "${YELLOW}⚠ Rasa not found - run 'make install-core' first${RESET}"; \
	fi
	@echo "${GREEN}Environment check complete${RESET}"

# Recipe management
.PHONY: list-recipes
list-recipes: ## List all available recipes
	@echo "${BLUE}Available Recipes:${RESET}"
	@echo ""
	@for level in $(RECIPE_LEVELS); do \
	  echo "${YELLOW}$$level:${RESET}"; \
	  if [ -d "recipes/$$level" ]; then \
	    for recipe in recipes/$$level/*/; do \
	      if [ -d "$$recipe" ]; then \
	        recipe_name=$$(basename "$$recipe"); \
	        if [ -f "$$recipe/README.md" ]; then \
	          description=$$(head -n 5 "$$recipe/README.md" | grep -E "^#|description" | head -n 1 | sed 's/^#*[[:space:]]*//'); \
	          echo "  ${GREEN}$$recipe_name${RESET} - $$description"; \
	        else \
	          echo "  ${GREEN}$$recipe_name${RESET}"; \
	        fi; \
	      fi; \
	    done; \
	  fi; \
	  echo ""; \
	done

.PHONY: recipe
recipe: ## Work with a specific recipe (usage: make recipe RECIPE_TARGET=basic-tutorial)
	@if [ ! -d "$(RECIPE_PATH)" ]; then \
	  echo "${RED}Recipe '$(RECIPE_TARGET)' not found in '$(RECIPE_LEVEL)'${RESET}"; \
	  echo "Available recipes:"; \
	  make list-recipes; \
	  exit 1; \
	fi
	@echo "${BLUE}Working with recipe: $(RECIPE_TARGET)${RESET}"
	@echo "Recipe path: $(RECIPE_PATH)"
	@echo ""
	@echo "${YELLOW}Recipe commands:${RESET}"
	@echo "  ${GREEN}cd $(RECIPE_PATH)${RESET}"
	@echo "  ${GREEN}make setup-recipe${RESET}        - Install recipe dependencies"
	@echo "  ${GREEN}make train${RESET}               - Train the model"
	@echo "  ${GREEN}make inspect${RESET}             - Start inspector"
	@echo "  ${GREEN}make test-e2e${RESET}            - Run E2E tests"

.PHONY: validate-recipe
validate-recipe: ## Validate recipe structure
	@if [ ! -d "$(RECIPE_PATH)" ]; then \
	  echo "${RED}Recipe '$(RECIPE_TARGET)' not found${RESET}"; \
	  exit 1; \
	fi
	@echo "${BLUE}Validating recipe: $(RECIPE_TARGET)${RESET}"
	@error_count=0; \
	for required_file in README.md pyproject.toml domain.yml data/flows.yml; do \
	  if [ ! -f "$(RECIPE_PATH)/$$required_file" ]; then \
	    echo "${RED}✗ Missing required file: $$required_file${RESET}"; \
	    error_count=$$((error_count + 1)); \
	  else \
	    echo "${GREEN}✓ Found: $$required_file${RESET}"; \
	  fi; \
	done; \
	if [ $$error_count -eq 0 ]; then \
	  echo "${GREEN}✓ Recipe structure is valid${RESET}"; \
	else \
	  echo "${RED}✗ Recipe validation failed with $$error_count errors${RESET}"; \
	  exit 1; \
	fi

.PHONY: new-recipe
new-recipe: ## Create a new recipe (usage: make new-recipe RECIPE_TARGET=my-recipe RECIPE_LEVEL=level-1-basic)
	@if [ -d "$(RECIPE_PATH)" ]; then \
	  echo "${RED}Recipe '$(RECIPE_TARGET)' already exists${RESET}"; \
	  exit 1; \
	fi
	@echo "${BLUE}Creating new recipe: $(RECIPE_TARGET)${RESET}"
	@mkdir -p "$(RECIPE_PATH)"
	@mkdir -p "$(RECIPE_PATH)/data"
	@mkdir -p "$(RECIPE_PATH)/actions"
	@mkdir -p "$(RECIPE_PATH)/tests"
	@mkdir -p "$(RECIPE_PATH)/conversations"
	@echo "# $(RECIPE_TARGET)" > "$(RECIPE_PATH)/README.md"
	@echo "" >> "$(RECIPE_PATH)/README.md"
	@echo "Description of your recipe goes here." >> "$(RECIPE_PATH)/README.md"
	@echo "${GREEN}✓ Recipe structure created at $(RECIPE_PATH)${RESET}"
	@echo "Edit the files to implement your recipe."

# Rasa commands
.PHONY: check-recipe-context
check-recipe-context: ## Check if we're in a valid recipe context
	@if [ ! -f "domain.yml" ] || [ ! -f "data/flows.yml" ]; then \
	  echo "${RED}Error: Not in a recipe directory. Run from a recipe folder or specify RECIPE_TARGET${RESET}"; \
	  echo "Usage: cd recipes/level-1-basic/basic-tutorial && make train"; \
	  echo "   or: make train RECIPE_TARGET=basic-tutorial RECIPE_LEVEL=level-1-basic"; \
	  exit 1; \
	fi

.PHONY: check-license
check-license: ## Check for Rasa license
	@if [ -z "$$RASA_LICENSE" ]; then \
	  echo "${RED}Error: RASA_LICENSE environment variable not set${RESET}"; \
	  echo "Export your Rasa license: export RASA_LICENSE='your-license-key'"; \
	  exit 1; \
	fi
	@echo "${GREEN}✓ Rasa license found${RESET}"

.PHONY: train
train: check-license ## Train Rasa model in current recipe
	@if [ -f "domain.yml" ]; then \
	  echo "${BLUE}Training Rasa model in current directory...${RESET}"; \
	  $(PYTHON) -m rasa train; \
	else \
	  if [ -d "$(RECIPE_PATH)" ]; then \
	    echo "${BLUE}Training Rasa model in $(RECIPE_PATH)...${RESET}"; \
	    cd "$(RECIPE_PATH)" && $(PYTHON) -m rasa train; \
	  else \
	    echo "${RED}No recipe context found. Specify RECIPE_TARGET or run from recipe directory.${RESET}"; \
	    exit 1; \
	  fi; \
	fi
	@echo "${GREEN}✓ Model training completed${RESET}"

.PHONY: shell
shell: check-license ## Start Rasa shell
	@if [ -f "domain.yml" ]; then \
	  echo "${BLUE}Starting Rasa shell in current directory...${RESET}"; \
	  $(PYTHON) -m rasa shell; \
	else \
	  if [ -d "$(RECIPE_PATH)" ]; then \
	    echo "${BLUE}Starting Rasa shell in $(RECIPE_PATH)...${RESET}"; \
	    cd "$(RECIPE_PATH)" && $(PYTHON) -m rasa shell; \
	  else \
	    echo "${RED}No recipe context found. Specify RECIPE_TARGET or run from recipe directory.${RESET}"; \
	    exit 1; \
	  fi; \
	fi

.PHONY: inspect
inspect: check-license ## Start Rasa inspector
	@if [ -f "domain.yml" ]; then \
	  echo "${BLUE}Starting Rasa inspector in current directory...${RESET}"; \
	  $(PYTHON) -m rasa inspect; \
	else \
	  if [ -d "$(RECIPE_PATH)" ]; then \
	    echo "${BLUE}Starting Rasa inspector in $(RECIPE_PATH)...${RESET}"; \
	    cd "$(RECIPE_PATH)" && $(PYTHON) -m rasa inspect; \
	  else \
	    echo "${RED}No recipe context found. Specify RECIPE_TARGET or run from recipe directory.${RESET}"; \
	    exit 1; \
	  fi; \
	fi

.PHONY: run
run: check-license ## Start Rasa server
	@if [ -f "domain.yml" ]; then \
	  echo "${BLUE}Starting Rasa server in current directory...${RESET}"; \
	  $(PYTHON) -m rasa run --enable-api --cors "*"; \
	else \
	  if [ -d "$(RECIPE_PATH)" ]; then \
	    echo "${BLUE}Starting Rasa server in $(RECIPE_PATH)...${RESET}"; \
	    cd "$(RECIPE_PATH)" && $(PYTHON) -m rasa run --enable-api --cors "*"; \
	  else \
	    echo "${RED}No recipe context found. Specify RECIPE_TARGET or run from recipe directory.${RESET}"; \
	    exit 1; \
	  fi; \
	fi

.PHONY: run-actions
run-actions: ## Start action server
	@if [ -f "actions/actions.py" ]; then \
	  echo "${BLUE}Starting action server in current directory...${RESET}"; \
	  $(PYTHON) -m rasa run actions; \
	else \
	  if [ -d "$(RECIPE_PATH)" ] && [ -f "$(RECIPE_PATH)/actions/actions.py" ]; then \
	    echo "${BLUE}Starting action server in $(RECIPE_PATH)...${RESET}"; \
	    cd "$(RECIPE_PATH)" && $(PYTHON) -m rasa run actions; \
	  else \
	    echo "${RED}No actions.py found. Check recipe context.${RESET}"; \
	    exit 1; \
	  fi; \
	fi

.PHONY: test-e2e
test-e2e: check-license ## Run end-to-end tests
	@if [ -f "tests/e2e_test_cases.yml" ]; then \
		echo "${BLUE}Running E2E tests in current directory...${RESET}"; \
		if [ ! -d "models" ] || [ -z "$$(ls -A models 2>/dev/null)" ]; then \
			echo "${YELLOW}No trained model found. Training model first...${RESET}"; \
			$(PYTHON) -m rasa train; \
		fi; \
		echo "${BLUE}Starting action server in background...${RESET}"; \
		$(PYTHON) -m rasa run actions > /dev/null 2>&1 & \
		ACTION_PID=$$!; \
		echo "Action server PID: $$ACTION_PID"; \
		sleep 5; \
		echo "${BLUE}Running E2E tests...${RESET}"; \
		$(PYTHON) -m rasa test e2e tests/e2e_test_cases.yml; \
		TEST_EXIT=$$?; \
		echo "${BLUE}Stopping action server (PID: $$ACTION_PID)...${RESET}"; \
		kill $$ACTION_PID 2>/dev/null || true; \
		if [ $$TEST_EXIT -eq 0 ]; then \
			echo "${GREEN}✓ E2E tests completed${RESET}"; \
		else \
			echo "${RED}✗ E2E tests failed${RESET}"; \
			exit $$TEST_EXIT; \
		fi; \
	else \
		if [ -d "$(RECIPE_PATH)" ] && [ -f "$(RECIPE_PATH)/tests/e2e_test_cases.yml" ]; then \
			echo "${BLUE}Running E2E tests in $(RECIPE_PATH)...${RESET}"; \
			cd "$(RECIPE_PATH)"; \
			if [ ! -d "models" ] || [ -z "$$(ls -A models 2>/dev/null)" ]; then \
				echo "${YELLOW}No trained model found. Training model first...${RESET}"; \
				$(PYTHON) -m rasa train; \
			fi; \
			echo "${BLUE}Starting action server in background...${RESET}"; \
			$(PYTHON) -m rasa run actions > /dev/null 2>&1 & \
			ACTION_PID=$$!; \
			echo "Action server PID: $$ACTION_PID"; \
			sleep 5; \
			echo "${BLUE}Running E2E tests...${RESET}"; \
			$(PYTHON) -m rasa test e2e tests/e2e_test_cases.yml; \
			TEST_EXIT=$$?; \
			echo "${BLUE}Stopping action server (PID: $$ACTION_PID)...${RESET}"; \
			kill $$ACTION_PID 2>/dev/null || true; \
			if [ $$TEST_EXIT -eq 0 ]; then \
				echo "${GREEN}✓ E2E tests completed${RESET}"; \
			else \
				echo "${RED}✗ E2E tests failed${RESET}"; \
				exit $$TEST_EXIT; \
			fi; \
		else \
			echo "${RED}No E2E test file found. Check recipe context.${RESET}"; \
			exit 1; \
		fi; \
	fi

.PHONY: test-recipe
test-recipe: check-license ## Test specific recipe
	@if [ ! -d "$(RECIPE_PATH)" ]; then \
		echo "${RED}Recipe '$(RECIPE_TARGET)' not found${RESET}"; \
		exit 1; \
	fi
	@echo "${BLUE}Testing recipe: $(RECIPE_TARGET)${RESET}"
	@cd "$(RECIPE_PATH)"; \
	if [ -f "tests/e2e_test_cases.yml" ]; then \
		echo "Checking for trained model..."; \
		if [ ! -d "models" ] || [ -z "$$(ls -A models 2>/dev/null)" ]; then \
			echo "${YELLOW}No trained model found. Training model first...${RESET}"; \
			$(PYTHON) -m rasa train; \
		fi; \
		echo "${BLUE}Starting action server in background...${RESET}"; \
		$(PYTHON) -m rasa run actions > /dev/null 2>&1 & \
		ACTION_PID=$$!; \
		echo "Action server PID: $$ACTION_PID"; \
		sleep 5; \
		echo "Running E2E tests..."; \
		$(PYTHON) -m rasa test e2e tests/e2e_test_cases.yml; \
		TEST_EXIT=$$?; \
		echo "${BLUE}Stopping action server (PID: $$ACTION_PID)...${RESET}"; \
		kill $$ACTION_PID 2>/dev/null || true; \
		if [ $$TEST_EXIT -eq 0 ]; then \
			echo "${GREEN}✓ Tests passed for $(RECIPE_TARGET)${RESET}"; \
		else \
			echo "${RED}✗ Tests failed for $(RECIPE_TARGET)${RESET}"; \
			exit $$TEST_EXIT; \
		fi; \
	else \
		echo "${YELLOW}No E2E tests found for this recipe${RESET}"; \
	fi

.PHONY: test-all-recipes
test-all-recipes: check-license ## Test all recipes with E2E tests
	@echo "${BLUE}Testing all recipes...${RESET}"
	@error_count=0; \
	success_count=0; \
	for level in $(RECIPE_LEVELS); do \
		if [ -d "recipes/$$level" ]; then \
			for recipe in recipes/$$level/*/; do \
				if [ -d "$$recipe" ] && [ -f "$$recipe/tests/e2e_test_cases.yml" ]; then \
					recipe_name=$$(basename "$$recipe"); \
					echo ""; \
					echo "${YELLOW}Testing $$level/$$recipe_name...${RESET}"; \
					if RECIPE_TARGET=$$recipe_name RECIPE_LEVEL=$$level $(MAKE) test-recipe; then \
						echo "${GREEN}✓ $$level/$$recipe_name passed${RESET}"; \
						success_count=$$((success_count + 1)); \
					else \
						echo "${RED}✗ $$level/$$recipe_name failed${RESET}"; \
						error_count=$$((error_count + 1)); \
					fi; \
				fi; \
			done; \
		fi; \
	done; \
	echo ""; \
	echo "${BLUE}Test Summary:${RESET}"; \
	echo "  ${GREEN}Passed: $$success_count${RESET}"; \
	echo "  ${RED}Failed: $$error_count${RESET}"; \
	if [ $$error_count -eq 0 ]; then \
		echo "${GREEN}✓ All recipe tests passed${RESET}"; \
	else \
		echo "${RED}✗ $$error_count recipe(s) failed tests${RESET}"; \
		exit 1; \
	fi

# Development commands
.PHONY: format
format: ## Format all code with Ruff and Black
	@echo "${BLUE}Formatting code...${RESET}"
	$(PYTHON) -m ruff check --fix recipes/
	$(PYTHON) -m ruff format recipes/
	$(PYTHON) -m black recipes/
	$(PYTHON) -m isort recipes/
	@echo "${GREEN}✓ Code formatting completed${RESET}"

.PHONY: lint
lint: ## Run linters
	@echo "${BLUE}Running linters...${RESET}"
	$(PYTHON) -m ruff check recipes/
	$(PYTHON) -m ruff format --check recipes/
	$(PYTHON) -m black --check recipes/
	$(PYTHON) -m mypy recipes/ --ignore-missing-imports
	@echo "${GREEN}✓ Linting completed${RESET}"

.PHONY: test
test: ## Run all tests
	@echo "${BLUE}Running tests...${RESET}"
	$(PYTHON) -m pytest recipes/ $(PYTEST_ARGS) \
	  --cov=recipes \
	  --cov-report=term-missing \
	  --cov-fail-under=$(COVERAGE_THRESHOLD)
	@echo "${GREEN}✓ All tests completed${RESET}"

.PHONY: test-fast
test-fast: ## Run fast tests only
	@echo "${BLUE}Running fast tests...${RESET}"
	$(PYTHON) -m pytest recipes/ $(PYTEST_ARGS) -m "not slow and not integration"
	@echo "${GREEN}✓ Fast tests completed${RESET}"

.PHONY: test-integration
test-integration: ## Run integration tests
	@echo "${BLUE}Running integration tests...${RESET}"
	$(PYTHON) -m pytest recipes/ $(PYTEST_ARGS) -m "integration"
	@echo "${GREEN}✓ Integration tests completed${RESET}"

# Utility commands
.PHONY: clean
clean: ## Clean build artifacts and cache
	@echo "${BLUE}Cleaning build artifacts and cache...${RESET}"
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/
	rm -rf $(VENV_NAME) .mypy_cache .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	# Clean recipe-specific artifacts
	find recipes/ -type d -name "models" -exec rm -rf {} +
	find recipes/ -type d -name "logs" -exec rm -rf {} +
	find recipes/ -type f -name "*.tar.gz" -delete
	@echo "${GREEN}✓ Cleaned all build artifacts and cache${RESET}"

.PHONY: clean-models
clean-models: ## Clean trained models from all recipes
	@echo "${BLUE}Cleaning trained models...${RESET}"
	find recipes/ -type d -name "models" -exec rm -rf {} +
	@echo "${GREEN}✓ All trained models cleaned${RESET}"

.PHONY: update
update: ## Update all dependencies
	@echo "${BLUE}Updating dependencies...${RESET}"
	$(UV) pip install --upgrade rasa-pro rasa-sdk pytest pytest-cov pytest-asyncio ruff mypy isort black pre-commit \
		--python $(REPO_ROOT)/$(VENV_NAME)/bin/python
	@echo "${GREEN}✓ Dependencies updated${RESET}"

.PHONY: docs
docs: ## Generate documentation
	@echo "${BLUE}Generating documentation...${RESET}"
	@if [ -f "scripts/generate-docs.py" ]; then \
	  $(PYTHON) scripts/generate-docs.py; \
	  echo "${GREEN}✓ Documentation generated${RESET}"; \
	else \
	  echo "${YELLOW}Documentation generator not found${RESET}"; \
	fi

.PHONY: validate-all
validate-all: ## Validate all recipes
	@echo "${BLUE}Validating all recipes...${RESET}"
	@error_count=0; \
	for level in $(RECIPE_LEVELS); do \
	  if [ -d "recipes/$$level" ]; then \
	    for recipe in recipes/$$level/*/; do \
	      if [ -d "$$recipe" ]; then \
	        recipe_name=$$(basename "$$recipe"); \
	        echo "Validating $$level/$$recipe_name..."; \
	        if ! RECIPE_TARGET=$$recipe_name RECIPE_LEVEL=$$level make validate-recipe >/dev/null 2>&1; then \
	          echo "${RED}✗ $$level/$$recipe_name failed validation${RESET}"; \
	          error_count=$$((error_count + 1)); \
	        else \
	          echo "${GREEN}✓ $$level/$$recipe_name${RESET}"; \
	        fi; \
	      fi; \
	    done; \
	  fi; \
	done; \
	if [ $$error_count -eq 0 ]; then \
	  echo "${GREEN}✓ All recipes validated successfully${RESET}"; \
	else \
	  echo "${RED}✗ $$error_count recipes failed validation${RESET}"; \
	  exit 1; \
	fi

.PHONY: pre-commit
pre-commit: format lint test validate-all ## Run all checks before committing
	@echo "${GREEN}✓ All pre-commit checks passed${RESET}"

.PHONY: structure
structure: ## Show project structure
	@echo "${YELLOW}Rasa CALM Cookbook Structure:${RESET}"
	@echo "${BLUE}"
	@if command -v tree > /dev/null; then \
		tree -a -I '.git|.venv|__pycache__|*.pyc|*.pyo|*.pyd|.pytest_cache|.ruff_cache|.coverage|htmlcov|models|logs|*.tar.gz' -L 3; \
	else \
		find . -not -path '*/\.*' -not -path '*.pyc' -not -path '*/__pycache__/*' \
			-not -path './.venv/*' -not -path './build/*' -not -path './dist/*' \
			-not -path './models/*' -not -path './logs/*' -not -path '*.tar.gz' \
			| head -50 | sort | \
			sed -e "s/[^-][^\/]*\// │   /g" -e "s/├── /├── /" -e "s/└── /└── /"; \
	fi
	@echo "${RESET}"

# Quick start commands
.PHONY: quick-start
quick-start: ## Quick start with basic tutorial
	@echo "${BLUE}Quick start with basic tutorial...${RESET}"
	@if [ ! -d ".venv" ]; then \
	  make setup; \
	fi
	@make recipe RECIPE_TARGET=basic-tutorial RECIPE_LEVEL=level-1-basic
	@echo ""
	@echo "${GREEN}✓ Quick start completed!${RESET}"
	@echo "${YELLOW}Next steps:${RESET}"
	@echo "  1. ${GREEN}cd recipes/level-1-basic/basic-tutorial${RESET}"
	@echo "  2. Set your environment variables (RASA_LICENSE, OPENAI_API_KEY)"
	@echo "  3. ${GREEN}make train${RESET}"
	@echo "  4. ${GREEN}make inspect${RESET}"

# Environment setup utilities
.PHONY: setup-env-all
setup-env-all: ## Create .env files for all recipes
	@echo "${BLUE}Setting up environment files for all recipes...${RESET}"
	@if [ ! -f ".env" ]; then \
		echo "Creating root .env file..."; \
		cp .env.example .env; \
	fi
	@for level in $(RECIPE_LEVELS); do \
		if [ -d "recipes/$$level" ]; then \
			for recipe in recipes/$$level/*/; do \
				if [ -d "$$recipe" ] && [ -f "$$recipe/.env.example" ]; then \
					recipe_name=$$(basename "$$recipe"); \
					if [ ! -f "$$recipe/.env" ]; then \
						echo "Creating .env for $$level/$$recipe_name..."; \
						cp "$$recipe/.env.example" "$$recipe/.env"; \
					fi; \
				fi; \
			done; \
		fi; \
	done
	@echo "${GREEN}✓ Environment files created${RESET}"
	@echo "${YELLOW}Please edit .env files with your actual credentials${RESET}"

.PHONY: check-env-all
check-env-all: ## Check environment setup for all recipes
	@echo "${BLUE}Checking environment for all recipes...${RESET}"
	@error_count=0; \
	for level in $(RECIPE_LEVELS); do \
		if [ -d "recipes/$$level" ]; then \
			for recipe in recipes/$$level/*/; do \
				if [ -d "$$recipe" ]; then \
					recipe_name=$$(basename "$$recipe"); \
					echo "Checking $$level/$$recipe_name..."; \
					if [ -f "$$recipe/.env" ]; then \
						echo "  ✓ .env exists"; \
					else \
						echo "  ✗ .env missing"; \
						error_count=$$((error_count + 1)); \
					fi; \
				fi; \
			done; \
		fi; \
	done; \
	if [ $$error_count -eq 0 ]; then \
		echo "${GREEN}✓ All recipes have environment files${RESET}"; \
	else \
		echo "${YELLOW}⚠ $$error_count recipes missing .env files${RESET}"; \
		echo "Run 'make setup-env-all' to create them"; \
	fi

.PHONY: add-paths
add-paths: ## Add file paths as first-line comments to all Python files
	@echo "${BLUE}Adding file paths as comments to Python files...${RESET}"
	@echo '#!/usr/bin/env python' > add_paths.py
	@echo '# add_paths.py' >> add_paths.py
	@echo '"""' >> add_paths.py
	@echo 'Script to add file paths as first-line comments to Python files.' >> add_paths.py
	@echo '"""' >> add_paths.py
	@echo 'import os' >> add_paths.py
	@echo 'import sys' >> add_paths.py
	@echo 'import traceback' >> add_paths.py
	@echo '' >> add_paths.py
	@echo 'EXTENSIONS = (".py", ".yaml", ".yml", ".toml", ".env", ".example")' >> add_paths.py
	@echo '' >> add_paths.py
	@echo 'def update_file(filepath):' >> add_paths.py
	@echo '    try:' >> add_paths.py
	@echo '        relpath = os.path.relpath(filepath)' >> add_paths.py
	@echo '        print(f"Processing {relpath}...")' >> add_paths.py
	@echo '' >> add_paths.py
	@echo '        with open(filepath, "r") as f:' >> add_paths.py
	@echo '            content = f.read()' >> add_paths.py
	@echo '' >> add_paths.py
	@echo '        lines = content.split("\\n")' >> add_paths.py
	@echo '        if not lines:' >> add_paths.py
	@echo '            print(f"  Skipping {relpath}: empty file")' >> add_paths.py
	@echo '            return' >> add_paths.py
	@echo '' >> add_paths.py
	@echo '        has_path_comment = False' >> add_paths.py
	@echo '        if lines[0].strip().startswith("#"):' >> add_paths.py
	@echo '            has_path_comment = True' >> add_paths.py
	@echo '            old_line = lines[0]' >> add_paths.py
	@echo '            lines[0] = f"# {relpath}"' >> add_paths.py
	@echo '            print(f"  Replacing comment: {old_line} -> # {relpath}")' >> add_paths.py
	@echo '        else:' >> add_paths.py
	@echo '            lines.insert(0, f"# {relpath}")' >> add_paths.py
	@echo '            print(f"  Adding new comment: # {relpath}")' >> add_paths.py
	@echo '' >> add_paths.py
	@echo '        with open(filepath, "w") as f:' >> add_paths.py
	@echo '            f.write("\\n".join(lines))' >> add_paths.py
	@echo '' >> add_paths.py
	@echo '        print(f"  Updated {relpath}")' >> add_paths.py
	@echo '    except Exception as e:' >> add_paths.py
	@echo '        print(f"  Error processing {filepath}: {str(e)}")' >> add_paths.py
	@echo '        traceback.print_exc()' >> add_paths.py
	@echo '' >> add_paths.py
	@echo 'def main():' >> add_paths.py
	@echo '    try:' >> add_paths.py
	@echo '        count = 0' >> add_paths.py
	@echo '        print("Starting file scan...")' >> add_paths.py
	@echo '        for root, dirs, files in os.walk("."):' >> add_paths.py
	@echo '            # Skip hidden and build directories' >> add_paths.py
	@echo '            if any(x in root for x in [".git", ".venv", "__pycache__", ".mypy_cache",' >> add_paths.py
	@echo '                                      ".pytest_cache", ".ruff_cache", "build", "dist", ".egg-info"]):' >> add_paths.py
	@echo '                continue' >> add_paths.py
	@echo '' >> add_paths.py
	@echo '            for file in files:' >> add_paths.py
	@echo '                if file.endswith(EXTENSIONS):' >> add_paths.py
	@echo '                    filepath = os.path.join(root, file)' >> add_paths.py
	@echo '                    update_file(filepath)' >> add_paths.py
	@echo '                    count += 1' >> add_paths.py
	@echo '' >> add_paths.py
	@echo '        print(f"Processed {count} files (extensions: {EXTENSIONS})")' >> add_paths.py
	@echo '    except Exception as e:' >> add_paths.py
	@echo '        print(f"Fatal error: {str(e)}")' >> add_paths.py
	@echo '        traceback.print_exc()' >> add_paths.py
	@echo '        sys.exit(1)' >> add_paths.py
	@echo '' >> add_paths.py
	@echo 'if __name__ == "__main__":' >> add_paths.py
	@echo '    main()' >> add_paths.py
	@chmod +x add_paths.py
	@$(PYTHON) add_paths.py
	@rm add_paths.py
	@echo "${GREEN}✓ File paths added to all files${RESET}"

.PHONY: flatten
flatten: ## Concatenate project files into flat.txt
	@echo "${BLUE}Flattening project files into flat.txt...${RESET}"
	@echo 'import os' > flatten_files.py
	@echo 'import sys' >> flatten_files.py
	@echo 'import traceback' >> flatten_files.py
	@echo '' >> flatten_files.py
	@echo 'EXTENSIONS = (".py", ".yaml", ".yml", ".toml", ".env", ".example")' >> flatten_files.py
	@echo 'SKIP_DIR_PARTS = (".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", "build", "dist", ".egg-info")' >> flatten_files.py
	@echo '' >> flatten_files.py
	@echo 'def iter_files(root_dir="."):' >> flatten_files.py
	@echo '    for root, dirs, files in os.walk(root_dir):' >> flatten_files.py
	@echo '        # Prune unwanted dirs in-place for efficiency' >> flatten_files.py
	@echo '        dirs[:] = [' >> flatten_files.py
	@echo '            d for d in dirs' >> flatten_files.py
	@echo '            if not any(skip in os.path.join(root, d) for skip in SKIP_DIR_PARTS)' >> flatten_files.py
	@echo '        ]' >> flatten_files.py
	@echo '' >> flatten_files.py
	@echo '        for file in files:' >> flatten_files.py
	@echo '            if not file.endswith(EXTENSIONS):' >> flatten_files.py
	@echo '                continue' >> flatten_files.py
	@echo '            filepath = os.path.join(root, file)' >> flatten_files.py
	@echo '            # Avoid including the output file itself or this script' >> flatten_files.py
	@echo '            if os.path.basename(filepath) in {"flat.txt", "flatten_files.py"}:' >> flatten_files.py
	@echo '                continue' >> flatten_files.py
	@echo '            yield filepath' >> flatten_files.py
	@echo '' >> flatten_files.py
	@echo 'def main():' >> flatten_files.py
	@echo '    out_path = os.path.join(os.path.dirname(__file__), "flat.txt")' >> flatten_files.py
	@echo '    print(f"Writing flattened output to {out_path!r}")' >> flatten_files.py
	@echo '    try:' >> flatten_files.py
	@echo '        files = sorted(iter_files("."))' >> flatten_files.py
	@echo '        if not files:' >> flatten_files.py
	@echo '            print("No matching files found. Nothing to do.")' >> flatten_files.py
	@echo '            return' >> flatten_files.py
	@echo '' >> flatten_files.py
	@echo '        with open(out_path, "w", encoding="utf-8") as out:' >> flatten_files.py
	@echo '            for idx, filepath in enumerate(files, start=1):' >> flatten_files.py
	@echo '                relpath = os.path.relpath(filepath)' >> flatten_files.py
	@echo '                print(f"[{idx}/{len(files)}] Adding {relpath}...")' >> flatten_files.py
	@echo '                out.write("=" * 80 + "\\n")' >> flatten_files.py
	@echo '                out.write(f"FILE: {relpath}\\n")' >> flatten_files.py
	@echo '                out.write("=" * 80 + "\\n\\n")' >> flatten_files.py
	@echo '                try:' >> flatten_files.py
	@echo '                    with open(filepath, "r", encoding="utf-8", errors="replace") as f:' >> flatten_files.py
	@echo '                        out.write(f.read())' >> flatten_files.py
	@echo '                except Exception as e:' >> flatten_files.py
	@echo '                    msg = f"[WARN] Could not read {relpath}: {e}"' >> flatten_files.py
	@echo '                    print(msg)' >> flatten_files.py
	@echo '                    out.write(f"\\n{msg}\\n")' >> flatten_files.py
	@echo '                out.write("\\n\\n")' >> flatten_files.py
	@echo '' >> flatten_files.py
	@echo '        print(f"Done. Flattened {len(files)} files into {out_path}")' >> flatten_files.py
	@echo '    except Exception as e:' >> flatten_files.py
	@echo '        print(f"Fatal error: {e}")' >> flatten_files.py
	@echo '        traceback.print_exc()' >> flatten_files.py
	@echo '        sys.exit(1)' >> flatten_files.py
	@echo '' >> flatten_files.py
	@echo 'if __name__ == "__main__":' >> flatten_files.py
	@echo '    main()' >> flatten_files.py
	@chmod +x flatten_files.py
	@$(PYTHON) flatten_files.py
	@rm flatten_files.py
	@echo "${GREEN}✓ Created flat.txt with concatenated project files${RESET}"


.DEFAULT_GOAL := help