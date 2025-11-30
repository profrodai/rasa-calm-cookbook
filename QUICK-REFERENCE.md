# Quick Reference Guide

## Installation Commands

### First Time Setup (Recommended)
```bash
make setup
source .venv/bin/activate
```
Installs: Python 3.11 venv + Rasa core + dev tools + basic dependencies

---

## Install by Recipe Level

### Level 1 - Basic Recipes
```bash
make install-core      # Rasa Pro + Rasa SDK
make install-basic     # + OpenAI
```

### Level 2 - Intermediate Recipes
```bash
make install-intermediate  # + Voice (no pyaudio) + Search tools
```

### Level 2 - With Full Voice Support
```bash
make install-system-deps   # Install PortAudio (macOS/Linux)
make install-voice-full    # Install pyaudio
```

### Level 3 - Advanced Recipes
```bash
make install-advanced  # + Azure + Deployment tools
```

### Install Everything
```bash
make install-all  # Everything except pyaudio
```

---

## Working with Recipes

### List Available Recipes
```bash
make list-recipes
```

### Navigate to a Recipe
```bash
cd recipes/level-1-basic/basic-tutorial
```

### From Within a Recipe Directory
```bash
# Set your environment variables first
export RASA_LICENSE="your-license-key"
export OPENAI_API_KEY="your-api-key"

# Then run recipe commands
make train              # Train the model
make shell              # Test in command line
make inspect            # Launch Rasa Inspector
make run                # Start Rasa server
make test-e2e           # Run end-to-end tests
```

### From Root Directory
```bash
# Train a specific recipe from root
make train RECIPE_TARGET=basic-tutorial RECIPE_LEVEL=level-1-basic

# Test a specific recipe from root
make test-recipe RECIPE_TARGET=basic-tutorial RECIPE_LEVEL=level-1-basic

# Test all recipes
make test-all-recipes
```

---

## Development Commands

### Code Quality
```bash
make format     # Auto-format code with ruff, black, isort
make lint       # Check code quality
make test       # Run all tests
```

### Validation
```bash
make validate-recipe RECIPE_TARGET=basic-tutorial  # Validate one recipe
make validate-all                                   # Validate all recipes
```

### Environment Management
```bash
make check-env           # Check environment setup
make setup-env-all       # Create .env files for all recipes
make check-env-all       # Verify all recipes have .env files
```

---

## Cleanup Commands

```bash
make clean          # Clean build artifacts, cache, models, logs
make clean-models   # Clean only trained models
```

---

## Troubleshooting

### "uv is not installed"
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "RASA_LICENSE environment variable not set"
```bash
export RASA_LICENSE="your-license-key"
# Or add to .env file in recipe directory
```

### "No trained model found"
```bash
cd recipes/level-1-basic/basic-tutorial
make train
```

### Voice dependencies fail to install
```bash
# macOS
make install-system-deps  # Installs via Homebrew

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install portaudio19-dev
make install-voice-full

# Fedora
sudo dnf install portaudio-devel
make install-voice-full
```

### "Virtual environment not found"
```bash
make env          # Create venv only
# or
make setup        # Create venv + install deps
```

---

## Common Workflows

### Workflow 1: Start a New Recipe
```bash
# From root
make new-recipe RECIPE_TARGET=my-assistant RECIPE_LEVEL=level-1-basic

# Navigate and edit
cd recipes/level-1-basic/my-assistant
# Edit domain.yml, data/flows.yml, etc.
```

### Workflow 2: Test Changes
```bash
# From recipe directory
make train
make test-e2e

# Or from root
make test-recipe RECIPE_TARGET=my-assistant RECIPE_LEVEL=level-1-basic
```

### Workflow 3: Contributing
```bash
# Install dev dependencies
make install-dev

# Make changes
# ...

# Run checks
make format
make lint
make test
make validate-all

# Or all at once
make pre-commit
```

### Workflow 4: Quick Start with Tutorial
```bash
make quick-start
# Follow the printed instructions
```

---

## Environment Variables

Create a `.env` file in your recipe directory:

```bash
# Required
RASA_LICENSE=your-rasa-license-key

# For OpenAI recipes
OPENAI_API_KEY=your-openai-api-key

# For Azure recipes
AZURE_SPEECH_KEY=your-azure-key
AZURE_SPEECH_REGION=your-region
```

Or export them:
```bash
export RASA_LICENSE="your-key"
export OPENAI_API_KEY="your-key"
```

---

## Project Structure Commands

```bash
make structure   # Display project directory tree
make help        # Show all available commands
```

---

## Tips

1. **Always activate the venv**: `source .venv/bin/activate`
2. **Start with setup**: `make setup` for first-time users
3. **Work from recipe directory**: Most commands work best when run from within a recipe
4. **Use RECIPE_TARGET from root**: When you need to run commands from the root directory
5. **Install system deps first**: Before installing voice-full on Linux/macOS
6. **Check environment**: Use `make check-env` to verify your setup

---

## Getting Help

```bash
make help                    # Show all available commands
make recipe RECIPE_TARGET=X  # Show commands for specific recipe
cat recipes/*/README.md      # Read recipe documentation
```