# Terminal colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)
BLUE   := $(shell tput -Txterm setaf 4)
RED    := $(shell tput -Txterm setaf 1)

# Recipe settings
RECIPE_NAME := meeting-intelligence-agent
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

# Default meeting ID
MEETING_ID ?= sample_earnings_call
TITLE ?= Sample Earnings Call

# Include environment variables
ifneq (,$(wildcard $(ENV_FILE)))
    include $(ENV_FILE)
    export
endif

.PHONY: help
help: ## Show this help message
	@echo ''
	@echo '${YELLOW}$(RECIPE_NAME) - Meeting Intelligence Agent${RESET}'
	@echo ''
	@echo '${YELLOW}Quick Start:${RESET}'
	@echo '  1. ${GREEN}make setup-recipe${RESET}         - Install dependencies'
	@echo '  2. ${GREEN}make setup-env${RESET}            - Create .env file'
	@echo '  3. Edit .env with API keys'
	@echo '  4. ${GREEN}make download-sample-call${RESET} - Get sample audio'
	@echo '  5. ${GREEN}make process-meeting${RESET}      - Process the meeting'
	@echo '  6. ${GREEN}make train${RESET}                - Train Rasa model'
	@echo '  7. ${GREEN}make inspect-voice${RESET}        - Test with voice!'
	@echo ''
	@echo '${YELLOW}Meeting Processing:${RESET}'
	@echo '  Download:     ${GREEN}make download-sample-call${RESET}'
	@echo '  Process:      ${GREEN}make process-meeting MEETING_ID=my_call${RESET}'
	@echo '  Embeddings:   ${GREEN}make create-embeddings MEETING_ID=my_call${RESET}'
	@echo '  Search:       ${GREEN}make search-meeting MEETING_ID=my_call QUERY="margins"${RESET}'
	@echo ''
	@echo '${YELLOW}Voice Testing:${RESET}'
	@echo '  Voice:        ${GREEN}make inspect-voice${RESET}'
	@echo '  Text:         ${GREEN}make inspect${RESET}'
	@echo '  Shell:        ${GREEN}make shell${RESET}'
	@echo ''
	@echo '${YELLOW}Development:${RESET}'
	@echo '  Train:        ${GREEN}make train${RESET}'
	@echo '  Run:          ${GREEN}make run${RESET}'
	@echo '  Actions:      ${GREEN}make run-actions${RESET}'
	@echo '  Status:       ${GREEN}make status${RESET}'
	@echo ''

.PHONY: setup-env
setup-env: ## Create .env file from template
	@if [ ! -f "$(ENV_FILE)" ]; then \
	  cp $(ENV_EXAMPLE) $(ENV_FILE); \
	  echo "${YELLOW}Created $(ENV_FILE) - please edit with your credentials${RESET}"; \
	  echo "${YELLOW}Required: RASA_LICENSE, OPENAI_API_KEY, HF_TOKEN${RESET}"; \
	else \
	  echo "${GREEN}$(ENV_FILE) already exists${RESET}"; \
	fi

.PHONY: setup-recipe
setup-recipe: check-venv setup-env ## Install recipe dependencies
	@echo "${BLUE}Installing meeting intelligence dependencies...${RESET}"
	@echo "${YELLOW}This may take 5-10 minutes (downloading models)${RESET}"
	@$(UV) pip install \
	  pyannote.audio \
	  faster-whisper \
	  chromadb \
	  sentence-transformers \
	  openai \
	  websockets \
	  aiohttp \
	  pydub \
	  --python $(PYTHON)
	@echo "${GREEN}✓ Dependencies installed${RESET}"
	@echo ""
	@echo "${YELLOW}System Dependencies Required:${RESET}"
	@echo "  • ffmpeg: ${GREEN}brew install ffmpeg${RESET}"
	@echo "  • espeak-ng: ${GREEN}brew install espeak-ng${RESET}"
	@echo ""
	@echo "${YELLOW}Accept HuggingFace Model Terms:${RESET}"
	@echo "  Visit: https://huggingface.co/pyannote/speaker-diarization-community-1"

.PHONY: check-venv
check-venv: ## Check if virtual environment exists
	@if [ ! -f "$(PYTHON)" ]; then \
	  echo "${RED}✗ Virtual environment not found${RESET}"; \
	  echo "Run from repository root: ${GREEN}make setup${RESET}"; \
	  exit 1; \
	fi
	@echo "${GREEN}✓ Virtual environment found${RESET}"

.PHONY: check-env
check-env: check-venv ## Check environment prerequisites
	@echo "${BLUE}Checking environment...${RESET}"
	@if [ -z "$(RASA_LICENSE)" ]; then \
	  echo "${RED}Error: RASA_LICENSE not set${RESET}"; \
	  exit 1; \
	fi
	@if [ -z "$(OPENAI_API_KEY)" ]; then \
	  echo "${YELLOW}Warning: OPENAI_API_KEY not set${RESET}"; \
	fi
	@if [ -z "$(HF_TOKEN)" ]; then \
	  echo "${YELLOW}Warning: HF_TOKEN not set (needed for pyannote)${RESET}"; \
	fi
	@echo "${GREEN}✓ Environment check complete${RESET}"

