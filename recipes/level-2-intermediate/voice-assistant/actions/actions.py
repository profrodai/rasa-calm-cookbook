from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionGetAccountBalance(Action):
    def name(self) -> Text:
        return "action_get_account_balance"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Get account balance from mock database."""
        account_type = tracker.get_slot("account_type")
        
        # Normalize account type
        if account_type:
            account_type = account_type.lower()
            if "check" in account_type:
                account_type = "checking"
            elif "sav" in account_type:
                account_type = "savings"
        
        # Mock balance data
        balances = {
            "checking": "$2,450.75",
            "savings": "$15,230.00"
        }
        
        balance = balances.get(account_type, "$0.00")
        
        return [
            SlotSet("account_type", account_type),
            SlotSet("account_balance", balance)
        ]


class ActionGetAccounts(Action):
    def name(self) -> Text:
        return "action_get_accounts"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Get list of user's accounts."""
        # Mock account data
        accounts = "checking and savings"
        
        return [SlotSet("available_accounts", accounts)]


class ActionProcessTransfer(Action):
    def name(self) -> Text:
        return "action_process_transfer"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Process money transfer between accounts."""
        from_account = tracker.get_slot("transfer_from_account")
        to_account = tracker.get_slot("transfer_to_account")
        amount = tracker.get_slot("transfer_amount")
        
        # In production, this would call banking API
        # For demo, we just confirm the transfer happened
        
        return []


class ActionBlockCard(Action):
    def name(self) -> Text:
        return "action_block_card"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Block a lost or stolen card."""
        card_last_four = tracker.get_slot("card_last_four")
        
        # Mock card blocking - in production, call banking API
        # Validate card last four digits
        if card_last_four and len(card_last_four) == 4 and card_last_four.isdigit():
            card_blocked = True
        else:
            card_blocked = False
        
        return [SlotSet("card_blocked", card_blocked)]


class ActionGetTransactions(Action):
    def name(self) -> Text:
        return "action_get_transactions"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        """Get recent transactions."""
        # Mock transaction data
        # In production, fetch from banking API
        
        return []