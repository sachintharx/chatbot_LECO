import csv
import random
import re
from ...models import TreeNode

def handle_bill_inquiries(user_message, session):
    # Create an instance of the bill inquiries tree
    bill_inquiries_tree = BillInquiriesTree()

    # Use the state machine to handle the state transitions and responses
    return bill_inquiries_tree.handle_state(user_message, session)


class BillInquiriesTree:
    def __init__(self):
        # Create nodes for different states
        self.root = TreeNode('awaiting_account_number', self.awaiting_account_number)

        # Create nodes for awaiting_mobile_number state and exit
        self.awaiting_mobile_number_node = TreeNode('awaiting_mobile_number', self.awaiting_mobile_number)
        self.awaiting_bill_details_node = TreeNode('awaiting_bill_details', self.awaiting_bill_details)
        self.exit_node = TreeNode('exit', self.exit_request)

        # Add children nodes (state transitions)
        self.root.add_child('awaiting_mobile_number', self.awaiting_mobile_number_node)
        self.awaiting_mobile_number_node.add_child('awaiting_bill_details', self.awaiting_bill_details_node)
        self.awaiting_bill_details_node.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        # Check if user wants to end the session
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'

        # Get the current state from the session (default to 'awaiting_account_number')
        current_state = session.get('current_state', 'awaiting_account_number')

        # Traverse the tree from the root based on current state
        current_node = self._find_node(self.root, current_state)

        if current_node:
            # Handle the current state and proceed
            response = current_node.handle(user_message, session)

            # If the state has transitioned, the response will be returned
            return response
        else:
            return self.reset_bill_inquiries(session)

    def _find_node(self, current_node, state_name):
        # Traverse the tree to find the node corresponding to the state_name
        if current_node.name == state_name:
            return current_node

        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def awaiting_account_number(self, user_message, session):
        # Extract account number from user message
        account_number = extract_account_number(user_message)

        if account_number:
            session['account_number'] = account_number
            session['current_state'] = 'awaiting_mobile_number'  # Transition to the next state
            response = self._choose_response([
                f"Thank you for providing your account number: {account_number}. Please provide your registered mobile number.",
                f"Got it! Your account number is {account_number}. Now, tell me your registered mobile number.",
                f"Thank you for providing your account number: {account_number}. Can you also share your registered mobile number?"
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)
        else:
            response = self._choose_response([
                "Please enter your account number to inquire about your bill.",
                "Could you please provide your account number?",
                "We need your account number to proceed with the bill inquiry."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def awaiting_mobile_number(self, user_message, session):
        # Extract mobile number from user message
        mobile_number = extract_mobile_number(user_message)

        if mobile_number:
            session['mobile_number'] = mobile_number
            session['current_state'] = 'awaiting_bill_details'  # Transition to the next state
            response = self._choose_response([
                f"Thank you for providing your mobile number: {mobile_number}. Please wait while we fetch your bill details.",
                f"Got it! Your mobile number is {mobile_number}. Fetching your bill details now.",
                f"Thank you for providing your mobile number: {mobile_number}. Retrieving your bill details."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)
        else:
            response = self._choose_response([
                "Please enter your registered mobile number.",
                "Could you please provide your registered mobile number?",
                "We need your registered mobile number to proceed with the bill inquiry."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def awaiting_bill_details(self, user_message, session):
        # Validate account number and mobile number using CSV file
        account_number = session.get('account_number')
        mobile_number = session.get('mobile_number')
        bill_details = fetch_bill_details(account_number, mobile_number)

        if bill_details:
            session['bill_details'] = bill_details
            session['current_state'] = 'exit'  # After fetching bill details, transition to exit state
            response = self._choose_response([
                f"Your bill details are as follows: {bill_details}.",
                f"Here are your bill details: {bill_details}.",
                f"Your bill details: {bill_details}."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)
        else:
            response = self._choose_response([
                "Invalid account number or mobile number. Please try again.",
                "We couldn't find your bill details. Please check your account number and mobile number.",
                "The account number or mobile number you provided is incorrect. Please try again."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def exit_request(self, user_message, session):
        # Handle customer exit request
        response = "Thank you for using our service. If you need further assistance, feel free to ask!"
        update_chat_history(session, "bot", response)
        session.clear()  # End the session
        return response

    def reset_bill_inquiries(self, session):
        # Reset the session to the initial state
        session['current_state'] = 'awaiting_account_number'
        session['chat_history'] = []  # Reset chat history

        response = "Please enter your account number to inquire about your bill."
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def _choose_response(self, responses):
        # Randomly choose a response from the list of variations
        return random.choice(responses)

    def _split_message(self, message, max_length=160):
        # Split long messages into multiple smaller chunks
        if len(message) <= max_length:
            return message

        parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        return parts


# Utility functions
def extract_account_number(message):
    # Extract account number from message
    account_number_pattern = r'\b\d{10}\b'  # Example pattern for a 10-digit account number
    match = re.search(account_number_pattern, message)
    if match:
        return match.group(0)
    return None

def extract_mobile_number(message):
    # Extract mobile number from message
    mobile_number_pattern = r'\b(\+947\d{8}|07\d{8})\b'  # Example pattern for mobile number
    match = re.search(mobile_number_pattern, message)
    if match:
        return match.group(0)
    return None

def fetch_bill_details(account_number, mobile_number):
    # Validate account number and mobile number using CSV file
    with open('customer_data.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['account_number'] == account_number and row['mobile_number'] == mobile_number:
                return f"Account Number: {row['account_number']}, Bill Amount: {row['bill_amount']} {row['currency']}"
    return None

def update_chat_history(session, sender, message):
    if 'chat_history' not in session:
        session['chat_history'] = []
    session['chat_history'].append({'sender': sender, 'message': message})
    session.modified = True
