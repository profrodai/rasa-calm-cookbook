# recipes/level-2-intermediate/meeting-intelligence-agent/meeting_processing/diarization.py
"""
Speaker diarization using pyannote.audio.

Takes an audio file and identifies who spoke when, outputting segments like:
  [{"speaker": "SPEAKER_0", "start": 12.34, "end": 18.90}, ...]
"""

import json
import logging
from pathlib import Path
from typing import Dict, List

import torch
from pyannote.audio import Pipeline

from .config import (
    PYANNOTE_DEVICE,
    PYANNOTE_MAX_SPEAKERS,
    PYANNOTE_MIN_SPEAKERS,
    PYANNOTE_MODEL,
    get_audio_path,
    get_diarization_path,
)

# Setup logging
logger = logging.getLogger(__name__)


def load_diarization_pipeline() -> Pipeline:
    """
    Load pyannote speaker diarization pipeline.

    Returns:
        Loaded pipeline ready for inference

    Raises:
        RuntimeError: If HF_TOKEN not set or model not accessible
    """
    import os

    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise RuntimeError(
            "HF_TOKEN environment variable not set. "
            "Get a token at: https://huggingface.co/settings/tokens\n"
            "Then accept model terms at: "
            "https://huggingface.co/pyannote/speaker-diarization-community-1"
        )

    logger.info(f"Loading pyannote pipeline: {PYANNOTE_MODEL}")

    try:
        pipeline = Pipeline.from_pretrained(PYANNOTE_MODEL, use_auth_token=hf_token)
    except Exception as e:
        logger.error(f"Failed to load pyannote pipeline: {e}")
        raise RuntimeError(
            f"Could not load pyannote pipeline. Make sure you've:\n"
            f"1. Accepted model terms at: "
            f"https://huggingface.co/pyannote/speaker-diarization-community-1\n"
            f"2. Set HF_TOKEN in your .env file\n"
            f"Error: {e}"
        )

    # Send to device
    device = torch.device(PYANNOTE_DEVICE)
    pipeline.to(device)

    logger.info(f"Pipeline loaded on device: {PYANNOTE_DEVICE}")
    return pipeline


def run_diarization(
    meeting_id: str,
    min_speakers: int = PYANNOTE_MIN_SPEAKERS,
    max_speakers: int = PYANNOTE_MAX_SPEAKERS,
) -> List[Dict]:
    """
    Run speaker diarization on a meeting audio file.

    Args:
        meeting_id: Meeting identifier
        min_speakers: Minimum number of speakers to detect
        max_speakers: Maximum number of speakers to detect

    Returns:
        List of diarization segments:
        [
            {
                "speaker": "SPEAKER_0",
                "start": 12.345,  # seconds
                "end": 18.901,    # seconds
            },
            ...
        ]

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If diarization fails
    """
    logger.info(f"Starting diarization for meeting: {meeting_id}")

    # Get audio path
    audio_path = get_audio_path(meeting_id)
    logger.info(f"Audio file: {audio_path}")

    # Load pipeline
    pipeline = load_diarization_pipeline()

    # Run diarization
    logger.info(f"Running diarization (min={min_speakers}, max={max_speakers})...")
    logger.info("This may take several minutes depending on audio length...")

    try:
        diarization = pipeline(
            str(audio_path), min_speakers=min_speakers, max_speakers=max_speakers
        )
    except Exception as e:
        logger.error(f"Diarization failed: {e}")
        raise RuntimeError(f"Speaker diarization failed: {e}")

    # Convert to list of segments
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segment = {
            "speaker": speaker,
            "start": round(turn.start, 3),
            "end": round(turn.end, 3),
        }
        segments.append(segment)

    logger.info(f"Diarization complete: {len(segments)} segments found")

    # Log speaker distribution
    speaker_counts = {}
    for seg in segments:
        speaker = seg["speaker"]
        speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1

    logger.info("Speaker distribution:")
    for speaker, count in sorted(speaker_counts.items()):
        logger.info(f"  {speaker}: {count} segments")

    # Save to JSON
    output_path = get_diarization_path(meeting_id)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    logger.info(f"Diarization saved to: {output_path}")

    return segments


def merge_same_speaker_segments(
    segments: List[Dict], max_gap_seconds: float = 1.0
) -> List[Dict]:
    """
    Merge consecutive segments from the same speaker if gap is small.

    This reduces fragmentation from diarization while preserving turn-taking.

    Args:
        segments: List of diarization segments
        max_gap_seconds: Maximum gap to merge (seconds)

    Returns:
        Merged segments
    """
    if not segments:
        return []

    merged = []
    current = segments[0].copy()

    for next_seg in segments[1:]:
        # Same speaker and small gap?
        if (
            next_seg["speaker"] == current["speaker"]
            and (next_seg["start"] - current["end"]) <= max_gap_seconds
        ):
            # Merge by extending end time
            current["end"] = next_seg["end"]
        else:
            # Different speaker or large gap - save current and start new
            merged.append(current)
            current = next_seg.copy()

    # Don't forget the last segment
    merged.append(current)

    logger.info(f"Merged {len(segments)} segments into {len(merged)} segments")

    return merged


def get_speaker_statistics(segments: List[Dict]) -> Dict:
    """
    Calculate statistics about speakers in the meeting.

    Args:
        segments: List of diarization segments

    Returns:
        Dictionary with statistics:
        {
            "total_speakers": 4,
            "total_duration": 3600.0,
            "speakers": {
                "SPEAKER_0": {
                    "segments": 120,
                    "total_time": 900.5,
                    "percentage": 25.01
                },
                ...
            }
        }
    """
    if not segments:
        return {
            "total_speakers": 0,
            "total_duration": 0.0,
            "speakers": {},
        }

    # Calculate total duration
    total_duration = max(seg["end"] for seg in segments)

    # Calculate per-speaker stats
    speaker_stats = {}
    for seg in segments:
        speaker = seg["speaker"]
        duration = seg["end"] - seg["start"]

        if speaker not in speaker_stats:
            speaker_stats[speaker] = {
                "segments": 0,
                "total_time": 0.0,
            }

        speaker_stats[speaker]["segments"] += 1
        speaker_stats[speaker]["total_time"] += duration

    # Add percentages
    for speaker, stats in speaker_stats.items():
        stats["percentage"] = round(
            (stats["total_time"] / total_duration * 100) if total_duration > 0 else 0,
            2,
        )
        stats["total_time"] = round(stats["total_time"], 2)

    return {
        "total_speakers": len(speaker_stats),
        "total_duration": round(total_duration, 2),
        "speakers": speaker_stats,
    }


# ==============================================================================
# CLI Interface for standalone testing
# ==============================================================================

if __name__ == "__main__":
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) < 2:
        print("Usage: python -m meeting_processing.diarization <meeting_id>")
        print("Example: python -m meeting_processing.diarization sample_earnings_call")
        sys.exit(1)

    meeting_id = sys.argv[1]

    try:
        segments = run_diarization(meeting_id)

        # Print statistics
        stats = get_speaker_statistics(segments)
        print("\n" + "=" * 60)
        print("DIARIZATION STATISTICS")
        print("=" * 60)
        print(f"Total speakers: {stats['total_speakers']}")
        print(f"Total duration: {stats['total_duration']:.1f}s")
        print("\nSpeaker breakdown:")
        for speaker, data in sorted(stats["speakers"].items()):
            print(
                f"  {speaker}: {data['segments']} segments, "
                f"{data['total_time']:.1f}s ({data['percentage']}%)"
            )
        print("=" * 60)

    except Exception as e:
        logger.error(f"Diarization failed: {e}")
        sys.exit(1)