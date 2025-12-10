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
	@echo '${YELLOW}Available Targets:${RESET}'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${YELLOW}%-15s${GREEN}%s${RESET}\n", $$1, $$2}' $(MAKEFILE_LIST)
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

.PHONY: setup-env
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

.PHONY: install-deps
install-deps: check-venv ## Install all recipe dependencies
	@echo "${BLUE}Installing recipe dependencies...${RESET}"
	@echo "${YELLOW}Installing base dependencies...${RESET}"
	@$(UV) pip install openai websockets aiohttp pyyaml requests --python $(PYTHON)
	@echo "${GREEN}✓ Base dependencies installed${RESET}"

.PHONY: install-voice-full
install-voice-full: check-venv ## Install full voice support (PyAudio, Torch, etc - requires system libs)
	@echo "${BLUE}Installing full voice support dependencies...${RESET}"
	@echo "${YELLOW}WARNING: This will install large dependencies (~2-3GB):${RESET}"
	@echo "  - PyTorch (ML framework)"
	@echo "  - Transformers (HuggingFace)"
	@echo "  - Audio processing libraries (librosa, soundfile, etc)"
	@echo ""
	@echo "${YELLOW}System requirements:${RESET}"
	@echo "  macOS:   ${GREEN}brew install portaudio${RESET}"
	@echo "  Ubuntu:  ${GREEN}sudo apt-get install portaudio19-dev python3-pyaudio${RESET}"
	@echo ""
	@read -p "Continue with installation? (y/N) " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "Installation cancelled"; \
		exit 0; \
	fi
	@echo ""
	@echo "${BLUE}Installing PyAudio (requires portaudio)...${RESET}"
	@if ! $(UV) pip install pyaudio --python $(PYTHON) 2>/dev/null; then \
		echo "${RED}✗ PyAudio installation failed${RESET}"; \
		echo "Please install portaudio first:"; \
		echo "  macOS:   ${GREEN}brew install portaudio${RESET}"; \
		echo "  Ubuntu:  ${GREEN}sudo apt-get install portaudio19-dev${RESET}"; \
		exit 1; \
	fi
	@echo "${GREEN}✓ PyAudio installed${RESET}"
	@echo ""
	@echo "${BLUE}Installing audio processing libraries...${RESET}"
	@$(UV) pip install \
		"librosa==0.11.0" \
		"soundfile==0.13.1" \
		"phonemizer==3.3.0" \
		--python $(PYTHON)
	@echo "${GREEN}✓ Audio libraries installed${RESET}"
	@echo ""
	@echo "${BLUE}Installing PyTorch (this may take several minutes)...${RESET}"
	@$(UV) pip install "torch==2.8.0" --python $(PYTHON)
	@echo "${GREEN}✓ PyTorch installed${RESET}"
	@echo ""
	@echo "${BLUE}Installing ML libraries...${RESET}"
	@$(UV) pip install \
		"transformers==4.56.1" \
		"neucodec>=0.0.4" \
		"resemble-perth==1.0.1" \
		--python $(PYTHON)
	@echo "${GREEN}✓ ML libraries installed${RESET}"
	@echo ""
	@echo "${GREEN}✓ Full voice support installed successfully!${RESET}"
	@echo ""
	@echo "${YELLOW}Next steps for local voice:${RESET}"
	@echo "  1. These libraries enable local TTS/ASR alternatives"
	@echo "  2. You can now replace Deepgram/Rime with local options"
	@echo "  3. See documentation for configuration"

