# recipes/level-3-advanced/meeting-intelligence-agent/meeting_processing/storage.py
"""
Helper functions for reading and writing JSON files.

Provides consistent interface for saving/loading meeting data.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .config import (
    get_diarization_path,
    get_speaker_map_path,
    get_transcript_path,
)

# Setup logging
logger = logging.getLogger(__name__)


def save_json(path: Path, data: Any, pretty: bool = True) -> None:
    """
    Save data to JSON file.

    Args:
        path: Output file path
        data: Data to save (must be JSON-serializable)
        pretty: If True, format with indentation
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)

        logger.debug(f"Saved JSON to: {path}")
    except Exception as e:
        logger.error(f"Failed to save JSON to {path}: {e}")
        raise


def load_json(path: Path) -> Any:
    """
    Load data from JSON file.

    Args:
        path: Input file path

    Returns:
        Loaded data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.debug(f"Loaded JSON from: {path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load JSON from {path}: {e}")
        raise


def load_transcript(meeting_id: str) -> Dict:
    """
    Load transcript for a meeting.

    Args:
        meeting_id: Meeting identifier

    Returns:
        Transcript dict with keys: meeting_id, title, utterances, metadata

    Raises:
        FileNotFoundError: If transcript doesn't exist
    """
    path = get_transcript_path(meeting_id)
    transcript = load_json(path)

    logger.info(f"Loaded transcript for {meeting_id}: {len(transcript.get('utterances', []))} utterances")

    return transcript


def load_diarization(meeting_id: str) -> list:
    """
    Load diarization segments for a meeting.

    Args:
        meeting_id: Meeting identifier

    Returns:
        List of diarization segments

    Raises:
        FileNotFoundError: If diarization doesn't exist
    """
    path = get_diarization_path(meeting_id)
    segments = load_json(path)

    logger.info(f"Loaded diarization for {meeting_id}: {len(segments)} segments")

    return segments


def load_speaker_map(meeting_id: str) -> Optional[Dict[str, str]]:
    """
    Load speaker map for a meeting if it exists.

    Args:
        meeting_id: Meeting identifier

    Returns:
        Speaker map dict like {"SPEAKER_0": "CEO", "SPEAKER_1": "CFO"}
        or None if no speaker map exists
    """
    path = get_speaker_map_path(meeting_id)

    if not path.exists():
        logger.debug(f"No speaker map found for {meeting_id}")
        return None

    speaker_map = load_json(path)

    logger.info(f"Loaded speaker map for {meeting_id}: {len(speaker_map)} speakers")

    return speaker_map


def save_speaker_map(meeting_id: str, speaker_map: Dict[str, str]) -> None:
    """
    Save speaker map for a meeting.

    Args:
        meeting_id: Meeting identifier
        speaker_map: Dict like {"SPEAKER_0": "CEO", "SPEAKER_1": "CFO"}
    """
    path = get_speaker_map_path(meeting_id)
    save_json(path, speaker_map)

    logger.info(f"Saved speaker map for {meeting_id}: {len(speaker_map)} speakers")


def get_utterances(meeting_id: str) -> list:
    """
    Get list of utterances from a transcript.

    Args:
        meeting_id: Meeting identifier

    Returns:
        List of utterance dicts

    Raises:
        FileNotFoundError: If transcript doesn't exist
    """
    transcript = load_transcript(meeting_id)
    return transcript.get("utterances", [])


def search_utterances_by_speaker(
    meeting_id: str, speaker: str
) -> list:
    """
    Get all utterances from a specific speaker.

    Args:
        meeting_id: Meeting identifier
        speaker: Speaker label (e.g., "SPEAKER_0" or "CEO")

    Returns:
        List of utterances from that speaker
    """
    utterances = get_utterances(meeting_id)
    matches = [u for u in utterances if u["speaker"] == speaker]

    logger.debug(f"Found {len(matches)} utterances from {speaker}")

    return matches


def search_utterances_by_keyword(
    meeting_id: str, keyword: str, case_sensitive: bool = False
) -> list:
    """
    Get all utterances containing a keyword.

    Args:
        meeting_id: Meeting identifier
        keyword: Keyword to search for
        case_sensitive: Whether search is case-sensitive

    Returns:
        List of utterances containing the keyword
    """
    utterances = get_utterances(meeting_id)

    if not case_sensitive:
        keyword = keyword.lower()

    matches = []
    for u in utterances:
        text = u["text"] if case_sensitive else u["text"].lower()
        if keyword in text:
            matches.append(u)

    logger.debug(f"Found {len(matches)} utterances containing '{keyword}'")

    return matches


def get_utterances_in_time_range(
    meeting_id: str, start: float, end: float
) -> list:
    """
    Get utterances within a time range.

    Args:
        meeting_id: Meeting identifier
        start: Start time in seconds
        end: End time in seconds

    Returns:
        List of utterances within the time range
    """
    utterances = get_utterances(meeting_id)

    matches = [
        u
        for u in utterances
        if u["start"] >= start and u["end"] <= end
    ]

    logger.debug(
        f"Found {len(matches)} utterances between {start:.1f}s and {end:.1f}s"
    )

    return matches


def export_transcript_to_text(
    meeting_id: str, output_path: Path, include_timestamps: bool = True
) -> None:
    """
    Export transcript to plain text file.

    Args:
        meeting_id: Meeting identifier
        output_path: Where to save text file
        include_timestamps: Whether to include timestamps
    """
    transcript = load_transcript(meeting_id)
    utterances = transcript.get("utterances", [])

    with open(output_path, "w", encoding="utf-8") as f:
        # Write header
        f.write(f"Transcript: {transcript.get('title', meeting_id)}\n")
        f.write(f"Duration: {transcript.get('metadata', {}).get('total_duration', 0):.1f}s\n")
        f.write("=" * 60 + "\n\n")

        # Write utterances
        for u in utterances:
            if include_timestamps:
                timestamp = f"[{u['start']:.1f}s - {u['end']:.1f}s]"
                f.write(f"{u['speaker']} {timestamp}:\n")
            else:
                f.write(f"{u['speaker']}:\n")

            f.write(f"{u['text']}\n\n")

    logger.info(f"Exported transcript to: {output_path}")


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
        print("Usage: python -m meeting_processing.storage <meeting_id>")
        print("Example: python -m meeting_processing.storage sample_earnings_call")
        sys.exit(1)

    meeting_id = sys.argv[1]

    try:
        # Load transcript
        transcript = load_transcript(meeting_id)

        print("\n" + "=" * 60)
        print(f"TRANSCRIPT: {transcript.get('title', meeting_id)}")
        print("=" * 60)
        print(f"Meeting ID: {transcript['meeting_id']}")
        print(f"Utterances: {len(transcript.get('utterances', []))}")
        print(f"Duration: {transcript.get('metadata', {}).get('total_duration', 0):.1f}s")
        print("=" * 60)

        # Show first 5 utterances
        utterances = transcript.get("utterances", [])
        if utterances:
            print("\nFirst 5 utterances:")
            for u in utterances[:5]:
                preview = u["text"][:80] + "..." if len(u["text"]) > 80 else u["text"]
                print(f"\n{u['speaker']} [{u['start']:.1f}s - {u['end']:.1f}s]:")
                print(f"  {preview}")

        # Load speaker map if exists
        speaker_map = load_speaker_map(meeting_id)
        if speaker_map:
            print("\nSpeaker Map:")
            for original, mapped in sorted(speaker_map.items()):
                print(f"  {original} → {mapped}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)