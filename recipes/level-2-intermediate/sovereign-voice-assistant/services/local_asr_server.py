import asyncio
import websockets
import json
import numpy as np
import logging
import audioop
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - ASR - %(levelname)s - %(message)s")
logger = logging.getLogger("LocalASR")

try:
    from faster_whisper import WhisperModel
except ImportError:
    logger.error("faster-whisper not found. Run 'make install-local-asr'")
    sys.exit(1)

# Configuration
MODEL_SIZE = "small.en"  # "tiny.en", "base.en", "small.en", "medium.en"
PORT = 9001
DEVICE = "cpu"
COMPUTE_TYPE = "int8" # Optimized for CPU

class ASRHandler:
    def __init__(self):
        logger.info(f"Loading Whisper Model ({MODEL_SIZE}) on {DEVICE}...")
        self.model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
        logger.info("✓ Model loaded")

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribes raw 16kHz Mono PCM audio bytes.
        """
        if not audio_bytes:
            return ""

        # Convert raw bytes to float32 numpy array
        # Input must be 16kHz mono 16-bit PCM
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        segments, _ = self.model.transcribe(audio_np, beam_size=5, language="en")
        text = " ".join([segment.text for segment in segments]).strip()
        return text

# Initialize engine globally
asr_engine = None

async def echo(websocket):
    """
    WebSocket handler.
    1. Receives audio chunks (bytes) from Rasa
    2. Buffers them
    3. On specific signal, runs transcription
    """
    logger.info("Client connected")
    audio_buffer = bytearray()
    
    try:
        async for message in websocket:
            # Control messages (JSON)
            if isinstance(message, str):
                msg_data = json.loads(message)
                
                # Signal from Rasa that user stopped talking
                if msg_data.get("action") == "transcribe":
                    if len(audio_buffer) > 0:
                        logger.info(f"Processing {len(audio_buffer)} bytes...")
                        text = asr_engine.transcribe(bytes(audio_buffer))
                        logger.info(f"Transcript: '{text}'")
                        
                        # Send back to Rasa
                        await websocket.send(json.dumps({
                            "text": text,
                            "is_final": True
                        }))
                        audio_buffer = bytearray()
                    else:
                        logger.info("Transcribe requested but buffer empty")
            
            # Audio Data (Bytes)
            elif isinstance(message, bytes):
                # Rasa sends 8kHz mulaw. Whisper needs 16kHz PCM.
                try:
                    # 1. Decode Mulaw -> Linear PCM (16-bit)
                    pcm_data = audioop.ulaw2lin(message, 2)
                    
                    # 2. Resample 8kHz -> 16kHz
                    # ratecv(fragment, width, nchannels, inrate, outrate, state)
                    pcm_16k, _ = audioop.ratecv(pcm_data, 2, 1, 8000, 16000, None)
                    
                    audio_buffer.extend(pcm_16k)
                except Exception as e:
                    logger.error(f"Audio processing error: {e}")

    except websockets.exceptions.ConnectionClosed:
        logger.info("Connection closed")

async def main():
    global asr_engine
    asr_engine = ASRHandler()
    
    logger.info(f"Starting Local ASR Server on ws://localhost:{PORT}")
    async with websockets.serve(echo, "localhost", PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())