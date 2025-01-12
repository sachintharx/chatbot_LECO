"""from ...models import TreeNode
from .en_connectionRequest import update_chat_history

# Main handler for incident reports
def handle_incident_reports(user_message, session):
    incident_tree = IncidentReportsTree()
    return incident_tree.handle_state(user_message, session)

class IncidentReportsTree:
    def __init__(self):
        self.root = TreeNode('awaiting_incident_location', self.awaiting_incident_location)
        self.exit_node = TreeNode('exit', self.exit_request)
        self.root.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'
        current_state = session.get('current_state', 'awaiting_incident_location')
        current_node = self._find_node(self.root, current_state)
        if current_node:
            response = current_node.handle(user_message, session)
            return response
        else:
            return self.reset_incident_reports(session)

    def _find_node(self, current_node, state_name):
        if current_node.name == state_name:
            return current_node
        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def awaiting_incident_location(self, user_message, session):
        session['incident_location'] = user_message
        session['current_state'] = 'exit'
        response = "Thank you for reporting the incident. Our team will look into it and get back to you shortly."
        update_chat_history(session, "bot", response)
        return response

    def exit_request(self, user_message, session):
        response = "Thank you for using our service. If you need further assistance, feel free to ask!"
        update_chat_history(session, "bot", response)
        session.clear()
        return response

    def reset_incident_reports(self, session):
        session['current_state'] = 'awaiting_incident_location'
        session['chat_history'] = []
        response = "Can you provide the location of the incident?"
        update_chat_history(session, "bot", response)
        return response """

########################################################3\

from datetime import datetime
from typing import Optional, Dict, Any
from ..chat_histories import update_chat_history
from ...models import TreeNode
import random
import re
import json

def handle_incident_reports(user_message, session):
    
    incident_tree = IncidentReportsTree()
    return incident_tree.handle_state(user_message, session)

