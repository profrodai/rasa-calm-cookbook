# recipes/level-1-basic/basic-tutorial/actions/actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionCheckSufficientFunds(Action):
    def name(self) -> Text:
        return "action_check_sufficient_funds"

    def run(
        self, 
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Check if user has sufficient funds for the transfer."""
        # Hard-coded balance for tutorial purposes
        # In production, this would be retrieved from a database or API
        balance = 1000.0
        
        # Get the transfer amount from the slot
        amount_str = tracker.get_slot("amount")
        
        try:
            # Extract numeric value from amount string
            amount = float(amount_str.replace("$", "").replace(",", ""))
        except (ValueError, AttributeError):
            # If we can't parse the amount, assume insufficient funds
            return [SlotSet("has_sufficient_funds", False)]
        
        # Check if user has sufficient funds
        has_sufficient_funds = amount <= balance
        
        return [SlotSet("has_sufficient_funds", has_sufficient_funds)]