"""
NeuTTS Air TTS Service for Rasa
Local text-to-speech using Neuphonic's NeuTTS Air
"""
import os
import io
from pathlib import Path
from typing import Optional
import soundfile as sf
import torch


class NeuTTSService:
    """Local TTS using Neuphonic NeuTTS Air"""
    
    def __init__(
        self,
        backbone_repo: str = "neuphonic/neutts-air-q8-gguf",
        codec_repo: str = "neuphonic/neucodec-onnx-decoder",
        device: str = "cpu",
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
    ):
        """
        Initialize NeuTTS service.
        
        Args:
            backbone_repo: HuggingFace repo for model (q8-gguf recommended)
            codec_repo: HuggingFace repo for codec (onnx recommended)
            device: Device to run on (cpu/gpu)
            reference_audio: Path to reference voice sample (5-10s, mono, 16-44kHz)
            reference_text: Text transcription of reference
        """
        try:
            from neuttsair.neutts import NeuTTSAir
        except ImportError as e:
            raise ImportError(
                "NeuTTS Air not installed. Install with:\n"
                "  pip install neutts-air\n"
                "Or:\n"
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
        
        # Load reference voice
        self.ref_codes = None
        self.ref_text = None
        
        if reference_audio and reference_text:
            self.load_reference(reference_audio, reference_text)
    
    def load_reference(self, audio_path: str, text: str):
        """
        Load reference voice for cloning.
        
        Args:
            audio_path: Path to reference audio file
            text: Reference text (or path to text file)
        """
        # Handle text file or string
        if os.path.exists(text):
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
                "No reference voice loaded. Call load_reference() first or "
                "provide reference_audio and reference_text in constructor."
            )
        
        print(f"Synthesizing: {text[:50]}...")
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
        # Check if using GGUF model (supports streaming)
        try:
            for chunk in self.tts.infer_stream(text, self.ref_codes, self.ref_text):
                yield chunk
        except (AttributeError, NotImplementedError):
            raise NotImplementedError(
                "Streaming requires GGUF model. Use:\n"
                "  backbone_repo: neuphonic/neutts-air-q8-gguf\n"
                "  or: neuphonic/neutts-air-q4-gguf"
            )


# Convenience function for quick testing
def quick_test(
    text: str = "Hello, this is a test of the local text to speech system.",
    output_path: str = "test_output.wav"
):
    """Quick test of NeuTTS service."""
    # You'll need to provide your own reference files
    tts = NeuTTSService(
        backbone_repo="neuphonic/neutts-air-q8-gguf",
        codec_repo="neuphonic/neucodec-onnx-decoder",
        device="cpu",
        reference_audio="references/assistant_voice.wav",
        reference_text="references/assistant_voice.txt"
    )
    
    audio = tts.synthesize(text, output_path=output_path)
    print(f"✓ Generated {len(audio)} bytes of audio")
    return audio


if __name__ == "__main__":
    # Test the service
    quick_test()