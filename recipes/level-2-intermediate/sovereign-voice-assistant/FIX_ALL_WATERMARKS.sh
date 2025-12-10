#!/bin/bash
# Fix all watermarker usage in neutts.py

PYTHON="../../../.venv/bin/python"
NEUTTS_FILE=$($PYTHON -c "import neuttsair, os; print(os.path.join(os.path.dirname(neuttsair.__file__), 'neutts.py'))")

echo "Fixing all watermarker usage in: $NEUTTS_FILE"
echo ""

# Backup
cp "$NEUTTS_FILE" "${NEUTTS_FILE}.watermark_fix_backup"
echo "✓ Backup created: ${NEUTTS_FILE}.watermark_fix_backup"

# Fix 1: In infer() method (line ~167)
echo "Fixing infer() method..."
sed -i '' 's/watermarked_wav = self\.watermarker\.apply_watermark(wav, sample_rate=24_000)/watermarked_wav = wav if self.watermarker is None else self.watermarker.apply_watermark(wav, sample_rate=24_000)/g' "$NEUTTS_FILE"

# Fix 2: In _infer_stream_ggml() method (line ~351 and ~377)
echo "Fixing _infer_stream_ggml() method..."
sed -i '' 's/recon = self\.watermarker\.apply_watermark(recon, sample_rate=24_000)/recon = recon if self.watermarker is None else self.watermarker.apply_watermark(recon, sample_rate=24_000)/g' "$NEUTTS_FILE"

echo ""
echo "✓ All watermarker calls patched!"
echo ""
echo "Changes made:"
echo "  1. infer() - watermark check added"
echo "  2. _infer_stream_ggml() - watermark checks added (2 places)"
echo ""
echo "Test with: make test-neutts-quick"