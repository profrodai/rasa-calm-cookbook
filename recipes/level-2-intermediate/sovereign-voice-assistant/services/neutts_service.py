# recipes/level-2-intermediate/sovereign-voice-assistant/services/neutts_service.py
import os
import io
import platform
import glob
import logging
import audioop
import numpy as np
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, AsyncIterator, Dict, Any

# Rasa specific imports
from rasa.core.channels.voice_stream.audio_bytes import RasaAudioBytes
from rasa.core.channels.voice_stream.tts.tts_engine import (
    TTSEngine,
    TTSEngineConfig,
    TTSError,
)

# Configure logging
logger = logging.getLogger(__name__)

# ==============================================================================
# 1. macOS Espeak Fix (Must run before other imports)
# ==============================================================================
if platform.system() == "Darwin":
    possible_paths = [
        "/opt/homebrew/Cellar/espeak/*/lib/libespeak.*.dylib",
        "/usr/local/Cellar/espeak/*/lib/libespeak.*.dylib",
    ]
    for pattern in possible_paths:
        matches = glob.glob(pattern)
        if matches:
            try:
                # We access the wrapper via importlib to avoid crashing if phonemizer isn't installed yet
                if importlib.util.find_spec("phonemizer"):
                    from phonemizer.backend.espeak.wrapper import EspeakWrapper
                    EspeakWrapper.set_library(matches[0])
                    logger.info(f"Espeak configured at: {matches[0]}")
            except Exception:
                pass
            break

# ==============================================================================
# 2. Configuration Class
# ==============================================================================
@dataclass
class NeuTTSConfig(TTSEngineConfig):
    """Configuration variables matching credentials.yml"""
    backbone_repo: str = "neuphonic/neutts-air-q8-gguf"
    codec_repo: str = "neuphonic/neucodec"
    device: str = "cpu"
    auto_generate_reference: bool = True
    reference_audio: Optional[str] = None
    reference_text: Optional[str] = None

# ==============================================================================
# 3. Main Service Class
# ==============================================================================
class NeuTTSService(TTSEngine[NeuTTSConfig]):
    """
    Rasa-compliant wrapper for NeuTTS Air.
    Converts 24kHz Float32 audio -> 8kHz Mulaw for Rasa Browser Channel.
    """
    
    def __init__(self, config: NeuTTSConfig):
        super().__init__(config)
        self.tts = None
        self.ref_codes = None
        self.ref_text = None
        self._librosa = None
        
        # Lazy load model to avoid overhead if not used immediately
        # or if dependencies are missing during initial Rasa graph validation
        self._initialized = False

    @staticmethod
    def get_default_config() -> NeuTTSConfig:
        return NeuTTSConfig()

    def _initialize_model(self):
        """Loads the model and dependencies on first use."""
        if self._initialized:
            return

        try:
            from neuttsair.neutts import NeuTTSAir
            import librosa
            self._librosa = librosa
        except ImportError as e:
            raise TTSError(f"Missing dependencies for NeuTTS: {e}. Run 'make install-neutts'")

        logger.info(f"Loading NeuTTS backbone: {self.config.backbone_repo}")
        
        self.tts = NeuTTSAir(
            backbone_repo=self.config.backbone_repo,
            backbone_device=self.config.device,
            codec_repo=self.config.codec_repo,
            codec_device=self.config.device,
        )

        # Handle Reference Audio
        self._setup_reference_voice()
        self._initialized = True

    def _setup_reference_voice(self):
        """Sets up the reference voice (cloning source)."""
        ref_audio = self.config.reference_audio
        ref_text = self.config.reference_text or "Hello, I am your banking assistant."

        # If no reference provided, auto-generate one
        if not ref_audio and self.config.auto_generate_reference:
            ref_audio = self._generate_gtts_reference(ref_text)

        if ref_audio:
            logger.info(f"Encoding reference audio: {ref_audio}")
            self.ref_codes = self.tts.encode_reference(ref_audio)
            self.ref_text = ref_text
        else:
            raise TTSError("No reference audio provided and auto-generation failed.")

    def _generate_gtts_reference(self, text: str) -> str:
        """Generates a temporary reference file using GTTS."""
        try:
            from gtts import gTTS
            from pydub import AudioSegment
            
            cache_dir = Path(".neutts_cache")
            cache_dir.mkdir(exist_ok=True)
            wav_path = cache_dir / "default_reference.wav"
            
            if not wav_path.exists():
                logger.info("Generating default reference voice...")
                mp3_path = cache_dir / "temp.mp3"
                tts = gTTS(text=text, lang='en')
                tts.save(str(mp3_path))
                
                # Convert to mono 16kHz WAV
                audio = AudioSegment.from_mp3(str(mp3_path))
                audio = audio.set_channels(1).set_frame_rate(16000)
                audio.export(str(wav_path), format="wav")
                mp3_path.unlink()
                
            return str(wav_path)
        except Exception as e:
            logger.error(f"Failed to generate reference: {e}")
            raise TTSError("Install gtts and pydub to use auto_generate_reference")

    # ==========================================================================
    # 4. Required Rasa Implementation
    # ==========================================================================
    
    @classmethod
    def from_config_dict(cls, config: Dict[str, Any]) -> "NeuTTSService":
        """Load configuration from credentials.yml"""
        return cls(NeuTTSConfig.from_dict(config))

    def engine_bytes_to_rasa_audio_bytes(self, chunk: bytes) -> RasaAudioBytes:
        """Required by Rasa: Wraps raw bytes into RasaAudioBytes."""
        return RasaAudioBytes(chunk)

    async def synthesize(self, text: str, config: Optional[NeuTTSConfig] = None) -> AsyncIterator[RasaAudioBytes]:
        """
        1. Generate 24kHz audio from NeuTTS
        2. Resample to 8kHz
        3. Convert to Mu-law
        4. Yield to Rasa
        """
        if not self._initialized:
            self._initialize_model()

        # Sanity check for empty text
        if not text or not text.strip():
            return

        logger.debug(f"Synthesizing: {text[:30]}...")

        # 1. Inference
        # NeuTTS returns a numpy array (float32) at 24000Hz
        try:
            # We use the blocking infer call because streaming infer in NeuTTS 
            # might not support the chunk-based resampling cleanly yet.
            wav_24k = self.tts.infer(text, self.ref_codes, self.ref_text)
        except Exception as e:
            logger.error(f"NeuTTS Inference failed: {e}")
            return

        if len(wav_24k) == 0:
            return

        # 2. Resample 24kHz -> 8kHz (Required by Rasa)
        # Using librosa for high quality resampling
        # orig_sr=24000 is the NeuTTS default
        wav_8k = self._librosa.resample(wav_24k, orig_sr=24000, target_sr=8000)

        # 3. Convert Float32 [-1, 1] -> Int16 PCM [ -32768, 32767 ]
        # Clip to prevent overflow artifacts
        wav_8k = np.clip(wav_8k, -1.0, 1.0)
        pcm_data = (wav_8k * 32767).astype(np.int16).tobytes()

        # 4. Convert Int16 PCM -> Mulaw (Required by Rasa)
        # 2 bytes width = 16 bit
        try:
            mulaw_data = audioop.lin2ulaw(pcm_data, 2)
            
            # 5. Yield result
            yield self.engine_bytes_to_rasa_audio_bytes(mulaw_data)
            
        except Exception as e:
            logger.error(f"Audio encoding failed: {e}")