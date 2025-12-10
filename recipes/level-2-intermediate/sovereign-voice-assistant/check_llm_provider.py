# recipes/level-2-intermediate/sovereign-voice-assistant/check_llm_provider.py
"""
Check which LLM provider is configured and verify connectivity.
This script helps visualize which provider (OpenAI vs Ollama) is active.
"""

import sys
import os

# Check for required dependencies and install if needed
try:
    import yaml
    import requests
except ImportError:
    print("Installing required dependencies (yaml, requests)...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "requests", "--break-system-packages", "--quiet"])
    import yaml
    import requests

from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_header(text):
    """Print a styled header."""
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}{text:^70}{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def load_config(config_path="config.yml"):
    """Load and parse config.yml."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print_error(f"Config file not found: {config_path}")
        return None
    except yaml.YAMLError as e:
        print_error(f"Error parsing config: {e}")
        return None


def load_endpoints(endpoints_path="endpoints.yml"):
    """Load and parse endpoints.yml."""
    try:
        with open(endpoints_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print_error(f"Endpoints file not found: {endpoints_path}")
        return None
    except yaml.YAMLError as e:
        print_error(f"Error parsing endpoints: {e}")
        return None


def get_model_group_config(endpoints, model_group_id):
    """Extract model group configuration."""
    if not endpoints or 'model_groups' not in endpoints:
        return None
    
    for group in endpoints['model_groups']:
        if group.get('id') == model_group_id:
            return group
    return None


def check_ollama_connection(api_base="http://localhost:11434"):
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{api_base}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            return True, models
        return False, []
    except Exception as e:
        return False, []


def check_openai_key():
    """Check if OpenAI API key is set."""
    return os.getenv('OPENAI_API_KEY') is not None


def main():
    """Main function to check LLM configuration."""
    print_header("LLM Provider Configuration Check")
    
    # Load configuration files
    print_info("Loading configuration files...")
    config = load_config()
    endpoints = load_endpoints()
    
    if not config or not endpoints:
        print_error("Failed to load configuration files")
        return 1
    
    # Extract model group from config
    pipeline = config.get('pipeline', [])
    llm_component = None
    for component in pipeline:
        if component.get('name') == 'CompactLLMCommandGenerator':
            llm_component = component
            break
    
    if not llm_component:
        print_error("CompactLLMCommandGenerator not found in config")
        return 1
    
    model_group_id = llm_component.get('llm', {}).get('model_group')
    if not model_group_id:
        print_error("No model_group specified in config")
        return 1
    
    print_success(f"Active model group: {BOLD}{model_group_id}{RESET}")
    
    # Get model group details
    group_config = get_model_group_config(endpoints, model_group_id)
    if not group_config:
        print_error(f"Model group '{model_group_id}' not found in endpoints.yml")
        return 1
    
    # Display model configuration
    print(f"\n{BOLD}Configuration Details:{RESET}")
    models = group_config.get('models', [])
    if not models:
        print_error("No models defined in model group")
        return 1
    
    model_config = models[0]  # Get first model
    provider = model_config.get('provider', 'unknown')
    model_name = model_config.get('model', 'unknown')
    api_base = model_config.get('api_base', 'N/A')
    
    print(f"  Provider: {BOLD}{provider.upper()}{RESET}")
    print(f"  Model: {BOLD}{model_name}{RESET}")
    if api_base != 'N/A':
        print(f"  API Base: {api_base}")
    print(f"  Temperature: {model_config.get('temperature', 'N/A')}")
    print(f"  Max Tokens: {model_config.get('max_tokens', 'N/A')}")
    print(f"  Timeout: {model_config.get('timeout', 'N/A')}s")
    
    # Provider-specific checks
    print(f"\n{BOLD}Connectivity Check:{RESET}")
    
    if provider == 'ollama':
        print_info("Checking Ollama service...")
        is_running, available_models = check_ollama_connection(api_base)
        
        if is_running:
            print_success(f"Ollama is running at {api_base}")
            print(f"\n  {BOLD}Available models:{RESET}")
            for model in available_models:
                marker = "→" if model == model_name else " "
                print(f"    {marker} {model}")
            
            if model_name in available_models:
                print_success(f"\nConfigured model '{model_name}' is available")
            else:
                print_error(f"\nConfigured model '{model_name}' is NOT available")
                print(f"    Run: ollama pull {model_name}")
        else:
            print_error(f"Cannot connect to Ollama at {api_base}")
            print(f"    Start Ollama: ollama serve")
            return 1
    
    elif provider == 'openai':
        print_info("Checking OpenAI configuration...")
        if check_openai_key():
            print_success("OPENAI_API_KEY environment variable is set")
            print_info(f"Will use model: {model_name}")
        else:
            print_error("OPENAI_API_KEY environment variable is NOT set")
            print(f"    Set it: export OPENAI_API_KEY=your-key")
            return 1
    
    else:
        print_info(f"Provider '{provider}' detected")
        print(f"    Manual verification may be required")
    
    # Summary
    print_header("Summary")
    
    if provider == 'ollama':
        print(f"{GREEN}{BOLD}✓ SOVEREIGN STACK MODE{RESET}")
        print(f"  All processing happens locally on your machine")
        print(f"  No data leaves your infrastructure")
    elif provider == 'openai':
        print(f"{YELLOW}{BOLD}⚠ CLOUD MODE{RESET}")
        print(f"  Using external API service")
        print(f"  Data will be sent to OpenAI servers")
    
    print(f"\n{BOLD}To switch providers:{RESET}")
    print(f"  • Quick: {GREEN}make use-ollama{RESET} or {GREEN}make use-openai{RESET}")
    print(f"  • Manual: Edit config.yml, change model_group to 'openai_llm' or 'ollama_llm'")
    
    print(f"\n{GREEN}{BOLD}✓ Configuration is valid and ready to use{RESET}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())