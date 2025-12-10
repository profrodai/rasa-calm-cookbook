# recipes/level-2-intermediate/meeting-intelligence-agent/meeting_processing/transcription.py
"""
Audio transcription using faster-whisper (optimized for M4 Mac).

Takes diarization segments and transcribes each one, creating a structured transcript.
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List

from faster_whisper import WhisperModel

from .config import (
    TARGET_SAMPLE_RATE,
    WHISPER_BEAM_SIZE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    WHISPER_LANGUAGE,
    WHISPER_MODEL,
    WHISPER_TASK,
    WHISPER_VAD_FILTER,
    get_audio_path,
    get_transcript_path,
)

# Setup logging
logger = logging.getLogger(__name__)


def load_whisper_model() -> WhisperModel:
    """
    Load faster-whisper model.

    Returns:
        Loaded Whisper model ready for transcription
    """
    logger.info(f"Loading Whisper model: {WHISPER_MODEL}")
    logger.info(f"Device: {WHISPER_DEVICE}, Compute type: {WHISPER_COMPUTE_TYPE}")

    try:
        model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
            cpu_threads=4 if WHISPER_DEVICE == "cpu" else 0,
        )
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise RuntimeError(
            f"Could not load Whisper model '{WHISPER_MODEL}'. "
            f"Error: {e}\n"
            f"Try installing: pip install faster-whisper --break-system-packages"
        )

    logger.info("Whisper model loaded successfully")
    return model


def extract_audio_segment(
    audio_path: Path, start: float, end: float, output_path: Path
) -> None:
    """
    Extract a time segment from audio file using ffmpeg.

    Args:
        audio_path: Source audio file
        start: Start time in seconds
        end: End time in seconds
        output_path: Where to save extracted segment

    Raises:
        RuntimeError: If ffmpeg fails
    """
    duration = end - start

    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-i",
        str(audio_path),
        "-ss",
        str(start),
        "-t",
        str(duration),
        "-ar",
        str(TARGET_SAMPLE_RATE),  # Resample to 16kHz
        "-ac",
        "1",  # Convert to mono
        "-f",
        "wav",  # Output format
        str(output_path),
        "-loglevel",
        "error",  # Only show errors
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"ffmpeg failed to extract segment [{start:.2f}s - {end:.2f}s]: "
            f"{e.stderr.decode()}"
        )


def transcribe_segment(model: WhisperModel, audio_path: Path) -> str:
    """
    Transcribe a single audio segment.

    Args:
        model: Loaded Whisper model
        audio_path: Path to audio file

    Returns:
        Transcribed text
    """
    segments, info = model.transcribe(
        str(audio_path),
        language=WHISPER_LANGUAGE if WHISPER_LANGUAGE else None,
        task=WHISPER_TASK,
        beam_size=WHISPER_BEAM_SIZE,
        vad_filter=WHISPER_VAD_FILTER,
        vad_parameters=dict(min_silence_duration_ms=500) if WHISPER_VAD_FILTER else None,
    )

    # Combine all segments into one text
    text_parts = [segment.text.strip() for segment in segments]
    text = " ".join(text_parts)

    return text.strip()


def transcribe_segments(
    meeting_id: str,
    diarization_segments: List[Dict],
    title: str = None,
) -> List[Dict]:
    """
    Transcribe all diarization segments to create full meeting transcript.

    Args:
        meeting_id: Meeting identifier
        diarization_segments: List of diarization segments from pyannote
        title: Optional meeting title

    Returns:
        List of utterances with transcriptions:
        [
            {
                "id": 1,
                "speaker": "SPEAKER_0",
                "start": 12.34,
                "end": 18.90,
                "text": "Thank you for joining our Q3 earnings call..."
            },
            ...
        ]

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If transcription fails
    """
    logger.info(f"Starting transcription for meeting: {meeting_id}")
    logger.info(f"Segments to transcribe: {len(diarization_segments)}")

    # Get audio path
    audio_path = get_audio_path(meeting_id)
    logger.info(f"Audio file: {audio_path}")

    # Load Whisper model
    model = load_whisper_model()

    # Create temporary directory for audio segments
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        utterances = []

        for idx, segment in enumerate(diarization_segments, start=1):
            logger.info(
                f"Transcribing segment {idx}/{len(diarization_segments)} "
                f"[{segment['start']:.1f}s - {segment['end']:.1f}s]"
            )

            # Extract audio segment
            segment_path = temp_path / f"segment_{idx}.wav"
            try:
                extract_audio_segment(
                    audio_path, segment["start"], segment["end"], segment_path
                )
            except RuntimeError as e:
                logger.error(f"Failed to extract segment {idx}: {e}")
                # Skip this segment
                continue

            # Transcribe segment
            try:
                text = transcribe_segment(model, segment_path)
            except Exception as e:
                logger.error(f"Failed to transcribe segment {idx}: {e}")
                text = "[TRANSCRIPTION FAILED]"

            # Create utterance
            utterance = {
                "id": idx,
                "speaker": segment["speaker"],
                "start": segment["start"],
                "end": segment["end"],
                "text": text,
            }

            utterances.append(utterance)

            # Log progress
            if text and text != "[TRANSCRIPTION FAILED]":
                preview = text[:80] + "..." if len(text) > 80 else text
                logger.info(f"  → {segment['speaker']}: {preview}")

    logger.info(f"Transcription complete: {len(utterances)} utterances")

    # Build full transcript structure
    transcript = {
        "meeting_id": meeting_id,
        "title": title or f"Meeting {meeting_id}",
        "utterances": utterances,
        "metadata": {
            "total_utterances": len(utterances),
            "total_duration": (
                max(u["end"] for u in utterances) if utterances else 0.0
            ),
            "whisper_model": WHISPER_MODEL,
            "whisper_language": WHISPER_LANGUAGE,
        },
    }

    # Save to JSON
    output_path = get_transcript_path(meeting_id)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)

    logger.info(f"Transcript saved to: {output_path}")

    return utterances


def apply_speaker_map(
    utterances: List[Dict], speaker_map: Dict[str, str]
) -> List[Dict]:
    """
    Apply human-readable speaker labels to utterances.

    Args:
        utterances: List of utterances with SPEAKER_X labels
        speaker_map: Mapping like {"SPEAKER_0": "CEO", "SPEAKER_1": "CFO"}

    Returns:
        Utterances with updated speaker labels
    """
    if not speaker_map:
        return utterances

    logger.info("Applying speaker map...")

    for utterance in utterances:
        original_speaker = utterance["speaker"]
        if original_speaker in speaker_map:
            utterance["speaker"] = speaker_map[original_speaker]
            logger.debug(f"Mapped {original_speaker} → {utterance['speaker']}")

    return utterances


def get_transcript_summary(utterances: List[Dict]) -> Dict:
    """
    Generate summary statistics about a transcript.

    Args:
        utterances: List of utterances

    Returns:
        Summary dict with stats
    """
    if not utterances:
        return {
            "total_utterances": 0,
            "total_duration": 0.0,
            "total_words": 0,
            "speakers": {},
        }

    total_duration = max(u["end"] for u in utterances)
    total_words = sum(len(u["text"].split()) for u in utterances)

    # Per-speaker stats
    speaker_stats = {}
    for utt in utterances:
        speaker = utt["speaker"]
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {
                "utterances": 0,
                "words": 0,
                "duration": 0.0,
            }

        speaker_stats[speaker]["utterances"] += 1
        speaker_stats[speaker]["words"] += len(utt["text"].split())
        speaker_stats[speaker]["duration"] += utt["end"] - utt["start"]

    # Add percentages
    for speaker, stats in speaker_stats.items():
        stats["word_percentage"] = round(
            (stats["words"] / total_words * 100) if total_words > 0 else 0, 2
        )
        stats["duration"] = round(stats["duration"], 2)

    return {
        "total_utterances": len(utterances),
        "total_duration": round(total_duration, 2),
        "total_words": total_words,
        "speakers": speaker_stats,
    }


# ==============================================================================
# CLI Interface for standalone testing
# ==============================================================================

if __name__ == "__main__":
    import sys

    from .storage import load_json

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) < 2:
        print(
            "Usage: python -m meeting_processing.transcription <meeting_id> [title]"
        )
        print("Example: python -m meeting_processing.transcription sample_earnings_call")
        sys.exit(1)

    meeting_id = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        # Load diarization
        from .config import get_diarization_path

        diarization_path = get_diarization_path(meeting_id)
        if not diarization_path.exists():
            logger.error(f"Diarization file not found: {diarization_path}")
            logger.error("Run diarization first:")
            logger.error(f"  python -m meeting_processing.diarization {meeting_id}")
            sys.exit(1)

        segments = load_json(diarization_path)

        # Transcribe
        utterances = transcribe_segments(meeting_id, segments, title)

        # Print summary
        summary = get_transcript_summary(utterances)
        print("\n" + "=" * 60)
        print("TRANSCRIPTION SUMMARY")
        print("=" * 60)
        print(f"Total utterances: {summary['total_utterances']}")
        print(f"Total duration: {summary['total_duration']:.1f}s")
        print(f"Total words: {summary['total_words']}")
        print("\nSpeaker breakdown:")
        for speaker, data in sorted(summary["speakers"].items()):
            print(
                f"  {speaker}: {data['utterances']} utterances, "
                f"{data['words']} words ({data['word_percentage']}%)"
            )
        print("=" * 60)

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)