.PHONY: check-voice-support
check-voice-support: check-venv ## Check voice support installation status
	@echo "${BLUE}Voice Support Status${RESET}"
	@echo ""
	@echo "${YELLOW}System Dependencies:${RESET}"
	@if command -v ffmpeg >/dev/null 2>&1; then \
		echo "  ${GREEN}✓ ffmpeg${RESET}"; \
	else \
		echo "  ${RED}✗ ffmpeg${RESET} (brew install ffmpeg)"; \
	fi
	@# Check portaudio (indirect - through pyaudio import)
	@if $(PYTHON) -c "import pyaudio" 2>/dev/null; then \
		echo "  ${GREEN}✓ portaudio (via pyaudio)${RESET}"; \
	else \
		echo "  ${YELLOW}- portaudio${RESET} (brew install portaudio)"; \
	fi
	@echo ""
	@echo "${YELLOW}Voice Testing Libraries:${RESET}"
	@for pkg in gtts pydub; do \
		if $(PYTHON) -c "import $$pkg" 2>/dev/null; then \
			echo "  ${GREEN}✓ $$pkg${RESET}"; \
		else \
			echo "  ${YELLOW}- $$pkg${RESET} (make install-voice-deps)"; \
		fi; \
	done
	@echo ""
	@echo "${YELLOW}Full Voice Support (Local TTS/ASR):${RESET}"
	@for pkg in pyaudio librosa soundfile phonemizer torch transformers; do \
		pkg_import=$$(echo $$pkg | sed 's/-/_/g'); \
		if $(PYTHON) -c "import $$pkg_import" 2>/dev/null; then \
			echo "  ${GREEN}✓ $$pkg${RESET}"; \
		else \
			echo "  ${YELLOW}- $$pkg${RESET} (make install-voice-full)"; \
		fi; \
	done
	@if $(PYTHON) -c "import neucodec" 2>/dev/null; then \
		echo "  ${GREEN}✓ neucodec${RESET}"; \
	else \
		echo "  ${YELLOW}- neucodec${RESET} (make install-voice-full)"; \
	fi
	@if $(PYTHON) -c "import resemble_perth" 2>/dev/null; then \
		echo "  ${GREEN}✓ resemble-perth${RESET}"; \
	else \
		echo "  ${YELLOW}- resemble-perth${RESET} (make install-voice-full)"; \
	fi
	@echo ""
	@echo "${YELLOW}Cloud Voice Services:${RESET}"
	@if $(PYTHON) -c "import azure.cognitiveservices.speech" 2>/dev/null; then \
		echo "  ${GREEN}✓ azure-speech${RESET}"; \
	else \
		echo "  ${YELLOW}- azure-speech${RESET} (make install-azure-speech)"; \
	fi
	@echo ""
	@echo "${YELLOW}Summary:${RESET}"
	@if $(PYTHON) -c "import torch, transformers, librosa" 2>/dev/null; then \
		echo "  ${GREEN}✓ Full voice support is installed${RESET}"; \
		echo "    You can use local TTS/ASR alternatives"; \
	else \
		echo "  ${YELLOW}○ Full voice support not installed${RESET}"; \
		echo "    Run: ${GREEN}make install-voice-full${RESET}"; \
	fi

.PHONY: install-system-voice-deps
install-system-voice-deps: ## Show instructions for installing system voice dependencies
	@echo "${BLUE}System Voice Dependencies${RESET}"
	@echo ""
	@echo "${YELLOW}Required system packages:${RESET}"
	@echo ""
	@echo "${BLUE}macOS:${RESET}"
	@echo "  ${GREEN}brew install portaudio${RESET}  # For PyAudio"
	@echo "  ${GREEN}brew install ffmpeg${RESET}     # For audio processing"
	@echo ""
	@echo "${BLUE}Ubuntu/Debian:${RESET}"
	@echo "  ${GREEN}sudo apt-get update${RESET}"
	@echo "  ${GREEN}sudo apt-get install portaudio19-dev python3-pyaudio${RESET}"
	@echo "  ${GREEN}sudo apt-get install ffmpeg${RESET}"
	@echo ""
	@echo "${BLUE}After installing system packages:${RESET}"
	@echo "  ${GREEN}make install-voice-full${RESET}  # Install Python packages"
	@echo ""
	@echo "${YELLOW}Note: Full voice support requires ~2-3GB of disk space${RESET}"

.PHONY: uninstall-voice-full
uninstall-voice-full: check-venv ## Uninstall full voice support (frees ~2-3GB)
	@echo "${BLUE}Uninstalling full voice support...${RESET}"
	@echo "${YELLOW}This will remove: PyTorch, Transformers, and related packages${RESET}"
	@read -p "Continue? (y/N) " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "Cancelled"; \
		exit 0; \
	fi
	@$(UV) pip uninstall -y \
		torch \
		transformers \
		librosa \
		soundfile \
		phonemizer \
		neucodec \
		resemble-perth \
		pyaudio \
		2>/dev/null || true
	@echo "${GREEN}✓ Full voice support uninstalled${RESET}"
	@echo "${YELLOW}Note: System packages (portaudio, ffmpeg) were not removed${RESET}"

