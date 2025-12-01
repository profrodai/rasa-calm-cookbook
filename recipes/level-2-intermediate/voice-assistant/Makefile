# Terminal colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)
BLUE   := $(shell tput -Txterm setaf 4)
RED    := $(shell tput -Txterm setaf 1)

# Recipe settings
RECIPE_NAME := voice-assistant
REPO_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null || echo "../..")
VENV_NAME := .venv
PYTHON := $(REPO_ROOT)/$(VENV_NAME)/bin/python
RASA := $(PYTHON) -m rasa
UV := $(shell which uv)

# Config
CONFIG_FILE := config.yml
DEFAULT_CONFIG := config-openai.yml
ENV_FILE := .env
ENV_EXAMPLE := .env.example

# Include environment variables
ifneq (,$(wildcard $(ENV_FILE)))
    include $(ENV_FILE)
    export
endif

help: ## Show this help message
	@echo ''
	@echo '${YELLOW}$(RECIPE_NAME) - Voice Assistant Commands${RESET}'
	@echo ''
	@echo '${YELLOW}Quick Start:${RESET}'
	@echo '  1. ${GREEN}make setup-recipe${RESET}     - Install dependencies'
	@echo '  2. ${GREEN}make setup-env${RESET}        - Create .env file'
	@echo '  3. Edit .env with API keys (RASA_LICENSE, OPENAI_API_KEY, DEEPGRAM_API_KEY, RIME_API_KEY)'
	@echo '  4. ${GREEN}make train${RESET}            - Train model'
	@echo '  5. ${GREEN}make inspect-voice${RESET}    - Test with voice'
	@echo ''
	@echo '${YELLOW}Voice Testing:${RESET}'
	@echo '  Voice Test:   ${GREEN}make inspect-voice${RESET}   - Test with voice in browser'
	@echo '  Text Test:    ${GREEN}make inspect${RESET}         - Test with text'
	@echo '  Shell:        ${GREEN}make shell${RESET}           - Command-line testing'
	@echo ''
	@echo '${YELLOW}Development:${RESET}'
	@echo '  Train:        ${GREEN}make train${RESET}           - Train the model'
	@echo '  Run:          ${GREEN}make run${RESET}             - Start server'
	@echo '  Actions:      ${GREEN}make run-actions${RESET}     - Start action server'
	@echo ''
	# Add to help section (around line 50-55):
	@echo '${YELLOW}Testing:${RESET}'
	@echo '  Test E2E:     ${GREEN}make test-e2e${RESET}            - Run end-to-end tests'
	@echo '  Test Voice:   ${GREEN}make test-voice${RESET}          - Run voice-specific tests'
	@echo '  Voice Auto:   ${GREEN}make test-voice-automated${RESET} - Automated voice tests'
	@echo '  Audio Gen:    ${GREEN}make generate-test-audio${RESET} - Generate test audio files'
	@echo '  Validate:     ${GREEN}make validate${RESET}            - Validate configuration'
	@echo ''
	@echo '${YELLOW}Configuration:${RESET}'
	@echo '  Check:        ${GREEN}make status${RESET}          - Show environment status'
	@echo '  Clean:        ${GREEN}make clean${RESET}           - Clean generated files'
	@echo ''

.PHONY: inspect-voice
inspect-voice: check-env ## Start Rasa inspector with voice enabled
	@echo "${BLUE}Starting Rasa inspector with voice enabled...${RESET}"
	@echo "${YELLOW}Instructions:${RESET}"
	@echo "  1. Inspector will open in your browser"
	@echo "  2. Click the microphone icon to enable voice"
	@echo "  3. Grant microphone permissions when prompted"
	@echo "  4. Speak naturally - the assistant will respond with voice"
	@echo ""
	$(RASA) inspect --voice

.PHONY: test-voice
test-voice: check-env ## Run voice-specific tests
	@echo "${BLUE}Running voice-specific tests...${RESET}"
	@if [ -f "tests/e2e_test_cases.yml" ]; then \
	  $(PYTHON) -m pytest tests/ -v -m voice; \
	else \
	  echo "${YELLOW}No voice tests found${RESET}"; \
	fi

