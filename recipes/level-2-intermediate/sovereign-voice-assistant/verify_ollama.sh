#!/bin/bash
# verify_ollama.sh - Verify Ollama setup for Rasa

echo "=================================="
echo "Ollama Setup Verification"
echo "=================================="
echo ""

# Check if Ollama is running
echo "1. Checking Ollama service..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama is running on http://localhost:11434"
else
    echo "   ❌ Ollama is not running"
    echo "      Start it with: ollama serve"
    exit 1
fi

echo ""

# Check if ministral model is available
echo "2. Checking for ministral-3:14b model..."
if curl -s http://localhost:11434/api/tags | grep -q "ministral-3:14b"; then
    echo "   ✅ ministral-3:14b model is available"
else
    echo "   ❌ ministral-3:14b model not found"
    echo "      Download it with: ollama pull ministral-3:14b"
    exit 1
fi

echo ""

# Show model info
echo "3. Available Ollama models:"
curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | sed 's/^/   - /'

echo ""

# Check Rasa config
echo "4. Checking Rasa configuration..."
if [ -f "config.yml" ]; then
    if grep -q "model_group: ollama_llm" config.yml; then
        echo "   ✅ config.yml is set to use ollama_llm"
    else
        echo "   ⚠️  config.yml is not set to use ollama_llm"
        echo "      Current model_group: $(grep "model_group:" config.yml | head -1)"
    fi
else
    echo "   ⚠️  config.yml not found in current directory"
fi

echo ""

# Check endpoints.yml
echo "5. Checking endpoints configuration..."
if [ -f "endpoints.yml" ]; then
    if grep -q "id: ollama_llm" endpoints.yml; then
        echo "   ✅ ollama_llm model group defined in endpoints.yml"
    else
        echo "   ❌ ollama_llm model group not found in endpoints.yml"
    fi
else
    echo "   ⚠️  endpoints.yml not found in current directory"
fi

echo ""
echo "=================================="
echo "Verification Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. If all checks passed, start Rasa: rasa run"
echo "  2. Or test in shell mode: rasa shell"
echo "  3. To switch to OpenAI, change model_group in config.yml to: openai_llm"
echo ""