.PHONY: download-sample-call
download-sample-call: ## Download sample earnings call audio
	@echo "${BLUE}Downloading sample earnings call...${RESET}"
	@$(PYTHON) recordings/download_sample_call.py
	@echo "${GREEN}✓ Sample call downloaded to recordings/${RESET}"

.PHONY: process-meeting
process-meeting: check-env ## Process a meeting (diarization + transcription + embeddings)
	@echo "${BLUE}Processing meeting: $(MEETING_ID)${RESET}"
	@$(PYTHON) -m meeting_processing $(MEETING_ID) "$(TITLE)"
	@echo "${GREEN}✓ Meeting processed${RESET}"

.PHONY: create-embeddings
create-embeddings: check-env ## Create vector embeddings for a meeting
	@echo "${BLUE}Creating embeddings for: $(MEETING_ID)${RESET}"
	@$(PYTHON) -m meeting_processing.vectordb create $(MEETING_ID)
	@echo "${GREEN}✓ Embeddings created${RESET}"

.PHONY: search-meeting
search-meeting: check-env ## Search a meeting (requires QUERY variable)
	@if [ -z "$(QUERY)" ]; then \
	  echo "${RED}Error: QUERY not set${RESET}"; \
	  echo "Usage: ${GREEN}make search-meeting MEETING_ID=my_call QUERY=\"margins\"${RESET}"; \
	  exit 1; \
	fi
	@$(PYTHON) -m meeting_processing.retrieval $(MEETING_ID) "$(QUERY)"

.PHONY: train
train: check-env ## Train Rasa model
	@echo "${BLUE}Training Rasa model...${RESET}"
	@$(RASA) train
	@echo "${GREEN}✓ Model trained${RESET}"

.PHONY: run
run: check-env ## Start Rasa server
	@echo "${BLUE}Starting Rasa server...${RESET}"
	@$(RASA) run --enable-api --cors "*"

.PHONY: run-actions
run-actions: ## Start action server
	@echo "${BLUE}Starting action server...${RESET}"
	@$(RASA) run actions

.PHONY: shell
shell: check-env ## Start Rasa shell
	@$(RASA) shell

.PHONY: inspect
inspect: check-env ## Start Rasa inspector
	@echo "${BLUE}Starting Rasa inspector...${RESET}"
	@$(RASA) inspect

.PHONY: inspect-voice
inspect-voice: check-env ## Start Rasa inspector with voice
	@echo "${BLUE}Starting voice inspector...${RESET}"
	@echo "${YELLOW}Remember to start action server in another terminal:${RESET}"
	@echo "  ${GREEN}make run-actions${RESET}"
	@$(RASA) inspect --voice

.PHONY: validate
validate: check-env ## Validate configuration
	@$(RASA) data validate

.PHONY: status
status: ## Show environment and meeting status
	@echo "${BLUE}Environment Status:${RESET}"
	@echo ""
	@if [ -n "$(RASA_LICENSE)" ]; then \
	  echo "  ✓ RASA_LICENSE set"; \
	else \
	  echo "  ✗ RASA_LICENSE not set"; \
	fi
	@if [ -n "$(OPENAI_API_KEY)" ]; then \
	  echo "  ✓ OPENAI_API_KEY set"; \
	else \
	  echo "  ✗ OPENAI_API_KEY not set"; \
	fi
	@if [ -n "$(HF_TOKEN)" ]; then \
	  echo "  ✓ HF_TOKEN set"; \
	else \
	  echo "  ✗ HF_TOKEN not set"; \
	fi
	@echo ""
	@echo "${BLUE}Processed Meetings:${RESET}"
	@if [ -d "meetings/processed" ]; then \
	  count=$$(ls -1 meetings/processed/*_transcript.json 2>/dev/null | wc -l); \
	  if [ $$count -gt 0 ]; then \
	    echo "  Found $$count processed meeting(s)"; \
	    ls -1 meetings/processed/*_transcript.json | sed 's|meetings/processed/||;s|_transcript.json||' | sed 's/^/    • /'; \
	  else \
	    echo "  No meetings processed yet"; \
	  fi; \
	else \
	  echo "  No meetings directory"; \
	fi

.PHONY: clean
clean: ## Clean generated files
	@echo "${BLUE}Cleaning generated files...${RESET}"
	@rm -rf models/ logs/ .rasa/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "${GREEN}✓ Cleanup complete${RESET}"

.PHONY: test-meeting-pipeline
test-meeting-pipeline: ## Test meeting processing pipeline
	@$(PYTHON) tests/test_meeting_pipeline.py

.PHONY: test-voice-production
test-voice-production: ## Test voice pipeline end-to-end
	@$(PYTHON) tests/test_voice_production.py

.DEFAULT_GOAL := help
MAKEFILE_END
echo "Makefile created"