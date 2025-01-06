
from ...models import TreeNode
import random
import re
from datetime import datetime
import pandas as pd


   

class BillInquiriesTree_EN:
    def __init__(self):
        # Initialize root node for service selection
        self.root = TreeNode('service_selection', self.service_selection)
        
        # Verification nodes
        self.verification_node = TreeNode('verification', self.verification)
        self.awaiting_verification_input_node = TreeNode('awaiting_verification_input', self.awaiting_verification_input)
        
        # Bill Balance Check nodes
        self.display_balance_node = TreeNode('display_balance', self.display_balance)
        
        # Bill Dispute nodes
        self.dispute_reason_node = TreeNode('dispute_reason', self.dispute_reason)
        self.agent_transfer_node = TreeNode('agent_transfer', self.agent_transfer)
        
        # Payment nodes
        self.make_payment_node = TreeNode('make_payment', self.make_payment)
        self.payment_confirmation_node = TreeNode('payment_confirmation', self.payment_confirmation)
        self.payment_history_node = TreeNode('payment_history', self.payment_history)
        
        # Exit node
        self.exit_node = TreeNode('exit', self.exit_request)

        # Set up node transitions
        self.root.add_child('verification', self.verification_node)
        self.verification_node.add_child('awaiting_verification_input', self.awaiting_verification_input_node)
        self.awaiting_verification_input_node.add_child('display_balance', self.display_balance_node)
        self.awaiting_verification_input_node.add_child('dispute_reason', self.dispute_reason_node)
        self.dispute_reason_node.add_child('agent_transfer', self.agent_transfer_node)
        self.display_balance_node.add_child('make_payment', self.make_payment_node)
        self.display_balance_node.add_child('payment_history', self.payment_history_node)
        self.display_balance_node.add_child('exit', self.exit_node)
        self.make_payment_node.add_child('payment_confirmation', self.payment_confirmation_node)
        self.payment_confirmation_node.add_child('exit', self.exit_node)
        self.payment_history_node.add_child('exit', self.exit_node)
        self.agent_transfer_node.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'
            
        current_state = session.get('current_state', 'service_selection')
        current_node = self._find_node(self.root, current_state)
        
        if current_node:
            return current_node.handle(user_message, session)
        return self.reset_bill_inquiries(session)

    def service_selection(self, user_message, session):
        # Handle numeric input
        if user_message.strip() == 'Bill Balance Check' or 'balance' in user_message.lower():
            session['service_type'] = 'balance'
            session['current_state'] = 'verification'
            response = (
                "You've selected Bill Balance Check.\n\n"
                "Please provide your 10-digit account number or registered mobile number:"
            )
        elif user_message.strip() == 'Bill Dispute' or 'dispute' in user_message.lower():
            session['service_type'] = 'dispute'
            session['current_state'] = 'verification'
            response = (
                "You've selected Bill Dispute.\n\n"
                "Please provide your 10-digit account number or registered mobile number:"
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
        service_type = "bill balance check" if session.get('service_type') == 'balance' else "bill dispute"
        response = f"To proceed with your {service_type}, please provide your 10-digit account number or registered mobile number:"
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def awaiting_verification_input(self, user_message, session):
        account_number = extract_account_number(user_message)
        mobile_number = extract_mobile_number(user_message)
        
        if account_number or mobile_number:
            session['identifier'] = account_number if account_number else mobile_number
            if session.get('service_type') == 'balance':
                session['current_state'] = 'display_balance'
                return self.display_balance(user_message, session)
            else:
                session['current_state'] = 'dispute_reason'
                return self.dispute_reason(user_message, session)
        
        response = "Please provide a valid 10-digit account number or registered mobile number."
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def fetch_bill_balance(self, identifier):
        # Mock database of bill balances
        mock_database = {
            '1234567890': 1234.56,
            '9876543210': 789.01,
            '5555555555': 2468.10,
            '9999999999': 135.79
        }
        return mock_database.get(identifier)

    def display_balance(self, user_message, session):
        if user_message and user_message.strip() in ['1', '2', '3']:
            return self.handle_balance_menu(user_message.strip(), session)
            
        identifier = session.get('identifier')
        if not identifier:
            response = "Sorry, we couldn't find your account information. Please try again."
            session['current_state'] = 'verification'
        else:
            balance = self.fetch_bill_balance(identifier)
            
            if balance is not None:
                response = (
                    "=== Bill Balance Details ===\n\n"
                    f"Account Number: {identifier}\n"
                    f"Current Balance: Rs. {balance:.2f}\n\n"
                    "What would you like to do next?\n"
                )
                response += """
                <div>
                    <p>Please select an option:</p>
                    <button class="language-button" onclick="sendMessage('1', this)">Make a payment</button>
                    <button class="language-button" onclick="sendMessage('2', this)">View payment history</button>
                    <button class="language-button" onclick="sendMessage('3', this)">Exit</button>
                </div>
                """
                session['balance'] = balance
            else:
                response = (
                    f"Sorry, we couldn't find any bill information for account {identifier}.\n"
                    f"Please verify your account number or contact customer support."
                )
        
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def handle_balance_menu(self, choice, session):
        if choice == '1':
            session['current_state'] = 'make_payment'
            return self.make_payment(None, session)
        elif choice == '2':
            session['current_state'] = 'payment_history'
            return self.payment_history(None, session)
        elif choice == '3':
            session['current_state'] = 'exit'
            return self.exit_request(None, session)
        
        return self.display_balance(None, session)

    def make_payment(self, user_message, session):
        balance = session.get('balance', 0)
        response = (
            f"=== Make Payment ===\n\n"
            f"Current Balance: Rs. {balance:.2f}\n\n"
            f"Please enter the amount you would like to pay: "
        )
        session['current_state'] = 'payment_confirmation'
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def payment_confirmation(self, user_message, session):
        try:
            amount = float(user_message.replace('Rs. ', '').strip())
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            payment_id = generate_payment_id()
            session['payment_id'] = payment_id
            
            response = (
                f"=== Payment Confirmation ===\n\n"
                f"Payment Amount: Rs. {amount:.2f}\n"
                f"Payment ID: {payment_id}\n"
                f"Status: Processing\n\n"
                f"Your payment is being processed. Please allow 24-48 hours for it to be reflected in your account.\n"
                f"Save your Payment ID for your records.\n\n"
                f"Thank you for your payment. Is there anything else we can help you with?"
            )
            session['current_state'] = 'exit'
            
        except ValueError:
            response = (
                f"Invalid amount. Please enter a valid number.\n"
                f"Example: 50.00"
            )
            session['current_state'] = 'make_payment'
            
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def payment_history(self, user_message, session):
        identifier = session.get('identifier')
        history = self.fetch_payment_history(identifier)
        
        if history:
            response = (
                f"=== Payment History ===\n\n"
                f"Account Number: {identifier}\n\n"
                f"Recent Transactions:\n"
            )
            
            for payment in history:
                response += (
                    f"Date: {payment['date']}\n"
                    f"Amount: Rs.{payment['amount']:.2f}\n"
                    f"Status: {payment['status']}\n"
                    f"Payment ID: {payment['payment_id']}\n\n"
                )
                
            response += "Would you like to make a payment?"
            response += """
                <div>
                    <p>Please select an option:</p>
                    <button class="language-button" onclick="sendMessage('1', this)">Yes</button>
                    
                    <button class="language-button" onclick="sendMessage('3', this)">Exit</button>
                </div>
                """
        else:
            response = (
                f"No payment history found for account {identifier}.\n\n"
                f"Would you like to make a payment? (Enter '1' for Yes or '3' to Exit)"
            )
            
        session['current_state'] = 'display_balance'
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def fetch_payment_history(self, identifier):
        # Mock payment history data
        mock_history = {
            '1234567890': [
                {
                    'date': '2024-12-20',
                    'amount': 100.00,
                    'status': 'Completed',
                    'payment_id': 'PAY20241220001'
                },
                {
                    'date': '2024-11-15',
                    'amount': 150.00,
                    'status': 'Completed',
                    'payment_id': 'PAY20241115001'
                }
            ]
        }
        return mock_history.get(identifier, [])

    def dispute_reason(self, user_message, session):
        if 'reason' in session:
            session['current_state'] = 'agent_transfer'
            return self.agent_transfer(user_message, session)
            
        session['reason'] = user_message
        response = (
            "Please briefly describe the reason for your dispute:\n"
            "(For example: incorrect charges, unauthorized transaction, etc.)"
        )
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def agent_transfer(self, user_message, session):
        case_number = generate_case_number()
        session['case_number'] = case_number
        response = (
            f"=== Bill Dispute Case Created ===\n\n"
            f"Account Number: {session.get('identifier')}\n"
            f"Case Number: #{case_number}\n"
            f"Status: Pending Agent Review\n\n"
            f"We have logged your dispute. A customer service agent will contact you within 24 hours.\n"
            f"Please keep your case number for reference.\n\n"
            f"Is there anything else we can help you with?"
        )
        session['current_state'] = 'exit'
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def exit_request(self, user_message, session):
        response = (
            "Thank you for using our Bill Management System.\n"
            "If you need further assistance, please don't hesitate to contact us.\n"
            "Have a great day!"
        )
        update_chat_history(session, "bot", response)
        session.clear()
        return self._split_message(response)

    def reset_bill_inquiries(self, session):
        session['current_state'] = 'service_selection'
        session['chat_history'] = []
        response = (
            "Welcome to the Bill Management System!\n\n"
            "Please select a service by entering the corresponding number:\n"
            "1. Check Bill Balance\n"
            "2. Report Bill Dispute"
        )
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def _find_node(self, current_node, state_name):
        if current_node.name == state_name:
            return current_node
        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def _split_message(self, message, max_length=160):
        if len(message) <= max_length:
            return message
        return [message[i:i+max_length] for i in range(0, len(message), max_length)]

def extract_account_number(message):
    account_number_pattern = r'\b\d{10}\b'
    match = re.search(account_number_pattern, message)
    return match.group(0) if match else None

def extract_mobile_number(message):
    mobile_pattern = r'\b\d{10}\b'  # Assuming 10-digit mobile numbers
    match = re.search(mobile_pattern, message)
    return match.group(0) if match else None

def generate_case_number():
    return f"DISP{datetime.now().strftime('%Y%m%d%H%M%S')}"

def generate_payment_id():
    return f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}"

def update_chat_history(session, sender, message):
    if 'chat_history' not in session:
        session['chat_history'] = []
    session['chat_history'].append({'sender': sender, 'message': message})
    session.modified = True