class IncidentReportsTree:
    def __init__(self):
        # Initialize nodes
        self.root = TreeNode('awaiting_location', self.awaiting_location)
        self.awaiting_incident_type_node = TreeNode('awaiting_incident_type', self.awaiting_incident_type)
        self.awaiting_severity_node = TreeNode('awaiting_severity', self.awaiting_severity)
        self.awaiting_details_node = TreeNode('awaiting_details', self.awaiting_details)
        self.awaiting_contact_node = TreeNode('awaiting_contact', self.awaiting_contact)
        self.confirm_details_node = TreeNode('confirm_details', self.confirm_details)
        self.exit_node = TreeNode('exit', self.exit_request)

        # Set up workflow
        self.root.add_child('awaiting_incident_type', self.awaiting_incident_type_node)
        self.awaiting_incident_type_node.add_child('awaiting_severity', self.awaiting_severity_node)
        self.awaiting_severity_node.add_child('awaiting_details', self.awaiting_details_node)
        self.awaiting_details_node.add_child('awaiting_contact', self.awaiting_contact_node)
        self.awaiting_contact_node.add_child('confirm_details', self.confirm_details_node)
        self.confirm_details_node.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        try:
            # Handle global commands
            if 'emergency' in user_message.lower():
                return self._handle_emergency()
            if 'exit' in user_message.lower():
                session['current_state'] = 'exit'
            if 'restart' in user_message.lower():
                return self.reset_incident_reporting(session)

            current_state = session.get('current_state', 'awaiting_location')
            current_node = self._find_node(self.root, current_state)
            return current_node.handle(user_message, session) if current_node else self.reset_incident_reporting(session)

        except Exception as e:
            return "For your safety, please contact emergency services immediately at 1987 if this is a life-threatening situation."

    def _find_node(self, current_node, state_name):
        if current_node.name == state_name:
            return current_node
        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def awaiting_location(self, user_message, session):
        location = extract_location(user_message)
        if location:
            session['location'] = location
            session['current_state'] = 'awaiting_incident_type'
            response = self._get_incident_type_prompt()
        else:
            response = ("Please provide the exact location of the incident.\n"
                       "Include street name, nearby landmarks, and area/district.")
        update_chat_history(session, "bot", response)
        return response

    def awaiting_incident_type(self, user_message, session):
        incident_type = self._extract_incident_type(user_message)
        if incident_type:
            session['incident_type'] = incident_type
            session['current_state'] = 'awaiting_severity'
            response = self._get_severity_prompt()
        else:
            response = self._get_incident_type_prompt()
        update_chat_history(session, "bot", response)
        return response

    def awaiting_severity(self, user_message, session):
        severity = self._extract_severity(user_message)
        if severity:
            session['severity'] = severity
            session['current_state'] = 'awaiting_details'
            response = ("Please provide additional details about the incident:\n"
                       "- What happened?\n"
                       "- Are there any injuries?\n"
                       "- Is there immediate danger?\n"
                       "- What is the current situation?")
        else:
            response = self._get_severity_prompt()
        update_chat_history(session, "bot", response)
        return response

    def awaiting_details(self, user_message, session):
        if len(user_message) > 10:  # Basic validation for details
            session['details'] = user_message
            session['current_state'] = 'awaiting_contact'
            response = ("Please provide your contact information:\n"
                       "- Contact number (required)\n"
                       "- Name (optional)\n"
                       "- Email (optional)")
        else:
            response = "Please provide more detailed information about the incident."
        update_chat_history(session, "bot", response)
        return response

    def awaiting_contact(self, user_message, session):
        contact_info = extract_contact_info(user_message)
        if contact_info.get('phone'):
            session['contact_info'] = contact_info
            session['current_state'] = 'confirm_details'
            response = self._generate_confirmation(session)
        else:
            response = "Please provide at least a valid contact number (format: 077-1234567)."
        update_chat_history(session, "bot", response)
        return response

    def confirm_details(self, user_message, session):
        if 'yes' in user_message.lower() or 'correct' in user_message.lower():
            session['current_state'] = 'exit'
            return self._generate_summary(session)
        elif 'no' in user_message.lower():
            return self._handle_correction(session)
        return "Please confirm if the details are correct (yes/no)."

    def exit_request(self, user_message, session):
        incident_ref = self._generate_incident_reference(session)
        response = (
            f"Your incident has been reported. Reference number: {incident_ref}\n"
            "Our emergency response team has been notified and will respond based on severity.\n"
            "For immediate assistance, contact our 24/7 hotline: 1987"
        )
        update_chat_history(session, "bot", response)
        session.clear()
        return response

    def _handle_emergency(self):
        return ("⚠️ EMERGENCY GUIDANCE ⚠️\n"
                "1. Stay away from any electrical equipment or wires\n"
                "2. Call emergency services immediately: 1987\n"
                "3. Keep others away from the danger area\n"
                "4. Do not attempt to handle electrical emergencies yourself\n"
                "5. Wait for professional help to arrive")

    def _extract_incident_type(self, message):
        incident_types = {
            "1": "electrical fire",
            "2": "fallen power line",
            "3": "transformer explosion",
            "4": "electrical shock",
            "5": "equipment failure",
            "6": "power surge damage",
            "7": "other electrical hazard"
        }
        
        message = message.strip()
        if message in incident_types:
            return incident_types[message]
            
        message = message.lower()
        for incident_type in incident_types.values():
            if incident_type in message:
                return incident_type
        return None

    def _extract_severity(self, message):
        severity_levels = {
            "1": "critical",
            "2": "high",
            "3": "medium",
            "4": "low"
        }
        
        message = message.strip()
        if message in severity_levels:
            return severity_levels[message]
            
        message = message.lower()
        for level in severity_levels.values():
            if level in message:
                return level
        return None

    def _get_incident_type_prompt(self):
       return """
        <div>
            <p>What type of electrical incident are you reporting?</p>
            <button class="language-button" onclick="sendMessage('Electrical Fire', this)">1. Electrical Fire</button>
            <button class="language-button" onclick="sendMessage('Fallen Power Line', this)">2. Fallen Power Line</button>
            <button class="language-button" onclick="sendMessage('Transformer Explosion', this)">3. Transformer Explosion</button>
            <button class="language-button" onclick="sendMessage('Electrical Shock', this)">4. Electrical Shock</button>
            <button class="language-button" onclick="sendMessage('Equipment Failure', this)">5. Equipment Failure</button>
            <button class="language-button" onclick="sendMessage('Power Surge Damage', this)">6. Power Surge Damage</button>
            <button class="language-button" onclick="sendMessage(' Other Electrical Hazard', this)">7. Other Electrical Hazard</button>
            <p>You can click a button or type the incident type.</p>
        </div>
    """
    def _get_severity_prompt(self):
        return """
        <div>
            <p>Please rate the severity of the incident:</p>
            <button class="language-button" onclick="sendMessage('Critical', this)">1. Critical - Life-threatening situation</button>
            <button class="language-button" onclick="sendMessage('High', this)">2. High - Serious hazard </button>
            <button class="language-button" onclick="sendMessage('Medium', this)">3. Medium - Potential risk </button>
            <button class="language-button" onclick="sendMessage('Low', this)">4. Low - No immediate danger</button>
            <p>You can click a button or type the severity level.</p>
        </div>"""

    def _generate_confirmation(self, session):
       return f"""
    <div>
        <p>Please confirm these incident details:</p>
        <p>Location: {session.get('location')}</p>
        <p>Incident Type: {session.get('incident_type')}</p>
        <p>Severity: {session.get('severity')}</p>
        <p>Details: {session.get('details')}</p>
        <p>Contact: {session.get('contact_info', {}).get('phone')}</p>
        
        <button class="language-button" onclick="sendMessage('yes', this)">Yes - Confirm these details</button>
        <button class="language-button" onclick="sendMessage('no', this)">No - Make corrections</button>
        
        <p>You can click a button or type 'yes' or 'no'.</p>
    </div>
    """
    def _handle_correction(self, session):
        session['current_state'] = 'awaiting_location'
        response = "Let's correct the details. Please provide the location of the incident."
        update_chat_history(session, "bot", response)
        return response

    def _generate_summary(self, session):
        incident_ref = self._generate_incident_reference(session)
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        return (
            f"===== INCIDENT REPORT ======\n"
            f"Reference: {incident_ref}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Location: {session.get('location')}\n"
            f"Type: {session.get('incident_type')}\n"
            f"Severity: {severity_emoji.get(session.get('severity', 'low'), '⚪')} {session.get('severity')}\n"
            f"Details: {session.get('details')}\n"
            f"Contact: {session.get('contact_info', {}).get('phone')}\n"
          
            f"Our team has been notified and will respond according to severity.\n"
            f"For emergencies, call: 1987\n"
            f"You will receive updates via SMS."
        )

    def _generate_incident_reference(self, session):
        timestamp = datetime.now().strftime('%y%m%d%H%M')
        severity_code = {'critical': 'C', 'high': 'H', 'medium': 'M', 'low': 'L'}
        sev = severity_code.get(session.get('severity', 'low'), 'X')
        return f"INC{timestamp}{sev}"

    def reset_incident_reporting(self, session):
        session['current_state'] = 'awaiting_location'
        session['chat_history'] = []
        response = ("Please provide the location of the electrical incident.\n"
                   "Include street name and nearby landmarks for accurate response.")
        update_chat_history(session, "bot", response)
        return response

def extract_location(message):
    # Basic location validation - requires at least 5 characters
    return message.strip() if len(message.strip()) >= 5 else None

def extract_contact_info(message):
    contact_info = {} 
    
    # Extract phone number
    phone_pattern = r'(?:0|94)?(?:(11|21|23|24|25|26|27|31|32|33|34|35|36|37|38|41|45|47|51|52|54|55|57|63|65|66|67|81|91)(0|2|3|4|5|7|9)|7(0|1|2|4|5|6|7|8)\d)\d{6}'
    phone_match = re.search(phone_pattern, message.replace(" ", ""))
    if phone_match:
        contact_info['phone'] = phone_match.group(0)
    
    # Extract email (optional)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, message)
    if email_match:
        contact_info['email'] = email_match.group(0)
    
    # Extract name (optional) - basic implementation
    name_pattern = r'(?:name[:\s]+)([a-zA-Z\s]+)'
    name_match = re.search(name_pattern, message, re.IGNORECASE)
    if name_match:
        contact_info['name'] = name_match.group(1).strip()
    
    return contact_info