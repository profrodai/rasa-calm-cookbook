import sys
import os
import warnings
import traceback
from pathlib import Path

# 1. Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 2. Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.absolute()))

import asyncio
import aiohttp
import logging
import wave
import json
import audioop  # Required for format conversion
import uuid
from typing import Optional, List, Dict

# Import your actual TTS service
try:
    from services.neutts_service import NeuTTSService, NeuTTSConfig
except ImportError as e:
    print(f"\n❌ CRITICAL ERROR: Could not import NeuTTSService.")
    traceback.print_exc()
    sys.exit(1)

# Configuration
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"
TEST_AUDIO_DIR = Path("tests/audio")
OUTPUT_DIR = Path("tests/audio_responses_real")
DEEPGRAM_URL = "https://api.deepgram.com/v1/listen?model=nova-2-general&smart_format=true"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

async def deepgram_transcribe(audio_path: Path, api_key: str) -> str:
    async with aiohttp.ClientSession() as session:
        with open(audio_path, 'rb') as audio_file:
            headers = {"Authorization": f"Token {api_key}", "Content-Type": "audio/wav"}
            async with session.post(DEEPGRAM_URL, headers=headers, data=audio_file) as response:
                if response.status != 200:
                    raise Exception(f"Deepgram Error {response.status}: {await response.text()}")
                data = await response.json()
                try:
                    return data['results']['channels'][0]['alternatives'][0]['transcript']
                except (KeyError, IndexError):
                    return ""

async def rasa_process(text: str, sender_id: str) -> List[str]:
    payload = {"sender": sender_id, "message": text}
    async with aiohttp.ClientSession() as session:
        async with session.post(RASA_URL, json=payload) as response:
            if response.status != 200:
                raise Exception(f"Rasa Error {response.status}")
            messages = await response.json()
            return [m.get("text") for m in messages if "text" in m]

async def neutts_synthesize(text: str, tts_service: NeuTTSService, output_path: Path):
    """
    Generates audio, converts it to standard WAV (Linear PCM), and saves it.
    """
    # 1. Collect all u-law encoded chunks from the service
    ulaw_data = bytearray()
    async for chunk in tts_service.synthesize(text):
        ulaw_data.extend(chunk)
    
    if not ulaw_data:
        raise Exception("TTS generated no audio data")

    # 2. Convert u-law (Rasa format) back to Linear PCM (Standard WAV format)
    # This is necessary because python's 'wave' module cannot write compressed files.
    # 2 = sample width (16-bit audio)
    pcm_data = audioop.ulaw2lin(ulaw_data, 2)

    # 3. Save as standard 16-bit 8kHz Mono WAV
    with wave.open(str(output_path), 'wb') as wav_file:
        wav_file.setnchannels(1)      # Mono
        wav_file.setsampwidth(2)      # 16-bit (2 bytes)
        wav_file.setframerate(8000)   # 8kHz
        wav_file.setcomptype('NONE', 'not compressed') # Standard PCM
        wav_file.writeframes(pcm_data)

async def run_pipeline():
    print(f"\n{Colors.BLUE}=== Starting End-to-End Voice Pipeline Test ==={Colors.RESET}")
    
    if not TEST_AUDIO_DIR.exists():
        print(f"{Colors.RED}❌ No test audio found at {TEST_AUDIO_DIR}.{Colors.RESET}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_key:
        print(f"{Colors.RED}❌ Missing DEEPGRAM_API_KEY env var.{Colors.RESET}")
        return

    print(f"{Colors.BLUE}Initializing NeuTTS Engine (this loads the model)...{Colors.RESET}")
    try:
        # Use config matching credentials.yml
        tts_config = NeuTTSConfig(
            backbone_repo="neuphonic/neutts-air-q8-gguf",
            codec_repo="neuphonic/neucodec",
            device="cpu",
            auto_generate_reference=True
        )
        tts_service = NeuTTSService(tts_config)
    except Exception:
        print(f"{Colors.RED}❌ Failed to initialize NeuTTS:{Colors.RESET}")
        traceback.print_exc()
        return

    test_files = ["check_balance.wav", "transfer_money.wav", "lost_card.wav"]
    print(f"\n{Colors.BLUE}Pipeline Ready. Processing files...{Colors.RESET}\n")

    # Use a unique sender_id for the entire run to maintain context if needed,
    # OR create a new one per file if you want fresh state.
    # Here we use a fresh ID per file to test flows in isolation.
    
    for filename in test_files:
        file_path = TEST_AUDIO_DIR / filename
        if not file_path.exists(): continue

        # Generate a random ID for this specific test case so Rasa state is clean
        sender_id = f"tester-{uuid.uuid4().hex[:8]}"

        print(f"{Colors.YELLOW}▶ Processing: {filename}{Colors.RESET}")
        try:
            # 1. Transcribe
            print(f"  🎤 Transcribing...", end=" ", flush=True)
            transcript = await deepgram_transcribe(file_path, deepgram_key)
            print(f"{Colors.GREEN}Done{Colors.RESET} ('{transcript}')")

            if not transcript: continue

            # 2. Rasa Process (Using the random sender_id)
            print(f"  🧠 Rasa processing...", end=" ", flush=True)
            responses = await rasa_process(transcript, sender_id)
            print(f"{Colors.GREEN}Done{Colors.RESET}")
            
            for i, response_text in enumerate(responses):
                print(f"     🤖 Bot: \"{response_text}\"")
                out_filename = f"{file_path.stem}_response_{i+1}.wav"
                out_path = OUTPUT_DIR / out_filename
                
                # 3. TTS Synthesis
                print(f"  🔊 Synthesizing...", end=" ", flush=True)
                await neutts_synthesize(response_text, tts_service, out_path)
                print(f"{Colors.GREEN}Saved to {out_path}{Colors.RESET}")

        except Exception as e:
            print(f"\n{Colors.RED}❌ Pipeline failed: {e}{Colors.RESET}")
            traceback.print_exc()
        print("-" * 50)

    print(f"\n{Colors.GREEN}Test Complete.{Colors.RESET}")
    print(f"Output files: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt: pass