# recipes/level-2-intermediate/meeting-intelligence-agent/meeting_processing/__init__.py
"""
Meeting Processing Module

Provides end-to-end processing of meeting audio:
  1. Speaker diarization (pyannote)
  2. Transcription (faster-whisper)
  3. Vector embeddings (ChromaDB + sentence-transformers)
  4. Semantic search retrieval

Main entry point: process_meeting(meeting_id, title)
"""

import logging
from pathlib import Path
from typing import Optional

from .config import (
    BASE_DIR,
    DEFAULT_MEETING_ID,
    MEETINGS_DIR,
    PROCESSED_DIR,
    RECORDINGS_DIR,
    SPEAKER_MAP_DIR,
    get_audio_path,
    meeting_is_processed,
)
from .diarization import merge_same_speaker_segments, run_diarization
from .retrieval import search_utterances
from .storage import load_speaker_map, load_transcript
from .transcription import apply_speaker_map, transcribe_segments
from .vectordb import create_embeddings

# Setup logging
logger = logging.getLogger(__name__)

# Package version
__version__ = "0.1.0"

# Public API
__all__ = [
    "process_meeting",
    "search_utterances",
    "load_transcript",
    "load_speaker_map",
    "meeting_is_processed",
    "get_audio_path",
]


def process_meeting(
    meeting_id: str,
    title: Optional[str] = None,
    apply_speaker_labels: bool = True,
    create_vectors: bool = True,
    force: bool = False,
) -> dict:
    """
    Process a meeting end-to-end: diarization → transcription → embeddings.

    This is the main entry point for the meeting processing pipeline.

    Args:
        meeting_id: Meeting identifier (must match audio file in recordings/)
        title: Optional meeting title (e.g., "Q3 2024 Earnings Call")
        apply_speaker_labels: If True, apply speaker map if it exists
        create_vectors: If True, create vector embeddings for search
        force: If True, reprocess even if already processed

    Returns:
        Dictionary with processing results:
        {
            "meeting_id": str,
            "title": str,
            "status": "success" | "error",
            "utterances": int,
            "speakers": int,
            "duration": float,
        }

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If processing fails

    Example:
        >>> from meeting_processing import process_meeting
        >>> result = process_meeting("q3_2024_call", "Q3 2024 Earnings Call")
        >>> print(f"Processed {result['utterances']} utterances")
    """
    logger.info("=" * 60)
    logger.info(f"Processing Meeting: {meeting_id}")
    if title:
        logger.info(f"Title: {title}")
    logger.info("=" * 60)

    try:
        # Check if audio exists
        audio_path = get_audio_path(meeting_id)
        logger.info(f"Audio file: {audio_path}")

        # Check if already processed
        if meeting_is_processed(meeting_id) and not force:
            logger.info("Meeting already processed (use force=True to reprocess)")
            transcript = load_transcript(meeting_id)
            return {
                "meeting_id": meeting_id,
                "title": transcript.get("title", ""),
                "status": "already_processed",
                "utterances": len(transcript.get("utterances", [])),
                "speakers": len(
                    set(u["speaker"] for u in transcript.get("utterances", []))
                ),
                "duration": transcript.get("metadata", {}).get("total_duration", 0.0),
            }

        # Step 1: Speaker Diarization
        logger.info("\n" + "=" * 60)
        logger.info("STEP 1/3: Speaker Diarization")
        logger.info("=" * 60)

        segments = run_diarization(meeting_id)

        # Optionally merge same-speaker segments
        segments = merge_same_speaker_segments(segments, max_gap_seconds=1.0)

        logger.info(f"✓ Diarization complete: {len(segments)} segments")

        # Step 2: Transcription
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2/3: Transcription")
        logger.info("=" * 60)

        utterances = transcribe_segments(meeting_id, segments, title=title)

        logger.info(f"✓ Transcription complete: {len(utterances)} utterances")

        # Apply speaker labels if map exists
        if apply_speaker_labels:
            speaker_map = load_speaker_map(meeting_id)
            if speaker_map:
                logger.info("Applying speaker labels...")
                utterances = apply_speaker_map(utterances, speaker_map)

                # Save updated transcript
                from .config import get_transcript_path
                from .storage import save_json

                transcript = load_transcript(meeting_id)
                transcript["utterances"] = utterances
                save_json(get_transcript_path(meeting_id), transcript)

                logger.info("✓ Speaker labels applied")

        # Step 3: Create Vector Embeddings
        if create_vectors:
            logger.info("\n" + "=" * 60)
            logger.info("STEP 3/3: Creating Vector Embeddings")
            logger.info("=" * 60)

            create_embeddings(meeting_id, force=True)

            logger.info("✓ Vector embeddings created")

        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("PROCESSING COMPLETE ✓")
        logger.info("=" * 60)

        transcript = load_transcript(meeting_id)
        utterances_list = transcript.get("utterances", [])
        speakers = set(u["speaker"] for u in utterances_list)

        result = {
            "meeting_id": meeting_id,
            "title": transcript.get("title", ""),
            "status": "success",
            "utterances": len(utterances_list),
            "speakers": len(speakers),
            "duration": transcript.get("metadata", {}).get("total_duration", 0.0),
        }

        logger.info(f"Utterances: {result['utterances']}")
        logger.info(f"Speakers: {result['speakers']}")
        logger.info(f"Duration: {result['duration']:.1f}s")
        logger.info("=" * 60)

        return result

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        import traceback

        traceback.print_exc()
        return {
            "meeting_id": meeting_id,
            "title": title or "",
            "status": "error",
            "error": str(e),
        }


# ==============================================================================
# CLI Interface
# ==============================================================================

if __name__ == "__main__":
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if len(sys.argv) < 2:
        print("Usage: python -m meeting_processing <meeting_id> [title]")
        print("\nExample:")
        print('  python -m meeting_processing sample_earnings_call "Sample Earnings Call"')
        print("\nOptions:")
        print("  --force          Reprocess even if already processed")
        print("  --no-vectors     Skip vector embedding creation")
        print("  --no-labels      Don't apply speaker labels")
        sys.exit(1)

    meeting_id = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None

    # Parse flags
    force = "--force" in sys.argv
    create_vectors = "--no-vectors" not in sys.argv
    apply_labels = "--no-labels" not in sys.argv

    result = process_meeting(
        meeting_id=meeting_id,
        title=title,
        apply_speaker_labels=apply_labels,
        create_vectors=create_vectors,
        force=force,
    )

    # Exit with appropriate code
    if result["status"] in ["success", "already_processed"]:
        sys.exit(0)
    else:
        sys.exit(1)