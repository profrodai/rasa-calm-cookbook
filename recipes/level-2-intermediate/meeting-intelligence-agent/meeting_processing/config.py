# recipes/level-2-intermediate/meeting-intelligence-agent/meeting_processing/config.py
"""
Central configuration for meeting processing module.

This file contains all paths, settings, and constants used throughout
the meeting processing pipeline.
"""

import os
from pathlib import Path

# ==============================================================================
# Directory Structure
# ==============================================================================

# Base directory (this recipe's root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Input/Output directories
RECORDINGS_DIR = BASE_DIR / "recordings"
MEETINGS_DIR = BASE_DIR / "meetings"
PROCESSED_DIR = MEETINGS_DIR / "processed"
SPEAKER_MAP_DIR = MEETINGS_DIR / "speaker_maps"
REFERENCE_VOICES_DIR = BASE_DIR / "reference_voices"

# Ensure directories exist
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
SPEAKER_MAP_DIR.mkdir(parents=True, exist_ok=True)
REFERENCE_VOICES_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# Default Meeting ID
# ==============================================================================
DEFAULT_MEETING_ID = "sample_earnings_call"

# ==============================================================================
# pyannote Speaker Diarization Settings
# ==============================================================================
PYANNOTE_MODEL = os.getenv(
    "PYANNOTE_MODEL", "pyannote/speaker-diarization-community-1"
)
PYANNOTE_DEVICE = os.getenv("PYANNOTE_DEVICE", "cpu")  # cpu, mps, cuda
PYANNOTE_MIN_SPEAKERS = int(os.getenv("PYANNOTE_MIN_SPEAKERS", "2"))
PYANNOTE_MAX_SPEAKERS = int(os.getenv("PYANNOTE_MAX_SPEAKERS", "10"))

# ==============================================================================
# Whisper ASR Settings
# ==============================================================================
# Model sizes: tiny, base, small, medium, large-v2, large-v3
# For M4 Mac: medium.en provides best quality/speed balance
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium.en")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")  # cpu, mps, cuda
WHISPER_COMPUTE_TYPE = os.getenv(
    "WHISPER_COMPUTE_TYPE", "int8"
)  # int8, float16, float32

# For M4 Mac GPU acceleration:
# - Set WHISPER_DEVICE=mps
# - Set WHISPER_COMPUTE_TYPE=float16

# Language settings
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")
WHISPER_TASK = os.getenv("WHISPER_TASK", "transcribe")  # transcribe or translate

# Quality settings
WHISPER_BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "5"))
WHISPER_VAD_FILTER = os.getenv("WHISPER_VAD_FILTER", "true").lower() == "true"

# ==============================================================================
# ChromaDB Vector Database Settings
# ==============================================================================
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(PROCESSED_DIR))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

# Collection naming
CHROMA_COLLECTION_PREFIX = "meeting_"

# ==============================================================================
# Retrieval Settings
# ==============================================================================
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "10"))
RETRIEVAL_SIMILARITY_THRESHOLD = float(
    os.getenv("RETRIEVAL_SIMILARITY_THRESHOLD", "0.5")
)

# Text chunking for embeddings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))  # tokens
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))  # tokens

# ==============================================================================
# Audio Processing Settings
# ==============================================================================
# Target sample rate for processing
TARGET_SAMPLE_RATE = 16000  # 16kHz (standard for speech)

# Silence detection thresholds (for removing non-speech)
SILENCE_THRESHOLD_DB = float(os.getenv("SILENCE_THRESHOLD_DB", "-40"))
MIN_SILENCE_DURATION_MS = int(os.getenv("MIN_SILENCE_DURATION_MS", "500"))

# Speaker segment merging
# Merge consecutive segments from same speaker if gap < threshold
MERGE_SAME_SPEAKER_GAP_MS = int(os.getenv("MERGE_SAME_SPEAKER_GAP_MS", "1000"))

# ==============================================================================
# File Naming Conventions
# ==============================================================================


def get_diarization_path(meeting_id: str) -> Path:
    """Get path to diarization JSON file."""
    return PROCESSED_DIR / f"{meeting_id}_diarization.json"


def get_transcript_path(meeting_id: str) -> Path:
    """Get path to transcript JSON file."""
    return PROCESSED_DIR / f"{meeting_id}_transcript.json"


def get_speaker_map_path(meeting_id: str) -> Path:
    """Get path to speaker map JSON file."""
    return SPEAKER_MAP_DIR / f"{meeting_id}_speaker_map.json"


def get_chroma_collection_name(meeting_id: str) -> str:
    """Get ChromaDB collection name for a meeting."""
    return f"{CHROMA_COLLECTION_PREFIX}{meeting_id}"


def get_chroma_persist_dir(meeting_id: str) -> Path:
    """Get ChromaDB persistence directory for a meeting."""
    return PROCESSED_DIR / f"{meeting_id}_embeddings"


# ==============================================================================
# Logging Configuration
# ==============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ==============================================================================
# Model Download Settings
# ==============================================================================
# Hugging Face token for downloading pyannote models
HF_TOKEN = os.getenv("HF_TOKEN", None)

if not HF_TOKEN:
    import warnings

    warnings.warn(
        "HF_TOKEN not set. You may not be able to download pyannote models. "
        "Get a token at: https://huggingface.co/settings/tokens"
    )

# ==============================================================================
# Helper Functions
# ==============================================================================


def validate_meeting_id(meeting_id: str) -> bool:
    """
    Validate meeting ID format.

    Args:
        meeting_id: Meeting identifier

    Returns:
        True if valid, False otherwise
    """
    if not meeting_id:
        return False

    # Must be alphanumeric with underscores/hyphens only
    import re

    return bool(re.match(r"^[a-zA-Z0-9_-]+$", meeting_id))


def get_audio_path(meeting_id: str) -> Path:
    """
    Get path to source audio file.

    Looks for .wav, .mp3, .m4a, .flac in recordings directory.

    Args:
        meeting_id: Meeting identifier

    Returns:
        Path to audio file

    Raises:
        FileNotFoundError: If no audio file found
    """
    extensions = [".wav", ".mp3", ".m4a", ".flac", ".ogg"]

    for ext in extensions:
        path = RECORDINGS_DIR / f"{meeting_id}{ext}"
        if path.exists():
            return path

    raise FileNotFoundError(
        f"No audio file found for meeting_id '{meeting_id}' in {RECORDINGS_DIR}. "
        f"Looked for extensions: {extensions}"
    )


def meeting_is_processed(meeting_id: str) -> bool:
    """
    Check if a meeting has been processed.

    Args:
        meeting_id: Meeting identifier

    Returns:
        True if transcript exists, False otherwise
    """
    return get_transcript_path(meeting_id).exists()


# ==============================================================================
# Export commonly used paths
# ==============================================================================
__all__ = [
    "BASE_DIR",
    "RECORDINGS_DIR",
    "MEETINGS_DIR",
    "PROCESSED_DIR",
    "SPEAKER_MAP_DIR",
    "REFERENCE_VOICES_DIR",
    "DEFAULT_MEETING_ID",
    "PYANNOTE_MODEL",
    "PYANNOTE_DEVICE",
    "WHISPER_MODEL",
    "WHISPER_DEVICE",
    "WHISPER_COMPUTE_TYPE",
    "EMBEDDING_MODEL",
    "RETRIEVAL_TOP_K",
    "get_diarization_path",
    "get_transcript_path",
    "get_speaker_map_path",
    "get_chroma_collection_name",
    "get_chroma_persist_dir",
    "validate_meeting_id",
    "get_audio_path",
    "meeting_is_processed",
]