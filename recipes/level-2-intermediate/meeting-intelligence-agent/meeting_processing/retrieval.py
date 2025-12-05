# recipes/level-3-advanced/meeting-intelligence-agent/meeting_processing/retrieval.py
"""
Hybrid retrieval combining keyword search and semantic search via ChromaDB.

Provides the main search interface used by Rasa actions.
"""

import logging
from typing import Dict, List, Optional

from .config import RETRIEVAL_TOP_K
from .storage import load_speaker_map
from .vectordb import search_meeting as chroma_search_meeting

# Setup logging
logger = logging.getLogger(__name__)


def search_utterances(
    meeting_id: str,
    query: str,
    speaker_roles: Optional[List[str]] = None,
    max_results: int = RETRIEVAL_TOP_K,
    use_semantic: bool = True,
) -> List[Dict]:
    """
    Search utterances in a meeting transcript.

    Uses semantic search via ChromaDB by default, with optional speaker filtering.

    Args:
        meeting_id: Meeting identifier
        query: Search query text
        speaker_roles: Optional list of speaker roles to filter by (e.g., ["CEO", "CFO"])
        max_results: Maximum number of results to return
        use_semantic: If True, use semantic search; if False, use keyword search

    Returns:
        List of matching utterances:
        [
            {
                "id": 42,
                "speaker": "CEO",
                "start": 123.4,
                "end": 145.6,
                "text": "...",
                "score": 0.85  # similarity score (only for semantic search)
            },
            ...
        ]
    """
    logger.info(
        f"Searching meeting '{meeting_id}' for: '{query}' "
        f"(max_results={max_results}, use_semantic={use_semantic})"
    )

    if speaker_roles:
        logger.info(f"Filtering by speaker roles: {speaker_roles}")

    # Load speaker map to convert roles to SPEAKER_X IDs if needed
    speaker_map = load_speaker_map(meeting_id)
    reverse_map = {}
    if speaker_map:
        # Create reverse mapping: "CEO" -> "SPEAKER_0"
        reverse_map = {v: k for k, v in speaker_map.items()}

    # If semantic search is enabled, use ChromaDB
    if use_semantic:
        return _semantic_search(
            meeting_id, query, speaker_roles, max_results, reverse_map
        )
    else:
        # Fallback to keyword search
        return _keyword_search(meeting_id, query, speaker_roles, max_results)


def _semantic_search(
    meeting_id: str,
    query: str,
    speaker_roles: Optional[List[str]],
    max_results: int,
    reverse_speaker_map: Dict[str, str],
) -> List[Dict]:
    """
    Perform semantic search using ChromaDB.

    Args:
        meeting_id: Meeting identifier
        query: Search query
        speaker_roles: Optional speaker roles to filter
        max_results: Max results
        reverse_speaker_map: Mapping from role names to SPEAKER_X

    Returns:
        List of matching utterances with scores
    """
    all_results = []

    if speaker_roles:
        # Search for each speaker role separately
        for role in speaker_roles:
            # Convert role to SPEAKER_X if needed
            speaker_id = reverse_speaker_map.get(role, role)

            logger.debug(f"Searching for speaker: {speaker_id} (role: {role})")

            try:
                results = chroma_search_meeting(
                    meeting_id=meeting_id,
                    query=query,
                    n_results=max_results,
                    speaker_filter=speaker_id,
                )
                all_results.extend(results)
            except ValueError as e:
                logger.error(f"Search failed for {meeting_id}: {e}")
                raise

    else:
        # Search all speakers
        try:
            all_results = chroma_search_meeting(
                meeting_id=meeting_id, query=query, n_results=max_results
            )
        except ValueError as e:
            logger.error(f"Search failed for {meeting_id}: {e}")
            raise

    # Sort by score (descending) and limit
    all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
    results = all_results[:max_results]

    logger.info(f"Semantic search returned {len(results)} results")

    return results


def _keyword_search(
    meeting_id: str,
    query: str,
    speaker_roles: Optional[List[str]],
    max_results: int,
) -> List[Dict]:
    """
    Fallback keyword search (simple text matching).

    This is a basic implementation - semantic search is preferred.

    Args:
        meeting_id: Meeting identifier
        query: Search query
        speaker_roles: Optional speaker roles to filter
        max_results: Max results

    Returns:
        List of matching utterances (without scores)
    """
    from .storage import get_utterances

    logger.info("Using keyword search (fallback)")

    utterances = get_utterances(meeting_id)

    # Tokenize query
    query_tokens = set(query.lower().split())

    # Score each utterance
    scored_utterances = []
    for utt in utterances:
        # Filter by speaker if specified
        if speaker_roles and utt["speaker"] not in speaker_roles:
            continue

        # Simple token overlap scoring
        text_tokens = set(utt["text"].lower().split())
        overlap = len(query_tokens & text_tokens)

        if overlap > 0:
            scored_utterances.append((overlap, utt))

    # Sort by score (descending)
    scored_utterances.sort(key=lambda x: x[0], reverse=True)

    # Take top results
    results = [utt for _, utt in scored_utterances[:max_results]]

    logger.info(f"Keyword search returned {len(results)} results")

    return results