.PHONY: check-speech-keys
check-speech-keys: ## Check if speech API keys are configured
	@echo "${BLUE}Checking speech service configuration...${RESET}"
	@if [ -z "$(DEEPGRAM_API_KEY)" ]; then \
	  echo "${RED}✗ DEEPGRAM_API_KEY not set${RESET}"; \
	else \
	  echo "${GREEN}✓ DEEPGRAM_API_KEY is set${RESET}"; \
	fi
	@if [ -z "$(RIME_API_KEY)" ]; then \
	  echo "${RED}✗ RIME_API_KEY not set${RESET}"; \
	else \
	  echo "${GREEN}✓ RIME_API_KEY is set${RESET}"; \
	fi

PHONY: setup-env
setup-env: ## Create .env file from template
	@if [ ! -f "$(ENV_FILE)" ]; then \
	  if [ -f "$(ENV_EXAMPLE)" ]; then \
	    echo "${BLUE}Creating $(ENV_FILE) from $(ENV_EXAMPLE)...${RESET}"; \
	    cp $(ENV_EXAMPLE) $(ENV_FILE); \
	    echo "${YELLOW}Please edit $(ENV_FILE) with your actual API keys and credentials${RESET}"; \
	    echo "${YELLOW}Required variables:${RESET}"; \
	    grep -E "^[A-Z_]+=.*-here" $(ENV_FILE) | cut -d'=' -f1 | sed 's/^/  - /' || true; \
	  else \
	    echo "${BLUE}Creating basic $(ENV_FILE)...${RESET}"; \
	    echo "# Environment Variables for $(RECIPE_NAME)" > $(ENV_FILE); \
	    echo "RASA_LICENSE=your-rasa-pro-license-key-here" >> $(ENV_FILE); \
	    echo "OPENAI_API_KEY=your-openai-api-key-here" >> $(ENV_FILE); \
	    echo "LOG_LEVEL=INFO" >> $(ENV_FILE); \
	    echo "DEBUG=false" >> $(ENV_FILE); \
	    echo "${YELLOW}Please edit $(ENV_FILE) with your actual credentials${RESET}"; \
	  fi; \
	  echo "${YELLOW}After editing, reload with: source $(ENV_FILE) or restart make${RESET}"; \
	else \
	  echo "${GREEN}$(ENV_FILE) already exists${RESET}"; \
	fi

.PHONY: check-venv
check-venv: ## Check if virtual environment is properly set up
	@echo "${BLUE}Checking virtual environment setup...${RESET}"
	@if [ ! -f "$(PYTHON)" ]; then \
	  echo "${RED}✗ Virtual environment not found at $(PYTHON)${RESET}"; \
	  echo "${YELLOW}Please run the following from repository root:${RESET}"; \
	  echo "  1. ${GREEN}cd $(REPO_ROOT)${RESET}"; \
	  echo "  2. ${GREEN}make setup${RESET}"; \
	  echo "  3. ${GREEN}source .venv/bin/activate${RESET}"; \
	  exit 1; \
	fi
	@echo "${GREEN}✓ Virtual environment found at $(PYTHON)${RESET}"
	@$(PYTHON) --version
	@echo "Virtual environment path: $(PYTHON)"

.PHONY: check-env
check-env: check-venv ## Check environment and prerequisites
	@echo "${BLUE}Checking environment...${RESET}"
	@# Check for required environment variables
	@if [ -z "$(RASA_LICENSE)" ]; then \
	  echo "${RED}Error: RASA_LICENSE environment variable not set${RESET}"; \
	  echo "Options:"; \
	  echo "  1. Edit $(ENV_FILE) file and restart make"; \
	  echo "  2. Export directly: ${GREEN}export RASA_LICENSE='your-license-key'${RESET}"; \
	  echo "  3. Run with env: ${GREEN}RASA_LICENSE='key' make train${RESET}"; \
	  exit 1; \
	fi
	@echo "${GREEN}✓ RASA_LICENSE is set${RESET}"
	@# Check for LLM provider credentials
	@provider_found=false; \
	if [ -n "$(OPENAI_API_KEY)" ]; then \
	  echo "${GREEN}✓ OpenAI API key found${RESET}"; \
	  provider_found=true; \
	fi; \
	if [ -n "$(AZURE_OPENAI_ENDPOINT)" ] && [ -n "$(AZURE_OPENAI_API_KEY)" ]; then \
	  echo "${GREEN}✓ Azure OpenAI credentials found${RESET}"; \
	  provider_found=true; \
	fi; \
	if [ -n "$(LOCAL_LLM_ENDPOINT)" ]; then \
	  echo "${GREEN}✓ Local LLM endpoint configured${RESET}"; \
	  provider_found=true; \
	fi; \
	if [ "$$provider_found" = "false" ]; then \
	  echo "${YELLOW}⚠ No LLM provider credentials found${RESET}"; \
	  echo "Set one of: OPENAI_API_KEY, AZURE_OPENAI_*, or LOCAL_LLM_ENDPOINT"; \
	fi
	@# Check config file
	@if [ ! -f "$(CONFIG_FILE)" ]; then \
	  echo "${YELLOW}No config.yml found. Using default: $(DEFAULT_CONFIG)${RESET}"; \
	  cp $(DEFAULT_CONFIG) $(CONFIG_FILE); \
	fi
	@echo "${GREEN}✓ Environment check completed${RESET}"

