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
import audioop
import uuid
from typing import Optional, List, Dict

# Import your actual TTS service
try:
    from services.neutts_service import NeuTTSService, NeuTTSConfig
except ImportError as e:
    print(f"\n❌ CRITICAL ERROR: Could not import NeuTTSService.")
    print(f"   Ensure 'services/neutts_service.py' exists and has no syntax errors.")
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

# ==============================================================================
# Audio Utilities for Stitching
# ==============================================================================

class ConversationRecorder:
    """Helper to stitch user and bot audio into a single file."""
    def __init__(self):
        self.audio_buffer = bytearray()
        # 0.5 seconds of silence (8kHz, 16-bit mono = 16000 bytes/sec)
        self.silence_chunk = b'\x00' * 8000 

    def add_turn(self, user_audio_path: Path, bot_audio_data: bytes):
        """Adds one turn (User Input -> Silence -> Bot Response -> Silence) to the buffer."""
        
        # 1. Process User Audio (Resample input WAV to match 8kHz output)
        try:
            with wave.open(str(user_audio_path), 'rb') as w:
                n_channels = w.getnchannels()
                width = w.getsampwidth()
                rate = w.getframerate()
                frames = w.readframes(w.getnframes())

            # Convert to Mono first if needed
            if n_channels == 2:
                frames = audioop.tomono(frames, width, 0.5, 0.5)
                n_channels = 1
            
            # Resample to 8000Hz if needed (e.g. input is 16kHz)
            if rate != 8000:
                frames, _ = audioop.ratecv(frames, width, n_channels, rate, 8000, None)

            self.audio_buffer.extend(frames)
            
        except Exception as e:
            print(f"   ⚠️ Could not stitch input audio '{user_audio_path.name}': {e}")

        # 2. Add Silence
        self.audio_buffer.extend(self.silence_chunk)

        # 3. Add Bot Audio (Already 8kHz PCM from neutts_synthesize_to_pcm)
        if bot_audio_data:
            self.audio_buffer.extend(bot_audio_data)
            # 4. Add Silence after bot
            self.audio_buffer.extend(self.silence_chunk)

    def save(self, output_path: Path):
        """Saves the accumulated buffer to a WAV file."""
        try:
            with wave.open(str(output_path), 'wb') as wav_file:
                wav_file.setnchannels(1)      # Mono
                wav_file.setsampwidth(2)      # 16-bit
                wav_file.setframerate(8000)   # 8kHz
                wav_file.setcomptype('NONE', 'not compressed')
                wav_file.writeframes(self.audio_buffer)
            return True
        except Exception as e:
            print(f"❌ Error saving conversation file: {e}")
            return False

# ==============================================================================
# Pipeline Stages
# ==============================================================================

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

async def neutts_synthesize_to_pcm(text: str, tts_service: NeuTTSService) -> bytes:
    """Generates audio bytes (Linear PCM 8kHz) but does NOT save to file."""
    ulaw_data = bytearray()
    async for chunk in tts_service.synthesize(text):
        ulaw_data.extend(chunk)
    
    if not ulaw_data:
        return b""

    # Convert u-law (Rasa format) back to Linear PCM (Standard WAV format)
    return audioop.ulaw2lin(ulaw_data, 2)

async def run_pipeline():
    print(f"\n{Colors.BLUE}=== Starting End-to-End Voice Pipeline & Recording ==={Colors.RESET}")
    
    if not TEST_AUDIO_DIR.exists():
        print(f"{Colors.RED}❌ No test audio found at {TEST_AUDIO_DIR}.{Colors.RESET}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_key:
        print(f"{Colors.RED}❌ Missing DEEPGRAM_API_KEY env var.{Colors.RESET}")
        return

    print(f"{Colors.BLUE}Initializing NeuTTS Engine...{Colors.RESET}")
    try:
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

    # Define Test Cases (Sequence of audio files to simulate a conversation)
    test_conversations = {
        # Case 1: Simple Balance Check
        "full_balance_check": ["check_balance.wav", "checking.wav"],
        
        # Case 2: Complex Transfer
        "full_transfer": ["transfer_money.wav", "checking.wav", "savings.wav", "five_hundred.wav", "yes.wav"],
        
        # Case 3: Lost Card Report
        "full_lost_card": ["lost_card.wav", "card_digits.wav"]
    }

    print(f"\n{Colors.BLUE}Pipeline Ready. Running Conversations...{Colors.RESET}\n")

    for case_name, file_sequence in test_conversations.items():
        print(f"{Colors.BLUE}🔵 Case: {case_name}{Colors.RESET}")
        
        # New sender ID and Recorder for each conversation
        sender_id = f"tester-{uuid.uuid4().hex[:8]}"
        recorder = ConversationRecorder()
        
        for filename in file_sequence:
            file_path = TEST_AUDIO_DIR / filename
            if not file_path.exists():
                print(f"   ⚠️ Skipping {filename} (not found)")
                continue

            print(f"   ▶ Step: {filename}")
            try:
                # 1. Transcribe
                transcript = await deepgram_transcribe(file_path, deepgram_key)
                print(f"     🎤 User: \"{transcript}\"")
                
                # If Deepgram hears nothing, skip Rasa processing
                if not transcript:
                    print(f"     ⚠️ Empty transcript, skipping turn.")
                    continue

                # 2. Rasa
                responses = await rasa_process(transcript, sender_id)
                
                # 3. Synthesize & Stitch
                bot_turn_audio = bytearray()
                
                if responses:
                    for response_text in responses:
                        print(f"     🤖 Bot:  \"{response_text}\"")
                        pcm_audio = await neutts_synthesize_to_pcm(response_text, tts_service)
                        bot_turn_audio.extend(pcm_audio)
                else:
                    print(f"     🤖 Bot:  (No text response)")
                
                # Add this turn (User Input + All Bot Responses) to the recording
                recorder.add_turn(file_path, bot_turn_audio)

            except Exception as e:
                print(f"     ❌ Error: {e}")
                traceback.print_exc()

        # Save the full conversation
        output_path = OUTPUT_DIR / f"{case_name}.wav"
        if recorder.save(output_path):
            print(f"   ✅ Saved full conversation: {Colors.GREEN}{output_path}{Colors.RESET}")
        print("-" * 50)

    print(f"\n{Colors.GREEN}Test Complete.{Colors.RESET}")
    print(f"Output files: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt: pass