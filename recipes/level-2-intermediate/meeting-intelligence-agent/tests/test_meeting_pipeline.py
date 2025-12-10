# recipes/level-2-intermediate/meeting-intelligence-agent/tests/test_meeting_pipeline.py
# recipes/level-3-advanced/meeting-intelligence-agent/tests/test_meeting_pipeline.py
"""
Test suite for meeting processing pipeline.

Tests diarization, transcription, and vector embedding creation.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from meeting_processing import meeting_is_processed, process_meeting
from meeting_processing.config import (
    get_audio_path,
    get_diarization_path,
    get_transcript_path,
)
from meeting_processing.storage import load_transcript
from meeting_processing.vectordb import get_collection_stats, search_meeting

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestMeetingPipeline:
    """Test meeting processing pipeline."""

    def test_audio_file_exists(self):
        """Test that sample audio file exists."""
        meeting_id = "sample_earnings_call"

        try:
            audio_path = get_audio_path(meeting_id)
            assert audio_path.exists(), f"Audio file not found: {audio_path}"
            logger.info(f"✓ Audio file found: {audio_path}")
        except FileNotFoundError:
            pytest.skip("Sample audio file not downloaded yet")

    @pytest.mark.slow
    def test_process_meeting(self):
        """Test full meeting processing pipeline."""
        meeting_id = "sample_earnings_call"
        title = "Sample Earnings Call"

        # Skip if already processed
        if meeting_is_processed(meeting_id):
            logger.info("Meeting already processed, skipping")
            pytest.skip("Meeting already processed")

        # Skip if no audio
        try:
            get_audio_path(meeting_id)
        except FileNotFoundError:
            pytest.skip("Sample audio not available")

        # Process meeting
        result = process_meeting(
            meeting_id=meeting_id, title=title, create_vectors=True, force=False
        )

        # Check result
        assert result["status"] == "success", f"Processing failed: {result}"
        assert result["utterances"] > 0, "No utterances created"
        assert result["speakers"] >= 2, "Expected at least 2 speakers"

        logger.info(f"✓ Processed meeting: {result}")

    def test_transcript_loaded(self):
        """Test loading transcript."""
        meeting_id = "sample_earnings_call"

        if not meeting_is_processed(meeting_id):
            pytest.skip("Meeting not processed yet")

        transcript = load_transcript(meeting_id)

        assert "meeting_id" in transcript
        assert "title" in transcript
        assert "utterances" in transcript
        assert len(transcript["utterances"]) > 0

        logger.info(f"✓ Loaded transcript with {len(transcript['utterances'])} utterances")

    def test_diarization_output(self):
        """Test diarization output exists and is valid."""
        meeting_id = "sample_earnings_call"

        diarization_path = get_diarization_path(meeting_id)

        if not diarization_path.exists():
            pytest.skip("Diarization not yet run")

        from meeting_processing.storage import load_json

        segments = load_json(diarization_path)

        assert isinstance(segments, list)
        assert len(segments) > 0

        # Check segment structure
        first_seg = segments[0]
        assert "speaker" in first_seg
        assert "start" in first_seg
        assert "end" in first_seg
        assert first_seg["start"] < first_seg["end"]

        logger.info(f"✓ Diarization has {len(segments)} segments")

    def test_transcript_structure(self):
        """Test transcript structure is correct."""
        meeting_id = "sample_earnings_call"

        if not meeting_is_processed(meeting_id):
            pytest.skip("Meeting not processed yet")

        transcript = load_transcript(meeting_id)
        utterances = transcript["utterances"]

        assert len(utterances) > 0

        # Check utterance structure
        first_utt = utterances[0]
        assert "id" in first_utt
        assert "speaker" in first_utt
        assert "start" in first_utt
        assert "end" in first_utt
        assert "text" in first_utt
        assert isinstance(first_utt["text"], str)
        assert len(first_utt["text"]) > 0

        logger.info(f"✓ Transcript structure valid")

    def test_vector_embeddings(self):
        """Test that vector embeddings exist."""
        meeting_id = "sample_earnings_call"

        if not meeting_is_processed(meeting_id):
            pytest.skip("Meeting not processed yet")

        try:
            stats = get_collection_stats(meeting_id)

            assert stats["total_embeddings"] > 0
            assert stats["meeting_id"] == meeting_id

            logger.info(f"✓ Vector embeddings: {stats['total_embeddings']}")

        except ValueError:
            pytest.skip("Vector embeddings not created yet")

    def test_semantic_search(self):
        """Test semantic search functionality."""
        meeting_id = "sample_earnings_call"

        if not meeting_is_processed(meeting_id):
            pytest.skip("Meeting not processed yet")

        try:
            # Search for common earnings call terms
            queries = [
                "revenue",
                "profit margins",
                "guidance",
                "market conditions",
            ]

            for query in queries:
                results = search_meeting(meeting_id, query, n_results=5)

                # Should find at least some results
                if len(results) > 0:
                    logger.info(f"✓ Search for '{query}': {len(results)} results")
                    assert results[0]["score"] > 0.3  # Minimum relevance
                    break
            else:
                pytest.skip("No search results found")

        except ValueError:
            pytest.skip("Vector embeddings not created yet")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])