.PHONY: install-voice-deps
install-voice-deps: check-venv ## Install voice testing dependencies
	@echo "${BLUE}Installing voice testing dependencies...${RESET}"
	@$(UV) pip install gtts pydub aiohttp --python $(PYTHON)
	@echo "${GREEN}✓ Voice testing dependencies installed${RESET}"
	@echo ""
	@echo "${YELLOW}Note: You also need ffmpeg installed:${RESET}"
	@echo "  macOS: ${GREEN}brew install ffmpeg${RESET}"
	@echo "  Ubuntu: ${GREEN}sudo apt-get install ffmpeg${RESET}"

.PHONY: install-azure-speech
install-azure-speech: check-venv ## Install Azure speech services
	@echo "${BLUE}Installing Azure speech services...${RESET}"
	@$(UV) pip install azure-cognitiveservices-speech --python $(PYTHON)
	@echo "${GREEN}✓ Azure speech services installed${RESET}"

.PHONY: check-deps
check-deps: check-venv ## Check if required dependencies are installed
	@echo "${BLUE}Checking dependencies...${RESET}"
	@echo ""
	@echo "${YELLOW}Base dependencies:${RESET}"
	@for pkg in openai websockets aiohttp pyyaml requests; do \
		if $(PYTHON) -c "import $$pkg" 2>/dev/null; then \
			echo "  ${GREEN}✓ $$pkg${RESET}"; \
		else \
			echo "  ${RED}✗ $$pkg${RESET}"; \
		fi; \
	done
	@echo ""
	@echo "${YELLOW}Voice testing (optional):${RESET}"
	@for pkg in gtts pydub; do \
		if $(PYTHON) -c "import $$pkg" 2>/dev/null; then \
			echo "  ${GREEN}✓ $$pkg${RESET}"; \
		else \
			echo "  ${YELLOW}- $$pkg (run: make install-voice-deps)${RESET}"; \
		fi; \
	done
	@echo ""
	@echo "${YELLOW}Azure speech (optional):${RESET}"
	@if $(PYTHON) -c "import azure.cognitiveservices.speech" 2>/dev/null; then \
		echo "  ${GREEN}✓ azure-cognitiveservices-speech${RESET}"; \
	else \
		echo "  ${YELLOW}- azure-cognitiveservices-speech (run: make install-azure-speech)${RESET}"; \
	fi
	@echo ""
	@echo "${YELLOW}System tools:${RESET}"
	@if command -v ffmpeg >/dev/null 2>&1; then \
		echo "  ${GREEN}✓ ffmpeg${RESET}"; \
	else \
		echo "  ${YELLOW}- ffmpeg (brew install ffmpeg)${RESET}"; \
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

.PHONY: pre-commit
pre-commit: format lint test ## Run all checks before committing
	@echo "${GREEN}✓ All checks passed${RESET}"

.PHONY: structure
structure: ## Show project structure
	@echo "${YELLOW}Current Project Structure:${RESET}"
	@echo "${BLUE}"
	@if command -v tree > /dev/null; then \
		tree -a -I '.git|.venv|__pycache__|*.pyc|*.pyo|*.pyd|.pytest_cache|.ruff_cache|.coverage|htmlcov'; \
	else \
		find . -not -path '*/\.*' -not -path '*.pyc' -not -path '*/__pycache__/*' \
			-not -path './.venv/*' -not -path './build/*' -not -path './dist/*' \
			-not -path './*.egg-info/*' \
			| sort | \
			sed -e "s/[^-][^\/]*\// │   /g" -e "s/├── /│── /" -e "s/└── /└── /"; \
	fi
	@echo "${RESET}"

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

.PHONY: check-llm
check-llm: ## Check current LLM provider configuration
	@echo "${BLUE}Checking LLM provider configuration...${RESET}"
	@$(PYTHON) check_llm_provider.py

.PHONY: use-ollama
use-ollama: ## Switch to Ollama (local)
	@echo "${BLUE}Switching to Ollama (local sovereign stack)...${RESET}"
	@sed -i.bak 's/model_group: openai_llm/model_group: ollama_llm/' config.yml || \
	 sed -i.bak 's/model_group: [a-z_]*/model_group: ollama_llm/' config.yml
	@rm -f config.yml.bak
	@echo "${GREEN}✓ Switched to Ollama${RESET}"
	@echo ""
	@$(PYTHON) check_llm_provider.py

