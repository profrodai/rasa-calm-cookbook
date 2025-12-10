# recipes/level-2-intermediate/sovereign-voice-assistant/services/neutts_service.py
"""
NeuTTS Air TTS Service for Rasa - Auto-Reference Version
Drop-in replacement for Rime with automatic reference generation
Compatible with existing test infrastructure (gtts-based)
"""

# CRITICAL: Configure espeak library BEFORE any phonemizer imports
# This must happen at module import time, not class init time
import platform
import glob

if platform.system() == "Darwin":  # macOS
    # Common Homebrew paths for espeak
    possible_paths = [
        "/opt/homebrew/Cellar/espeak/*/lib/libespeak.*.dylib",
        "/usr/local/Cellar/espeak/*/lib/libespeak.*.dylib",
    ]
    for pattern in possible_paths:
        matches = glob.glob(pattern)
        if matches:
            espeak_lib = matches[0]
            try:
                from phonemizer.backend.espeak.wrapper import EspeakWrapper
                EspeakWrapper.set_library(espeak_lib)
                print(f"✓ espeak library configured: {espeak_lib}")
            except Exception as e:
                print(f"Warning: Could not set espeak library: {e}")
            break

# Now safe to import other modules
import os
import io
from pathlib import Path
from typing import Optional
import soundfile as sf
import torch


class NeuTTSService:
    """Local TTS using Neuphonic NeuTTS Air with auto-generated references"""
    
    # Default reference voice - uses auto-generated gtts sample
    DEFAULT_REF_TEXT = "Hello, I'm your banking assistant. I can help you today."
    
    def __init__(
        self,
        backbone_repo: str = "neuphonic/neutts-air-q8-gguf",
        codec_repo: str = "neuphonic/neucodec",
        device: str = "cpu",
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        auto_generate_reference: bool = True,
    ):
        """
        Initialize NeuTTS service with automatic reference generation.
        
        Args:
            backbone_repo: HuggingFace repo for model (q8-gguf recommended)
            codec_repo: HuggingFace repo for codec (onnx recommended)
            device: Device to run on (cpu/gpu)
            reference_audio: Path to reference voice (optional - will auto-generate)
            reference_text: Text for reference (optional - will use default)
            auto_generate_reference: If True, generates reference from gtts if missing
        """
        try:
            from neuttsair.neutts import NeuTTSAir
        except ImportError as e:
            raise ImportError(
                "NeuTTS Air not installed. Install with:\n"
                "  make install-neutts"
            ) from e
        
        print(f"Loading NeuTTS from {backbone_repo} on {device}...")
        
        self.tts = NeuTTSAir(
            backbone_repo=backbone_repo,
            backbone_device=device,
            codec_repo=codec_repo,
            codec_device=device,
        )
        
        self.sample_rate = 24000
        self.ref_codes = None
        self.ref_text = None
        
        # Auto-generate reference if none provided
        if reference_audio is None and auto_generate_reference:
            print("No reference audio provided - generating default...")
            reference_audio = self._generate_default_reference()
            reference_text = self.DEFAULT_REF_TEXT
        
        # Load reference voice
        if reference_audio and reference_text:
            self.load_reference(reference_audio, reference_text)
    
    def _generate_default_reference(self) -> str:
        """
        Generate default reference voice using gtts (same as test infrastructure).
        
        Returns:
            Path to generated reference audio file
        """
        try:
            from gtts import gTTS
        except ImportError:
            raise ImportError(
                "gtts required for auto-reference generation.\n"
                "Install with: make install-voice-deps"
            )
        
        # Create cache directory
        cache_dir = Path(".neutts_cache")
        cache_dir.mkdir(exist_ok=True)
        
        ref_path = cache_dir / "default_reference.wav"
        
        # Generate if doesn't exist
        if not ref_path.exists():
            print(f"  Generating reference with gtts...")
            tts_gen = gTTS(text=self.DEFAULT_REF_TEXT, lang='en', slow=False)
            
            # Save as mp3 first (gtts limitation)
            mp3_path = cache_dir / "default_reference.mp3"
            tts_gen.save(str(mp3_path))
            
            # Convert to WAV using pydub
            try:
                from pydub import AudioSegment
                
                audio = AudioSegment.from_mp3(str(mp3_path))
                # Convert to mono, 16kHz (optimal for NeuTTS)
                audio = audio.set_channels(1).set_frame_rate(16000)
                audio.export(str(ref_path), format="wav")
                
                # Cleanup mp3
                mp3_path.unlink()
                
                print(f"  ✓ Generated reference: {ref_path}")
                
            except ImportError:
                raise ImportError(
                    "pydub required for audio conversion.\n"
                    "Install with: make install-voice-deps"
                )
        else:
            print(f"  ✓ Using cached reference: {ref_path}")
        
        return str(ref_path)
    
    def load_reference(self, audio_path: str, text: str):
        """
        Load reference voice for cloning.
        
        Args:
            audio_path: Path to reference audio file
            text: Reference text (or path to text file)
        """
        # Handle text file or string
        if os.path.exists(text) and os.path.isfile(text):
            with open(text, 'r') as f:
                text = f.read().strip()
        
        print(f"Encoding reference audio: {audio_path}")
        self.ref_codes = self.tts.encode_reference(audio_path)
        self.ref_text = text
        print("✓ Reference voice loaded successfully")
    
    def synthesize(self, text: str, output_path: Optional[str] = None) -> bytes:
        """
        Convert text to speech.
        
        Args:
            text: Text to synthesize
            output_path: Optional path to save audio file
            
        Returns:
            Audio data as bytes (WAV format)
            
        Raises:
            ValueError: If no reference voice loaded
        """
        if self.ref_codes is None:
            raise ValueError(
                "No reference voice loaded. This should not happen with "
                "auto_generate_reference=True."
            )
        
        # Truncate for logging
        display_text = text[:50] + "..." if len(text) > 50 else text
        print(f"Synthesizing: {display_text}")
        
        wav = self.tts.infer(text, self.ref_codes, self.ref_text)
        
        # Optionally save to file
        if output_path:
            sf.write(output_path, wav, self.sample_rate)
            print(f"✓ Saved to {output_path}")
        
        # Convert to bytes for Rasa
        buffer = io.BytesIO()
        sf.write(buffer, wav, self.sample_rate, format='WAV')
        buffer.seek(0)
        return buffer.getvalue()
    
    def synthesize_stream(self, text: str):
        """
        Stream audio synthesis (GGUF models only).
        
        Args:
            text: Text to synthesize
            
        Yields:
            Audio chunks as numpy arrays
            
        Raises:
            NotImplementedError: If model doesn't support streaming
        """
        try:
            for chunk in self.tts.infer_stream(text, self.ref_codes, self.ref_text):
                yield chunk
        except (AttributeError, NotImplementedError):
            raise NotImplementedError(
                "Streaming requires GGUF model. Use:\n"
                "  backbone_repo: neuphonic/neutts-air-q8-gguf"
            )


# For backward compatibility with test scripts
def quick_test(
    text: str = "Hello, this is a test of the local text to speech system.",
    output_path: str = "test_output.wav"
):
    """Quick test with auto-generated reference."""
    tts = NeuTTSService(
        backbone_repo="neuphonic/neutts-air-q8-gguf",
        codec_repo="neuphonic/neucodec",
        device="cpu",
        auto_generate_reference=True
    )
    
    audio = tts.synthesize(text, output_path=output_path)
    print(f"✓ Generated {len(audio)} bytes of audio")
    return audio


if __name__ == "__main__":
    quick_test()