def get_context_around_utterance(
    meeting_id: str, utterance_id: int, context_size: int = 2
) -> List[Dict]:
    """
    Get utterances surrounding a given utterance for context.

    Args:
        meeting_id: Meeting identifier
        utterance_id: ID of the central utterance
        context_size: Number of utterances to include before and after

    Returns:
        List of utterances including context
    """
    from .storage import get_utterances

    utterances = get_utterances(meeting_id)

    # Find the index of the target utterance
    target_idx = None
    for i, utt in enumerate(utterances):
        if utt["id"] == utterance_id:
            target_idx = i
            break

    if target_idx is None:
        logger.warning(f"Utterance {utterance_id} not found")
        return []

    # Get context window
    start_idx = max(0, target_idx - context_size)
    end_idx = min(len(utterances), target_idx + context_size + 1)

    context = utterances[start_idx:end_idx]

    logger.debug(
        f"Got {len(context)} utterances as context around utterance {utterance_id}"
    )

    return context


def format_results_for_llm(results: List[Dict], include_timestamps: bool = True) -> str:
    """
    Format search results as context text for LLM.

    Args:
        results: List of search results
        include_timestamps: Whether to include timestamps

    Returns:
        Formatted context string suitable for LLM prompt
    """
    if not results:
        return "No relevant information found in the meeting."

    context_parts = []

    for i, result in enumerate(results, 1):
        speaker = result["speaker"]
        text = result["text"]

        if include_timestamps:
            start = result["start"]
            end = result["end"]
            timestamp = f" [{start:.1f}s-{end:.1f}s]"
        else:
            timestamp = ""

        # Add score if available
        score_info = ""
        if "score" in result:
            score_info = f" (relevance: {result['score']:.2f})"

        context_parts.append(f"{i}. {speaker}{timestamp}{score_info}:\n   {text}")

    return "\n\n".join(context_parts)


# ==============================================================================
# CLI Interface for standalone testing
# ==============================================================================

if __name__ == "__main__":
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) < 3:
        print("Usage: python -m meeting_processing.retrieval <meeting_id> <query>")
        print("Example: python -m meeting_processing.retrieval sample_earnings_call 'operating margins'")
        print("\nOptional flags:")
        print("  --speaker <role>   Filter by speaker (e.g., --speaker CEO)")
        print("  --keyword          Use keyword search instead of semantic")
        print("  --max <n>          Maximum results (default: 10)")
        sys.exit(1)

    meeting_id = sys.argv[1]
    query_parts = []
    speaker_roles = []
    use_semantic = True
    max_results = 10

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "--speaker" and i + 1 < len(sys.argv):
            speaker_roles.append(sys.argv[i + 1])
            i += 2
        elif arg == "--keyword":
            use_semantic = False
            i += 1
        elif arg == "--max" and i + 1 < len(sys.argv):
            max_results = int(sys.argv[i + 1])
            i += 2
        else:
            query_parts.append(arg)
            i += 1

    query = " ".join(query_parts)

    try:
        # Search
        results = search_utterances(
            meeting_id=meeting_id,
            query=query,
            speaker_roles=speaker_roles if speaker_roles else None,
            max_results=max_results,
            use_semantic=use_semantic,
        )

        # Display results
        print("\n" + "=" * 60)
        print(f"SEARCH RESULTS for: '{query}'")
        if speaker_roles:
            print(f"Filtered by speakers: {speaker_roles}")
        print("=" * 60)

        if not results:
            print("\nNo results found.")
        else:
            for i, result in enumerate(results, 1):
                score_str = ""
                if "score" in result:
                    score_str = f" (score: {result['score']:.3f})"

                print(f"\n{i}. {result['speaker']}{score_str}")
                print(f"   [{result['start']:.1f}s - {result['end']:.1f}s]")

                text = result["text"]
                if len(text) > 200:
                    text = text[:200] + "..."

                print(f"   {text}")

        print("\n" + "=" * 60)
        print(f"Total results: {len(results)}")
        print("=" * 60)

        # Show formatted context
        print("\n" + "=" * 60)
        print("FORMATTED CONTEXT FOR LLM:")
        print("=" * 60)
        print(format_results_for_llm(results))
        print("=" * 60)

    except Exception as e:
        logger.error(f"Search failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)