.PHONY: use-openai
use-openai: ## Switch to OpenAI (cloud)
	@echo "${BLUE}Switching to OpenAI (cloud)...${RESET}"
	@sed -i.bak 's/model_group: ollama_llm/model_group: openai_llm/' config.yml || \
	 sed -i.bak 's/model_group: [a-z_]*/model_group: openai_llm/' config.yml
	@rm -f config.yml.bak
	@echo "${GREEN}✓ Switched to OpenAI${RESET}"
	@echo ""
	@$(PYTHON) check_llm_provider.py

.PHONY: show-provider
show-provider: ## Show current provider (simple)
	@echo "${BLUE}Current LLM provider:${RESET}"
	@grep "model_group:" config.yml | head -1 | sed 's/.*model_group: /  /'


test-with-provider: check-llm ## Test with visual provider indication
	@echo ""
	@echo "${BLUE}Starting tests...${RESET}"
	@$(PYTHON) -m rasa test


run-with-check: check-llm ## Run Rasa with provider check first
	@echo ""
	@read -p "Press Enter to start Rasa with this configuration..." dummy
	@$(PYTHON) -m rasa run

# Shell with provider check
shell-with-check: check-llm
	@echo ""
	@read -p "Press Enter to start Rasa shell with this configuration..." dummy
	@$(PYTHON) -m rasa shell

# Inspect with provider check
inspect-with-check: check-llm
	@echo ""
	@read -p "Press Enter to start Rasa inspector with this configuration..." dummy
	@$(PYTHON) -m rasa inspect

# Inspect voice with provider check
inspect-voice-with-check: check-llm
	@echo ""
	@read -p "Press Enter to start Rasa voice inspector with this configuration..." dummy
	@$(PYTHON) -m rasa inspect --voice

.PHONY: install-neutts
install-neutts: check-venv ## Install NeuTTS Air (drop-in Rime replacement)
	@echo "${BLUE}Installing NeuTTS Air...${RESET}"
	@echo ""
	@echo "${YELLOW}Checking system dependencies...${RESET}"
	@if ! command -v espeak >/dev/null 2>&1; then \
		echo "${RED}✗ espeak not found${RESET}"; \
		echo ""; \
		echo "${YELLOW}Please install espeak first:${RESET}"; \
		echo "  macOS:   ${GREEN}brew install espeak${RESET}"; \
		echo "  Ubuntu:  ${GREEN}sudo apt-get install espeak${RESET}"; \
		echo ""; \
		echo "Then run: ${GREEN}make install-neutts${RESET}"; \
		exit 1; \
	fi
	@echo "  ${GREEN}✓ espeak installed${RESET}"
	@echo ""
	@echo "${BLUE}Installing core dependencies...${RESET}"
	@$(UV) pip install llama-cpp-python onnxruntime neucodec phonemizer perth --python $(PYTHON)
	@echo "${GREEN}✓ Core dependencies installed${RESET}"
	@echo ""
	@echo "${BLUE}Installing neutts-air module...${RESET}"
	@echo "${YELLOW}Note: Copying Python module directly (no package installation)${RESET}"
	@# Create neuttsair directory in site-packages
	@SITE_PACKAGES=$$($(PYTHON) -c "import site; print(site.getsitepackages()[0])"); \
	NEUTTS_DIR="$$SITE_PACKAGES/neuttsair"; \
	TEMP_DIR=$$(mktemp -d); \
	echo "Cloning neutts-air repository..."; \
	git clone https://github.com/neuphonic/neutts-air.git "$$TEMP_DIR/neutts-air" --depth 1 --quiet; \
	echo "Installing neutts-air module to: $$NEUTTS_DIR"; \
	mkdir -p "$$NEUTTS_DIR"; \
	cp "$$TEMP_DIR/neutts-air/neuttsair/__init__.py" "$$NEUTTS_DIR/"; \
	cp "$$TEMP_DIR/neutts-air/neuttsair/neutts.py" "$$NEUTTS_DIR/"; \
	rm -rf "$$TEMP_DIR"; \
	if [ -f "$$NEUTTS_DIR/neutts.py" ]; then \
		echo "${GREEN}✓ neutts-air module installed${RESET}"; \
	else \
		echo "${RED}✗ neutts-air installation failed${RESET}"; \
		exit 1; \
	fi
	@echo ""
	@echo "${GREEN}✓ NeuTTS Air installation complete!${RESET}"
	@echo ""
	@echo "${YELLOW}Usage:${RESET}"
	@echo "  1. Update credentials.yml (see: ${GREEN}make use-neutts${RESET})"
	@echo "  2. Test: ${GREEN}make test-voice-production${RESET} (works as before)"
	@echo "  3. No manual voice setup needed - auto-generates from gtts!"

