#!/bin/bash
set -e  # Exit on error

echo "=================================================================="
echo "NeuTTS Complete Setup"
echo "=================================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "services/neutts_service.py" ]; then
    echo "❌ Error: Run this from sovereign-voice-assistant directory"
    exit 1
fi

# Use Python from venv (uv is in system PATH)
PYTHON="../../../.venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "❌ Error: Virtual environment not found at ../../../.venv"
    echo "Run 'make setup' from project root first"
    exit 1
fi

echo "Using Python: $PYTHON"
echo "Using uv from PATH: $(which uv)"
echo ""

# Check espeak
echo "Step 1: Checking system dependencies..."
if ! command -v espeak >/dev/null 2>&1; then
    echo "❌ espeak not found"
    echo "Install with: brew install espeak"
    exit 1
fi
echo "✓ espeak installed: $(espeak --version 2>&1 | head -n1)"
echo ""

# Install Python dependencies (without perth)
echo "Step 2: Installing Python dependencies..."
echo "This will take a few minutes..."
uv pip install \
    "llama-cpp-python>=0.2.0" \
    "onnxruntime>=1.16.0" \
    "neucodec==0.0.4" \
    "phonemizer>=3.3.0" \
    --python "$PYTHON" \
    --break-system-packages
echo "✓ Core dependencies installed"
echo ""

# Install neuttsair module
echo "Step 3: Installing neuttsair module..."
SITE_PACKAGES=$($PYTHON -c "import site; print(site.getsitepackages()[0])")
echo "Site packages: $SITE_PACKAGES"

if [ ! -d "$SITE_PACKAGES/neuttsair" ]; then
    echo "Cloning neutts-air repository..."
    rm -rf /tmp/neutts-air-install
    git clone https://github.com/neuphonic/neutts-air.git /tmp/neutts-air-install
    
    echo "Copying neuttsair module..."
    mkdir -p "$SITE_PACKAGES/neuttsair"
    cp /tmp/neutts-air-install/neuttsair/__init__.py "$SITE_PACKAGES/neuttsair/"
    cp /tmp/neutts-air-install/neuttsair/neutts.py "$SITE_PACKAGES/neuttsair/"
    
    rm -rf /tmp/neutts-air-install
    echo "✓ neuttsair module installed"
else
    echo "✓ neuttsair module already installed"
fi
echo ""

# Disable watermarking
echo "Step 4: Disabling watermarking..."
NEUTTS_FILE="$SITE_PACKAGES/neuttsair/neutts.py"
if grep -q "self.watermarker = perth.PerthImplicitWatermarker()" "$NEUTTS_FILE" 2>/dev/null; then
    cp "$NEUTTS_FILE" "${NEUTTS_FILE}.bak"
    sed -i '' 's/self.watermarker = perth.PerthImplicitWatermarker()/self.watermarker = None  # Watermarking disabled/g' "$NEUTTS_FILE"
    echo "✓ Watermarking disabled"
    echo "  Backup: ${NEUTTS_FILE}.bak"
else
    echo "✓ Already disabled or different format"
fi
echo ""

# Verify installation
echo "Step 5: Verifying installation..."
$PYTHON << 'PYEOF'
try:
    import neuttsair
    print("✓ neuttsair imports successfully")
    import os
    neutts_file = os.path.join(os.path.dirname(neuttsair.__file__), 'neutts.py')
    print(f"  Location: {neutts_file}")
except Exception as e:
    print(f"❌ Verification failed: {e}")
    exit(1)
PYEOF
echo ""

echo "=================================================================="
echo "✓ Setup Complete!"
echo "=================================================================="
echo ""
echo "Next steps:"
echo "  1. Test: make test-neutts-quick"
echo "  2. Update credentials.yml: make use-neutts"
echo "  3. Run: make inspect-voice-clean"
echo ""