.PHONY: status
status: ## Show environment status
	@echo "${BLUE}Environment Status:${RESET}"
	@echo ""
	@echo "${YELLOW}Files:${RESET}"
	@if [ -f "$(ENV_FILE)" ]; then \
	  echo "  ✓ .env file exists"; \
	else \
	  echo "  ✗ .env file missing (run 'make setup-env')"; \
	fi
	@if [ -f "$(CONFIG_FILE)" ]; then \
	  echo "  ✓ config.yml exists"; \
	else \
	  echo "  ✗ config.yml missing"; \
	fi
	@echo ""
	@echo "${YELLOW}Environment Variables:${RESET}"
	@if [ -n "$(RASA_LICENSE)" ]; then \
	  echo "  ✓ RASA_LICENSE is set"; \
	else \
	  echo "  ✗ RASA_LICENSE not set"; \
	fi
	@if [ -n "$(OPENAI_API_KEY)" ]; then \
	  echo "  ✓ OPENAI_API_KEY is set"; \
	else \
	  echo "  ✗ OPENAI_API_KEY not set"; \
	fi
	@if [ -n "$(AZURE_OPENAI_ENDPOINT)" ]; then \
	  echo "  ✓ AZURE_OPENAI_ENDPOINT is set"; \
	else \
	  echo "  - AZURE_OPENAI_ENDPOINT not set"; \
	fi
	@if [ -n "$(LOCAL_LLM_ENDPOINT)" ]; then \
	  echo "  ✓ LOCAL_LLM_ENDPOINT is set"; \
	else \
	  echo "  - LOCAL_LLM_ENDPOINT not set"; \
	fi
	@echo ""
	@echo "${YELLOW}Dependencies:${RESET}"
	@if command -v uv >/dev/null 2>&1; then \
	  echo "  ✓ uv is installed"; \
	else \
	  echo "  ✗ uv not found"; \
	fi
	@if [ -f "$(PYTHON)" ]; then \
	  echo "  ✓ Python virtual environment found: $(PYTHON)"; \
	  if $(PYTHON) -c "import rasa" 2>/dev/null; then \
	    echo "  ✓ Rasa is installed in venv"; \
	  else \
	    echo "  ✗ Rasa not installed in venv"; \
	  fi; \
	else \
	  echo "  ✗ Virtual environment not found at $(PYTHON)"; \
	  echo "    Run 'make setup' from repository root first"; \
	fi
	@echo ""
	@echo "${YELLOW}Trained Models:${RESET}"
	@if [ ! -d "models" ]; then \
	  echo "  ✗ No models directory"; \
	elif [ -z "$(ls -A models 2>/dev/null)" ]; then \
	  echo "  ✗ Models directory is empty"; \
	else \
	  latest_model=$(ls -t models/*.tar.gz 2>/dev/null | head -1); \
	  if [ -n "$latest_model" ]; then \
	    echo "  ✓ Latest model: $(basename $latest_model)"; \
	    echo "    Size: $(ls -lh "$latest_model" | awk '{print $5}')"; \
	    echo "    Modified: $(ls -lh "$latest_model" | awk '{print $6, $7, $8}')"; \
	  else \
	    echo "  ✗ No .tar.gz model files found"; \
	  fi; \
	fi

.PHONY: setup-recipe
setup-recipe: check-venv setup-env ## Verify recipe dependencies are installed
	@echo "${BLUE}Checking recipe dependencies...${RESET}"
	@echo "${YELLOW}Note: This recipe requires voice dependencies${RESET}"
	@echo "${YELLOW}If not already installed, run from root:${RESET}"
	@echo "  ${GREEN}cd $(REPO_ROOT)${RESET}"
	@echo "  ${GREEN}make install-intermediate${RESET}  # Base voice dependencies"
	@echo "  ${GREEN}make install-system-deps${RESET}   # PortAudio (if needed)"
	@echo "  ${GREEN}make install-voice-full${RESET}    # PyAudio (optional)"
	@echo ""
	@echo "${BLUE}Verifying required dependencies...${RESET}"
	@missing_deps=false; \
	for pkg in openai websockets aiohttp; do \
		if ! $(PYTHON) -c "import $$pkg" 2>/dev/null; then \
			echo "${RED}✗ $$pkg not installed${RESET}"; \
			missing_deps=true; \
		else \
			echo "${GREEN}✓ $$pkg is installed${RESET}"; \
		fi; \
	done; \
	if [ "$$missing_deps" = "true" ]; then \
		echo ""; \
		echo "${YELLOW}Installing missing dependencies...${RESET}"; \
		$(UV) pip install openai websockets aiohttp --python $(PYTHON); \
		echo "${GREEN}✓ Missing dependencies installed${RESET}"; \
	else \
		echo "${GREEN}✓ All required dependencies are installed${RESET}"; \
	fi

.PHONY: config-openai
config-openai: ## Use OpenAI configuration
	@echo "${BLUE}Setting up OpenAI configuration...${RESET}"
	@cp config-openai.yml config.yml
	@echo "${GREEN}✓ OpenAI configuration active${RESET}"
	@if [ -z "$(OPENAI_API_KEY)" ]; then \
	  echo "${YELLOW}⚠ Remember to set OPENAI_API_KEY environment variable${RESET}"; \
	  echo "Add it to your .env file or export it directly"; \
	fi

.PHONY: config-azure
config-azure: ## Use Azure OpenAI configuration
	@echo "${BLUE}Setting up Azure OpenAI configuration...${RESET}"
	@cp config-azure.yml config.yml
	@echo "${GREEN}✓ Azure OpenAI configuration active${RESET}"
	@if [ -z "$(AZURE_OPENAI_ENDPOINT)" ] || [ -z "$(AZURE_OPENAI_API_KEY)" ]; then \
	  echo "${YELLOW}⚠ Remember to set Azure OpenAI environment variables:${RESET}"; \
	  echo "  AZURE_OPENAI_ENDPOINT"; \
	  echo "  AZURE_OPENAI_API_KEY"; \
	fi

.PHONY: config-local
config-local: ## Use local LLM configuration
	@echo "${BLUE}Setting up local LLM configuration...${RESET}"
	@cp config-local.yml config.yml
	@echo "${GREEN}✓ Local LLM configuration active${RESET}"
	@echo "${YELLOW}Make sure your local LLM server is running${RESET}"
	@if [ -n "$(LOCAL_LLM_ENDPOINT)" ]; then \
	  echo "Configured endpoint: $(LOCAL_LLM_ENDPOINT)"; \
	else \
	  echo "Default endpoint: http://localhost:8000/v1"; \
	fi

.PHONY: train
train: check-env ## Train the Rasa model
	@echo "${BLUE}Training Rasa model...${RESET}"
	$(RASA) train
	@echo "${GREEN}✓ Model training completed${RESET}"

.PHONY: shell
shell: check-env ## Start Rasa shell
	@echo "${BLUE}Starting Rasa shell...${RESET}"
	$(RASA) shell

.PHONY: inspect
inspect: check-env ## Start Rasa inspector (recommended for testing)
	@echo "${BLUE}Starting Rasa inspector...${RESET}"
	@echo "${YELLOW}Inspector will open in your browser${RESET}"
	$(RASA) inspect

.PHONY: run
run: check-env ## Start Rasa server
	@echo "${BLUE}Starting Rasa server...${RESET}"
	$(RASA) run --enable-api --cors "*"

.PHONY: run-actions
run-actions: ## Start action server
	@echo "${BLUE}Starting action server...${RESET}"
	$(RASA) run actions

.PHONY: test-e2e-manual
test-e2e-manual: check-env ## Run end-to-end tests (requires running action server)
	@echo "${BLUE}Running end-to-end tests...${RESET}"
	@if [ ! -f "tests/e2e_test_cases.yml" ]; then \
	  echo "${YELLOW}No E2E tests found${RESET}"; \
	  exit 0; \
	fi
	@if [ ! -d "models" ] || [ -z "$(ls -A models 2>/dev/null)" ]; then \
	  echo "${YELLOW}No trained model found. Training model first...${RESET}"; \
	  $(RASA) train; \
	fi
	@echo "${BLUE}Checking if action server is running...${RESET}"
	@if ! curl -s http://localhost:5055/health > /dev/null 2>&1; then \
	  echo "${RED}Action server is not running${RESET}"; \
	  echo "Please start it in another terminal with: ${GREEN}make run-actions${RESET}"; \
	  echo "Or use: ${GREEN}make test-e2e${RESET} to auto-start action server"; \
	  exit 1; \
	fi
	@echo "${GREEN}✓ Action server is running${RESET}"
	$(RASA) test e2e tests/e2e_test_cases.yml
	@echo "${GREEN}✓ E2E tests completed${RESET}"

.PHONY: test-e2e
test-e2e: check-env ## Run end-to-end tests (auto-starts action server)
	@echo "${BLUE}Running end-to-end tests...${RESET}"
	@if [ ! -f "tests/e2e_test_cases.yml" ]; then \
	  echo "${YELLOW}No E2E tests found${RESET}"; \
	  exit 0; \
	fi
	@if [ ! -d "models" ] || [ -z "$$(ls -A models 2>/dev/null)" ]; then \
	  echo "${YELLOW}No trained model found. Training model first...${RESET}"; \
	  $(RASA) train; \
	fi
	@echo "${BLUE}Starting action server in background...${RESET}"
	@$(RASA) run actions > /dev/null 2>&1 & \
	ACTION_PID=$$!; \
	echo "Action server PID: $$ACTION_PID"; \
	sleep 5; \
	echo "${BLUE}Running E2E tests...${RESET}"; \
	$(RASA) test e2e tests/e2e_test_cases.yml; \
	TEST_EXIT=$$?; \
	echo "${BLUE}Stopping action server (PID: $$ACTION_PID)...${RESET}"; \
	kill $$ACTION_PID 2>/dev/null || true; \
	if [ $$TEST_EXIT -eq 0 ]; then \
	  echo "${GREEN}✓ E2E tests completed${RESET}"; \
	else \
	  echo "${RED}✗ E2E tests failed${RESET}"; \
	  exit $$TEST_EXIT; \
	fi

.PHONY: validate
validate: check-env ## Validate configuration files
	@echo "${BLUE}Validating configuration...${RESET}"
	@if [ -f "config.yml" ]; then \
	  $(RASA) data validate; \
	  echo "${GREEN}✓ Configuration is valid${RESET}"; \
	else \
	  echo "${RED}No config.yml found${RESET}"; \
	  exit 1; \
	fi

.PHONY: clean
clean: ## Clean generated files
	@echo "${BLUE}Cleaning generated files...${RESET}"
	rm -rf models/ logs/ .rasa/
	find . -name "*.tar.gz" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	@echo "${GREEN}✓ Cleanup completed${RESET}"

.PHONY: reset
reset: clean ## Reset to fresh state
	@echo "${BLUE}Resetting recipe to fresh state...${RESET}"
	@if [ -f "config.yml" ] && [ -f "$(DEFAULT_CONFIG)" ]; then \
	  rm config.yml; \
	  echo "Removed config.yml (will use default on next run)"; \
	fi
	@echo "${YELLOW}Note: .env file preserved. Remove manually if needed.${RESET}"
	@echo "${GREEN}✓ Recipe reset completed${RESET}"

.PHONY: quick-start
quick-start: ## Quick start: setup, config, and train
	@echo "${BLUE}Quick start for $(RECIPE_NAME)...${RESET}"
	@make setup-recipe
	@make config-openai
	@if [ -f "$(ENV_FILE)" ] && [ -n "$(RASA_LICENSE)" ]; then \
	  echo "${BLUE}Environment configured, proceeding with training...${RESET}"; \
	  make train; \
	else \
	  echo "${YELLOW}Environment not properly configured. Please:${RESET}"; \
	  echo "  1. Edit $(ENV_FILE) with your credentials"; \
	  echo "  2. Run: ${GREEN}make train${RESET}"; \
	  echo "  3. Or use: ${GREEN}RASA_LICENSE='key' OPENAI_API_KEY='key' make train${RESET}"; \
	  exit 1; \
	fi
	@echo ""
	@echo "${GREEN}✓ Quick start completed!${RESET}"
	@echo "${YELLOW}Next steps:${RESET}"
	@echo "  1. ${GREEN}make inspect${RESET} - Test your assistant"
	@echo "  2. ${GREEN}make test-e2e${RESET} - Run tests"

.PHONY: generate-test-audio
generate-test-audio: ## Generate test audio files for automated testing
	@echo "${BLUE}Generating test audio files...${RESET}"
	@if [ ! -f "tests/generate_test_audio.py" ]; then \
	  echo "${RED}Error: tests/generate_test_audio.py not found${RESET}"; \
	  echo "Please copy the script to tests/ directory"; \
	  exit 1; \
	fi
	@# Check dependencies
	@if ! $(PYTHON) -c "import gtts, pydub" 2>/dev/null; then \
	  echo "${YELLOW}Installing voice automation dependencies...${RESET}"; \
	  $(UV) pip install gtts pydub --python $(PYTHON); \
	fi
	@# Check ffmpeg
	@if ! command -v ffmpeg >/dev/null 2>&1; then \
	  echo "${RED}Error: ffmpeg not found${RESET}"; \
	  echo "Please install ffmpeg:"; \
	  echo "  macOS: ${GREEN}brew install ffmpeg${RESET}"; \
	  echo "  Ubuntu: ${GREEN}sudo apt-get install ffmpeg${RESET}"; \
	  exit 1; \
	fi
	@$(PYTHON) tests/generate_test_audio.py
	@echo "${GREEN}✓ Test audio files generated${RESET}"

.PHONY: test-voice-automated
test-voice-automated: check-env ## Run automated voice tests
	@echo "${BLUE}Running automated voice tests...${RESET}"
	@# Check if test script exists
	@if [ ! -f "tests/test_voice_automated.py" ]; then \
	  echo "${RED}Error: tests/test_voice_automated.py not found${RESET}"; \
	  echo "Please copy the script to tests/ directory"; \
	  exit 1; \
	fi
	@# Generate audio files if they don't exist
	@if [ ! -d "tests/audio" ] || [ -z "$$(ls -A tests/audio 2>/dev/null)" ]; then \
	  echo "${YELLOW}Test audio files not found. Generating...${RESET}"; \
	  make generate-test-audio; \
	fi
	@# Check dependencies
	@if ! $(PYTHON) -c "import aiohttp" 2>/dev/null; then \
	  echo "${YELLOW}Installing aiohttp...${RESET}"; \
	  $(UV) pip install aiohttp --python $(PYTHON); \
	fi
	@# Check if Rasa is running
	@echo "${BLUE}Checking if Rasa voice server is running...${RESET}"
	@if ! curl -s http://localhost:5005/ > /dev/null 2>&1; then \
	  echo "${RED}Error: Rasa server is not running${RESET}"; \
	  echo ""; \
	  echo "${YELLOW}Please start Rasa in another terminal:${RESET}"; \
	  echo "  ${GREEN}make inspect-voice${RESET}"; \
	  echo ""; \
	  echo "Then run this command again."; \
	  exit 1; \
	fi
	@echo "${GREEN}✓ Rasa server is running${RESET}"
	@# Run automated tests
	@$(PYTHON) tests/test_voice_automated.py

.PHONY: install-voice-test-deps
install-voice-test-deps: ## Install dependencies for automated voice testing
	@echo "${BLUE}Installing voice testing dependencies...${RESET}"
	@$(UV) pip install gtts pydub aiohttp --python $(PYTHON)
	@echo "${GREEN}✓ Voice testing dependencies installed${RESET}"
	@echo ""
	@echo "${YELLOW}Note: You also need ffmpeg installed:${RESET}"
	@echo "  macOS: ${GREEN}brew install ffmpeg${RESET}"
	@echo "  Ubuntu: ${GREEN}sudo apt-get install ffmpeg${RESET}"

.PHONY: test-voice-pipeline
test-voice-pipeline: check-env ## Test full voice pipeline (mock ASR/TTS)
	@echo "${BLUE}Running voice pipeline tests...${RESET}"
	@$(PYTHON) tests/test_voice_full_pipeline.py

.PHONY: test-voice-production
test-voice-production: check-env ## Test with real ASR/TTS services
	@echo "${BLUE}Running production voice tests...${RESET}"
	@if [ -z "$$DEEPGRAM_API_KEY" ] && [ -z "$$AZURE_SPEECH_API_KEY" ]; then \
	  echo "${RED}Error: No ASR/TTS service configured${RESET}"; \
	  echo "Set DEEPGRAM_API_KEY or AZURE_SPEECH_API_KEY"; \
	  exit 1; \
	fi
	@$(PYTHON) tests/test_voice_production.py

.DEFAULT_GOAL := help