.PHONY: check-neutts
check-neutts: check-venv ## Check NeuTTS installation status
	@echo "${BLUE}NeuTTS Installation Check${RESET}"
	@echo ""
	@echo "${YELLOW}System Dependencies:${RESET}"
	@if command -v espeak >/dev/null 2>&1; then \
		echo "  ${GREEN}✓ espeak${RESET} $$(espeak --version 2>&1 | head -n1)"; \
	else \
		echo "  ${RED}✗ espeak${RESET} (brew install espeak)"; \
	fi
	@echo ""
	@echo "${YELLOW}Python Packages:${RESET}"
	@for pkg in neuttsair llama_cpp onnxruntime neucodec phonemizer perth; do \
		if $(PYTHON) -c "import $$pkg" 2>/dev/null; then \
			version=$$($(PYTHON) -c "import $$pkg; print(getattr($$pkg, '__version__', 'unknown'))" 2>/dev/null); \
			echo "  ${GREEN}✓ $$pkg${RESET} ($$version)"; \
		else \
			echo "  ${RED}✗ $$pkg${RESET} (make install-neutts)"; \
		fi; \
	done
	@echo ""
	@echo "${YELLOW}Module Location:${RESET}"
	@SITE_PACKAGES=$$($(PYTHON) -c "import site; print(site.getsitepackages()[0])"); \
	if [ -f "$$SITE_PACKAGES/neuttsair/neutts.py" ]; then \
		echo "  ${GREEN}✓ neuttsair module found${RESET}"; \
		echo "    $$SITE_PACKAGES/neuttsair/"; \
	else \
		echo "  ${RED}✗ neuttsair module not found${RESET}"; \
	fi
	@echo ""
	@echo "${YELLOW}Reference Generation:${RESET}"
	@if $(PYTHON) -c "import gtts, pydub" 2>/dev/null; then \
		echo "  ${GREEN}✓ gtts + pydub installed${RESET} (for auto-reference)"; \
	else \
		echo "  ${YELLOW}○ gtts + pydub missing${RESET} (make install-voice-deps)"; \
	fi
	@if [ -d ".neutts_cache" ]; then \
		echo "  ${GREEN}✓ Cache directory exists${RESET}"; \
		if [ -f ".neutts_cache/default_reference.wav" ]; then \
			echo "  ${GREEN}✓ Default reference cached${RESET}"; \
		fi; \
	fi
	@echo ""
	@echo "${YELLOW}Summary:${RESET}"
	@if $(PYTHON) -c "import neuttsair.neutts" 2>/dev/null && \
	   command -v espeak >/dev/null 2>&1; then \
		echo "  ${GREEN}✓ NeuTTS is ready to use${RESET}"; \
		echo "  ${GREEN}✓ No manual setup needed - auto-generates reference${RESET}"; \
	else \
		echo "  ${YELLOW}○ NeuTTS setup incomplete${RESET}"; \
		echo "    Run: ${GREEN}make install-neutts${RESET}"; \
	fi

.PHONY: use-neutts
use-neutts: check-neutts ## Show config to switch to NeuTTS (drop-in for Rime)
	@echo "${BLUE}Switching to NeuTTS (Local TTS)...${RESET}"
	@echo ""
	@if ! $(PYTHON) -c "import neuttsair" 2>/dev/null; then \
		echo "${RED}✗ NeuTTS not installed${RESET}"; \
		echo "Run: ${GREEN}make install-neutts${RESET}"; \
		exit 1; \
	fi
	@echo "${YELLOW}Update credentials.yml with:${RESET}"
	@echo ""
	@echo "browser_audio:"
	@echo "  tts:"
	@echo "    name: custom"
	@echo "    module: services.neutts_service.NeuTTSService"
	@echo "    config:"
	@echo "      backbone_repo: neuphonic/neutts-air-q8-gguf"
	@echo "      codec_repo: neuphonic/neucodec-onnx-decoder"
	@echo "      device: cpu"
	@echo "      auto_generate_reference: true  # No manual setup needed!"
	@echo ""
	@echo "${GREEN}✓ Configuration shown above${RESET}"
	@echo ""
	@echo "${YELLOW}Then test with:${RESET}"
	@echo "  ${GREEN}make test-voice-production${RESET}  # Your existing test"
	@echo "  ${GREEN}make inspect-voice${RESET}          # Interactive testing"

