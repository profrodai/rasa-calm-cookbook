# recipes/level-2-intermediate/sovereign-voice-assistant/tests/generate_test_audio.py
#!/usr/bin/env python3
"""
Generate Test Audio Files for Automated Voice Testing

This script generates WAV audio files from text using Google Text-to-Speech.
These files can be used for automated voice testing.

Usage:
    python tests/generate_test_audio.py
    
Requirements:
    pip install gtts pydub
"""

from gtts import gTTS
from pydub import AudioSegment
from pathlib import Path
import os

# Configuration
OUTPUT_DIR = Path("tests/audio")
LANGUAGE = 'en'
TLD = 'com'  # Top-level domain for accent (com=US, co.uk=UK, etc.)

# Test utterances to generate
TEST_UTTERANCES = {
    # Check Balance Flow
    "check_balance.wav": "What's my balance?",
    "checking.wav": "Checking",
    "savings.wav": "Savings",
    
    # Transfer Money Flow
    "transfer_money.wav": "I want to transfer money",
    "five_hundred.wav": "Five hundred dollars",
    "yes.wav": "Yes",
    "no.wav": "No",
    
    # Lost Card Flow
    "lost_card.wav": "I lost my card",
    "card_digits.wav": "Four five three two",
    
    # Additional useful phrases
    "cancel.wav": "Cancel",
    "help.wav": "Help",
    "goodbye.wav": "Goodbye",
}


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {OUTPUT_DIR}")


def generate_audio_file(filename: str, text: str):
    """Generate a WAV audio file from text."""
    output_path = OUTPUT_DIR / filename
    
    try:
        # Generate MP3 using gTTS
        print(f"🎤 Generating: '{text}' -> {filename}")
        tts = gTTS(text=text, lang=LANGUAGE, tld=TLD, slow=False)
        
        # Save to temporary MP3
        temp_mp3 = output_path.with_suffix('.mp3')
        tts.save(str(temp_mp3))
        
        # Convert MP3 to WAV (required format for Rasa)
        audio = AudioSegment.from_mp3(str(temp_mp3))
        
        # Export as WAV with settings for voice
        audio.export(
            str(output_path),
            format="wav",
            parameters=[
                "-ar", "16000",  # 16kHz sample rate (standard for speech)
                "-ac", "1",      # Mono channel
            ]
        )
        
        # Clean up temporary MP3
        temp_mp3.unlink()
        
        print(f"   ✓ Created: {output_path}")
        return True
        
    except Exception as e:
        print(f"   ✗ Failed to generate {filename}: {e}")
        return False


def check_dependencies():
    """Check if required libraries are installed."""
    try:
        import gtts
        import pydub
        print("✓ Dependencies installed (gtts, pydub)")
        return True
    except ImportError as e:
        print("✗ Missing dependencies!")
        print("\nPlease install:")
        print("  pip install gtts pydub")
        print("\nNote: pydub also requires ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        return False


def main():
    """Generate all test audio files."""
    print("=" * 60)
    print("Test Audio File Generator")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Create output directory
    ensure_output_dir()
    print()
    
    # Generate all files
    print("Generating audio files...")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for filename, text in TEST_UTTERANCES.items():
        if generate_audio_file(filename, text):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("-" * 60)
    print()
    print(f"✓ Successfully generated: {success_count} files")
    if fail_count > 0:
        print(f"✗ Failed: {fail_count} files")
    print()
    print("=" * 60)
    print("Audio files are ready for testing!")
    print(f"Location: {OUTPUT_DIR.absolute()}")
    print()
    print("Next steps:")
    print("  1. Start Rasa: make inspect-voice")
    print("  2. Run tests: python tests/test_voice_automated.py")
    print("=" * 60)
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())