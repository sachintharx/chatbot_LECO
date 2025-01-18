from ..chat_histories import update_chat_history
import random
import re
from datetime import datetime
import requests
# from chatbot.models import TreeNode

class TreeNode:
    def __init__(self, state, handler):
        self.state = state
        self.handler = handler
        self.children = {}

    def add_child(self, state, node):
        self.children[state] = node

    def handle(self, user_message, session):
        return self.handler(user_message, session)

class BillInquiriesTree_EN:
    def __init__(self):
        # Initialize root node for service selection
        self.root = TreeNode('service_selection', self.service_selection)
        
        # Bill Balance Check nodes
        self.verification_node = TreeNode('verification', self.verification)
        self.awaiting_verification_input_node = TreeNode('awaiting_verification_input', self.awaiting_verification_input)
        self.contact_verification_node = TreeNode('contact_verification', self.contact_verification)
        self.display_balance_node = TreeNode('display_balance', self.display_balance)
        self.make_payment_node = TreeNode('make_payment', self.make_payment)
        
        # Bill Dispute nodes
        self.dispute_reason_node = TreeNode('dispute_reason', self.dispute_reason)
        self.agent_transfer_node = TreeNode('agent_transfer', self.agent_transfer)
        
        # Exit node
        self.exit_node = TreeNode('exit', self.exit_request)

        # Set up node transitions for Bill Balance path
        self.root.add_child('verification', self.verification_node)
        self.verification_node.add_child('awaiting_verification_input', self.awaiting_verification_input_node)
        self.awaiting_verification_input_node.add_child('contact_verification', self.contact_verification_node)
        self.contact_verification_node.add_child('display_balance', self.display_balance_node)
        self.display_balance_node.add_child('make_payment', self.make_payment_node)
        self.display_balance_node.add_child('exit', self.exit_node)
        
        # Set up node transitions for Bill Dispute path
        self.root.add_child('dispute_reason', self.dispute_reason_node)
        self.dispute_reason_node.add_child('agent_transfer', self.agent_transfer_node)
        self.agent_transfer_node.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'
            
        current_state = session.get('current_state', 'service_selection')
        current_node = self._find_node(self.root, current_state)
        
        if current_node:
            return current_node.handle(user_message, session)
        return self.reset_bill_inquiries(session)
    
    def reset_bill_inquiries(self, session):
        session['current_state'] = 'service_selection'
        response = "Let's start over. Please select a service option."
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def _find_node(self, node, state):
        if node.state == state:
            return node
        for child in node.children.values():
            result = self._find_node(child, state)
            if result:
                return result
        return None

    def service_selection(self, user_message, session):
        if user_message.strip() == 'Bill Balance Check' or 'balance' in user_message.lower():
            session['service_type'] = 'balance'
            session['current_state'] = 'verification'
            response = (
                "You've selected Bill Balance Check.\n\n"
                "Please provide your 10-digit account number:"
            )
        elif user_message.strip() == 'Bill Dispute' or 'dispute' in user_message.lower():
            session['service_type'] = 'dispute'
            session['current_state'] = 'dispute_reason'
            response = (
                "You've selected Bill Dispute.\n\n"
                "Please select the reason for your dispute:\n"
                "1. Incorrect Charges\n"
                "2. Overcharge\n"
                "3. Other"
            )
        else:
            return """
                <div>
                    <p>Please select an option:</p>
                    <button class="language-button" onclick="sendMessage('Bill Balance Check', this)">Bill Balance Check</button>
                    <button class="language-button" onclick="sendMessage('Bill Dispute', this)">Bill Dispute</button>
                </div>
            """
        
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def verification(self, user_message, session):
        session['current_state'] = 'awaiting_verification_input'
        response = "Please provide your 10-digit account number:"
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def awaiting_verification_input(self, user_message, session):
        account_number = extract_account_number(user_message)
        
        if account_number:
            # Validate account number exists
            account_validation_response = self.validate_account_number_with_api(account_number)
            if account_validation_response.get('valid', False):
                session['identifier'] = account_number
                session['balance'] = account_validation_response.get('balance', 0.0)
                session['current_state'] = 'contact_verification'
                response = "Please provide your registered contact number:"
            else:
                response = "Invalid account number. Please provide a valid 10-digit account number."
                session['current_state'] = 'verification'
        else:
            response = "Please provide a valid 10-digit account number."
        
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def contact_verification(self, user_message, session):
        contact_number = extract_mobile_number(user_message)
        
        if not contact_number:
            response = "Please provide a valid contact number."
            update_chat_history(session, "bot", response)
            return self._split_message(response)

        # Validate contact number with API
        contact_validation_response = self.validate_contact_number_with_api(contact_number)
        retrieved_account = contact_validation_response.get('account_number')
        stored_account = session.get('identifier')

        if retrieved_account and retrieved_account == stored_account:
            session['contact_number'] = contact_number
            session['current_state'] = 'display_balance'
            return self.display_balance(user_message, session)
        else:
            response = "The provided contact number doesn't match with the account records. Please try again."
            session['current_state'] = 'contact_verification'
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def validate_account_number_with_api(self, account_number):
        try:
            response = requests.get(f"http://124.43.163.177:8080/CCLECO/Main/GetAccountBalance?accountNumber={account_number}")
            if response.status_code == 200:
                data = response.text.split(',')
                if data[0] == "YES":
                    return {'valid': True, 'balance': float(data[1])}
        except (requests.exceptions.RequestException, IndexError, ValueError):
            pass
        return {'valid': False}

    def validate_contact_number_with_api(self, contact_number):
        try:
            response = requests.get(f"http://124.43.163.177:8080/CCLECO/Main/GetAccountNumber?contactNumber={contact_number}")
            if response.status_code == 200:
                data = response.text.strip()
                return {'account_number': data}
        except (requests.exceptions.RequestException, IndexError):
            pass
        return {'account_number': None}

    def display_balance(self, user_message, session):
        identifier = session.get('identifier')
        balance = session.get('balance')
        contact_number = session.get('contact_number')
        
        if balance is not None:
            response = (
                "<div style='font-family: Arial, sans-serif; font-size: 12px;'>"
                "<h3 style='font-size: 12px;'>Bill Balance Details</h3>"
                f"<p><strong>Account Number:</strong> {identifier}</p>"
                f"<p><strong>Registered Contact Number:</strong> {contact_number}</p>"
                f"<p><strong>Current Balance:</strong> Rs. {balance:.2f}</p>"
                "<h3 style='font-size: 12px;'>What would you like to do next?</h3>"
                "<button class='language-button' onclick=\"sendMessage('make_payment', this)\" style='font-size: 12px;'>Make a payment</button>"
                "<button class='language-button' onclick=\"sendMessage('exit', this)\" style='font-size: 12px;'>Exit</button>"
                "</div>"
            )

        else:
            response = (
                f"Sorry, we couldn't find any bill information for account {identifier}.\n"
                f"Please verify your account number or contact customer support."
            )
        
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def make_payment(self, user_message, session):
        identifier = session.get('identifier')
        contact_number = session.get('contact_number')
        payment_url = f"https://lecoapp.leco.lk:9442/BillPay/account={identifier}&contact={contact_number}"
        response = f"Please proceed to the following link to make your payment: <a href='{payment_url}' target='_blank'>{payment_url}</a>"
        
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def dispute_reason(self, user_message, session):
        if user_message in ['1', '2', '3']:
            session['current_state'] = 'agent_transfer'
            response = (
                "Thank you for providing the reason.\n\n"
                "We are transferring you to our customer service agent who will assist you with your dispute.\n"
                "Please wait while we connect you."
            )
        else:
            response = (
                "Please select a valid reason for your dispute:\n"
                "1. Incorrect Charges\n"
                "2. Overcharge\n"
                "3. Other"
            )
        
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def agent_transfer(self, user_message, session):
        response = (
            "Our customer service agent will be with you shortly.\n"
            "Your session ID is: " + str(random.randint(10000, 99999)) + "\n"
            "Please keep this ID handy for reference."
        )
        session['current_state'] = 'exit'
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def exit_request(self, user_message, session):
        response = "Thank you for using our service. Have a great day!"
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def _split_message(self, message):
        return message.split("\n\n")

def extract_account_number(message):
    match = re.search(r'\b\d{10}\b', message)
    return match.group() if match else None

def extract_mobile_number(message):
    # Remove any spaces or special characters
    cleaned_message = re.sub(r'[^0-9]', '', message)
    # Look for a 10-digit number
    match = re.search(r'\b\d{10}\b', cleaned_message)
    return match.group() if match else None

def extract_payment_amount(message):
    match = re.search(r'\d+(\.\d{2})?', message)
    return float(match.group()) if match else None