.PHONY: test-neutts-quick
test-neutts-quick: check-venv ## Quick test NeuTTS with auto-generated reference
	@if ! $(PYTHON) -c "import neuttsair" 2>/dev/null; then \
		echo "${RED}✗ NeuTTS not installed${RESET}"; \
		echo "Run: ${GREEN}make install-neutts${RESET}"; \
		exit 1; \
	fi
	@echo "${BLUE}Testing NeuTTS with auto-generated reference...${RESET}"
	@$(PYTHON) -c "from services.neutts_service import quick_test; quick_test()"
	@if [ -f test_output.wav ]; then \
		echo ""; \
		echo "${GREEN}✓ Test completed!${RESET}"; \
		echo "Audio saved to: ${GREEN}test_output.wav${RESET}"; \
		echo ""; \
		echo "Listen with:"; \
		echo "  macOS:  ${GREEN}afplay test_output.wav${RESET}"; \
		echo "  Linux:  ${GREEN}aplay test_output.wav${RESET}"; \
	fi

.PHONY: clean-neutts-cache
clean-neutts-cache: ## Clean NeuTTS cache (will regenerate on next use)
	@echo "${BLUE}Cleaning NeuTTS cache...${RESET}"
	@rm -rf .neutts_cache
	@rm -f test_output.wav
	@echo "${GREEN}✓ Cache cleaned${RESET}"
	@echo "${YELLOW}Reference will be regenerated on next use${RESET}"

.PHONY: uninstall-neutts
uninstall-neutts: check-venv ## Uninstall NeuTTS Air
	@echo "${BLUE}Uninstalling NeuTTS Air module...${RESET}"
	@SITE_PACKAGES=$$($(PYTHON) -c "import site; print(site.getsitepackages()[0])"); \
	rm -rf "$$SITE_PACKAGES/neuttsair"; \
	echo "${GREEN}✓ neuttsair module removed${RESET}"
	@echo "${YELLOW}Note: Core dependencies not removed (may be used elsewhere)${RESET}"

# Add this target to your Makefile for testing local fork

.PHONY: install-neutts-local
install-neutts-local: check-venv ## Install NeuTTS from local fork (for testing PR)
	@echo "${BLUE}Installing NeuTTS from local fork...${RESET}"
	@echo ""
	@FORK_PATH="$(HOME)/repos/profrodai/profrodai/neutts-air"; \
	if [ ! -d "$$FORK_PATH" ]; then \
		echo "${RED}✗ Fork not found at $$FORK_PATH${RESET}"; \
		exit 1; \
	fi; \
	echo "${YELLOW}Using fork at: $$FORK_PATH${RESET}"; \
	echo ""; \
	SITE_PACKAGES=$$($(PYTHON) -c "import site; print(site.getsitepackages()[0])"); \
	NEUTTS_DIR="$$SITE_PACKAGES/neuttsair"; \
	echo "Creating neuttsair directory..."; \
	mkdir -p "$$NEUTTS_DIR"; \
	echo "Copying files from fork..."; \
	cp "$$FORK_PATH/neuttsair/__init__.py" "$$NEUTTS_DIR/"; \
	cp "$$FORK_PATH/neuttsair/neutts.py" "$$NEUTTS_DIR/"; \
	if [ -f "$$NEUTTS_DIR/neutts.py" ]; then \
		echo "${GREEN}✓ Local fork installed${RESET}"; \
	else \
		echo "${RED}✗ Installation failed${RESET}"; \
		exit 1; \
	fi
	@echo ""
	@echo "${YELLOW}Verifying changes...${RESET}"
	@$(PYTHON) -c 'import neuttsair, inspect; \
source = inspect.getsource(neuttsair.NeuTTSAir.__init__); \
has_try = "try:" in source and "import perth" in source; \
has_espeak = "_configure_espeak_library" in open(neuttsair.__file__.replace("__init__.py", "neutts.py")).read(); \
print("  ✓ Perth try/except found" if has_try else "  ✗ Perth try/except missing"); \
print("  ✓ espeak auto-detection found" if has_espeak else "  ✗ espeak auto-detection missing"); \
print("  ✓ Your PR changes are active!" if (has_try and has_espeak) else "  ⚠ Some changes missing")'
	@echo ""
	@echo "${GREEN}✓ Ready to test!${RESET}"
	@echo "  Run: ${GREEN}make test-neutts-quick${RESET}"

.DEFAULT_GOAL := help