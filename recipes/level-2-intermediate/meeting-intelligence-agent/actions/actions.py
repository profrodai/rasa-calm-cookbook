# recipes/level-2-intermediate/meeting-intelligence-agent/actions/actions.py
"""
Custom Rasa Actions for Meeting Intelligence Agent
"""

import logging
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

# Import meeting processing functions
import sys
from pathlib import Path

# Add parent directory to path so we can import meeting_processing
sys.path.insert(0, str(Path(__file__).parent.parent))

from meeting_processing import search_utterances
from meeting_processing.config import meeting_is_processed

from .llm_helper import format_context_only, generate_answer_from_context

# Setup logging
logger = logging.getLogger(__name__)


class ActionAnswerMeetingQuestion(Action):
    """
    Main action for answering questions about meetings.

    Workflow:
    1. Get question from user message
    2. Extract speaker filter if mentioned
    3. Search meeting transcript using semantic search
    4. Generate answer using LLM
    5. Respond with answer (as text + voice)
    """

    def name(self) -> Text:
        return "action_answer_meeting_question"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Execute the meeting Q&A action."""

        # Get user's question
        user_message = tracker.latest_message.get("text", "")
        logger.info(f"User question: {user_message}")

        # Get current meeting ID
        meeting_id = tracker.get_slot("meeting_id")
        if not meeting_id:
            meeting_id = "sample_earnings_call"  # Default

        logger.info(f"Querying meeting: {meeting_id}")

        # Check if meeting is processed
        if not meeting_is_processed(meeting_id):
            dispatcher.utter_message(response="utter_no_meeting")
            return []

        # Get speaker role filter (if mentioned by LLM)
        speaker_role = tracker.get_slot("speaker_role")
        speaker_roles = [speaker_role] if speaker_role else None

        if speaker_roles:
            logger.info(f"Filtering by speaker: {speaker_roles}")

        try:
            # Search meeting using semantic search
            logger.info("Searching meeting transcript...")
            results = search_utterances(
                meeting_id=meeting_id,
                query=user_message,
                speaker_roles=speaker_roles,
                max_results=10,
                use_semantic=True,
            )

            if not results:
                dispatcher.utter_message(response="utter_no_results")
                return [SlotSet("last_answer", None)]

            logger.info(f"Found {len(results)} relevant utterances")

            # Generate answer using LLM
            logger.info("Generating answer with LLM...")

            try:
                answer = generate_answer_from_context(
                    question=user_message,
                    context_utterances=results,
                    speaker_focus=speaker_role,
                )
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                # Fallback to formatted context
                answer = format_context_only(results)

            # Send answer
            dispatcher.utter_message(text=answer)

            # Store answer for potential follow-up
            return [SlotSet("last_answer", answer)]

        except ValueError as e:
            # Meeting not found or no embeddings
            logger.error(f"Meeting query failed: {e}")
            dispatcher.utter_message(response="utter_no_meeting")
            return []

        except Exception as e:
            # General error
            logger.error(f"Action failed: {e}")
            import traceback

            traceback.print_exc()
            dispatcher.utter_message(response="utter_processing_error")
            return []


class ActionListAvailableMeetings(Action):
    """List all processed meetings (optional helper action)."""

    def name(self) -> Text:
        return "action_list_available_meetings"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """List all processed meetings."""

        from meeting_processing.config import PROCESSED_DIR

        # Find all transcript files
        transcript_files = list(PROCESSED_DIR.glob("*_transcript.json"))

        if not transcript_files:
            dispatcher.utter_message(text="No meetings have been processed yet.")
            return []

        # Load meeting info
        from meeting_processing.storage import load_json

        meetings = []
        for file in transcript_files:
            try:
                transcript = load_json(file)
                meetings.append(
                    {
                        "id": transcript.get("meeting_id", "unknown"),
                        "title": transcript.get("title", "Untitled"),
                    }
                )
            except Exception:
                continue

        if not meetings:
            dispatcher.utter_message(text="No meetings available.")
            return []

        # Format response
        meeting_list = "\n".join([f"• {m['title']} (ID: {m['id']})" for m in meetings])

        dispatcher.utter_message(text=f"Available meetings:\n\n{meeting_list}")

        return []


class ActionSwitchMeeting(Action):
    """Switch to a different meeting (optional helper action)."""

    def name(self) -> Text:
        return "action_switch_meeting"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Switch to a different meeting."""

        # This is a placeholder for future functionality
        # You would extract the meeting ID from the user's message
        # For now, just acknowledge

        dispatcher.utter_message(
            text="Meeting switching is not yet implemented. "
            "To change meetings, update the meeting_id slot in your configuration."
        )

        return []