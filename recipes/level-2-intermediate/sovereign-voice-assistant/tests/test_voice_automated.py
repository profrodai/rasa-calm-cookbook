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
import websockets # Required for Local ASR
from typing import Optional, List, Dict

# Import your actual TTS service
try:
    from services.neutts_service import NeuTTSService, NeuTTSConfig
except ImportError as e:
    print(f"\n❌ CRITICAL ERROR: Could not import NeuTTSService.")
    print(f"   Ensure 'services/neutts_service.py' exists.")
    traceback.print_exc()
    sys.exit(1)

# Configuration
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"
LOCAL_ASR_URL = "ws://localhost:9001" # Pointing to your local server
TEST_AUDIO_DIR = Path("tests/audio")
OUTPUT_DIR = Path("tests/audio_responses_real")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

# ==============================================================================
# Audio Utilities
# ==============================================================================

class ConversationRecorder:
    def __init__(self):
        self.audio_buffer = bytearray()
        self.silence_chunk = b'\x00' * 8000 # 0.5s silence

    def add_turn(self, user_audio_path: Path, bot_audio_data: bytes):
        # Add User Audio (PCM)
        try:
            with wave.open(str(user_audio_path), 'rb') as w:
                n_channels = w.getnchannels()
                width = w.getsampwidth()
                rate = w.getframerate()
                frames = w.readframes(w.getnframes())

            if n_channels == 2:
                frames = audioop.tomono(frames, width, 0.5, 0.5)
                n_channels = 1
            if rate != 8000:
                frames, _ = audioop.ratecv(frames, width, n_channels, rate, 8000, None)

            self.audio_buffer.extend(frames)
        except Exception as e:
            print(f"   ⚠️ Could not stitch input: {e}")

        # Add Silence
        self.audio_buffer.extend(self.silence_chunk)

        # Add Bot Audio
        if bot_audio_data:
            self.audio_buffer.extend(bot_audio_data)
            self.audio_buffer.extend(self.silence_chunk)

    def save(self, output_path: Path):
        try:
            with wave.open(str(output_path), 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(8000)
                wav_file.setcomptype('NONE', 'not compressed')
                wav_file.writeframes(self.audio_buffer)
            return True
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False

# ==============================================================================
# Pipeline Stages
# ==============================================================================

async def local_asr_transcribe(audio_path: Path) -> str:
    """
    Connects to Local ASR (Whisper), simulates Rasa's audio stream (8k mulaw), 
    and returns text.
    """
    try:
        async with websockets.connect(LOCAL_ASR_URL) as ws:
            # 1. Read WAV and Convert to 8kHz Mulaw (Format expected by Server)
            with wave.open(str(audio_path), 'rb') as w:
                frames = w.readframes(w.getnframes())
                width = w.getsampwidth()
                rate = w.getframerate()
                
                # Convert to Mono
                if w.getnchannels() == 2:
                    frames = audioop.tomono(frames, width, 0.5, 0.5)
                
                # Resample to 8kHz (Server expects telephony standard)
                if rate != 8000:
                    frames, _ = audioop.ratecv(frames, width, 1, rate, 8000, None)
                
                # Encode to u-law (Server expects encoded bytes)
                mulaw_bytes = audioop.lin2ulaw(frames, width)

            # 2. Send Audio Bytes
            await ws.send(mulaw_bytes)

            # 3. Trigger Transcription
            await ws.send(json.dumps({"action": "transcribe"}))

            # 4. Wait for Response
            response = await ws.recv()
            data = json.loads(response)
            return data.get("text", "").strip()

    except Exception as e:
        print(f"{Colors.RED}Local ASR Connection Failed: {e}{Colors.RESET}")
        print(f"Make sure 'make run-local-asr' is running in another terminal.")
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
    ulaw_data = bytearray()
    async for chunk in tts_service.synthesize(text):
        ulaw_data.extend(chunk)
    if not ulaw_data: return b""
    return audioop.ulaw2lin(ulaw_data, 2)

async def run_pipeline():
    print(f"\n{Colors.BLUE}=== Starting End-to-End Sovereign Pipeline Test ==={Colors.RESET}")
    print(f"{Colors.YELLOW}Config: Local ASR (Whisper) -> Rasa -> Local TTS (NeuTTS){Colors.RESET}\n")
    
    if not TEST_AUDIO_DIR.exists():
        print(f"{Colors.RED}❌ No test audio found at {TEST_AUDIO_DIR}.{Colors.RESET}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize TTS
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

    test_conversations = {
        "full_balance_check": ["check_balance.wav", "checking.wav"],
        "full_transfer": ["transfer_money.wav", "checking.wav", "savings.wav", "five_hundred.wav", "yes.wav"],
        "full_lost_card": ["lost_card.wav", "card_digits.wav"]
    }

    print(f"\n{Colors.BLUE}Pipeline Ready. Running Conversations...{Colors.RESET}\n")

    for case_name, file_sequence in test_conversations.items():
        print(f"{Colors.BLUE}🔵 Case: {case_name}{Colors.RESET}")
        sender_id = f"tester-{uuid.uuid4().hex[:8]}"
        recorder = ConversationRecorder()
        
        for filename in file_sequence:
            file_path = TEST_AUDIO_DIR / filename
            if not file_path.exists(): continue

            print(f"   ▶ Step: {filename}")
            try:
                # 1. Local ASR
                print(f"     🎤 Transcribing (Local Whisper)...", end=" ", flush=True)
                transcript = await local_asr_transcribe(file_path)
                print(f"{Colors.GREEN}Done{Colors.RESET} ('{transcript}')")
                
                if not transcript: 
                    print("     ⚠️ No transcript, skipping.")
                    continue

                # 2. Rasa
                responses = await rasa_process(transcript, sender_id)
                
                # 3. Local TTS
                bot_turn_audio = bytearray()
                if responses:
                    for response_text in responses:
                        print(f"     🤖 Bot:  \"{response_text}\"")
                        pcm_audio = await neutts_synthesize_to_pcm(response_text, tts_service)
                        bot_turn_audio.extend(pcm_audio)
                else:
                    print(f"     🤖 Bot:  (No text response)")
                
                recorder.add_turn(file_path, bot_turn_audio)

            except Exception as e:
                print(f"     ❌ Error: {e}")
                traceback.print_exc()

        output_path = OUTPUT_DIR / f"{case_name}.wav"
        if recorder.save(output_path):
            print(f"   ✅ Saved: {Colors.GREEN}{output_path}{Colors.RESET}")
        print("-" * 50)

    print(f"\n{Colors.GREEN}Test Complete.{Colors.RESET}")
    print(f"Output files: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt: pass