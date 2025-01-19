

from chatbot.utils.english.en_incident_reports import IncidentReportsTree
from ...models import TreeNode
from ..chat_histories import update_chat_history

import random
import re
from datetime import datetime
from typing import Optional, Dict, Any
import json



class Fault_and_Incident_ReportingTree_EN:
    def __init__(self):
        # Initialize root node for report type selection
        self.root = TreeNode('awaiting_report_type', self.awaiting_report_type)
        
        # Initialize nodes for fault reporting workflow
        self.awaiting_district_node = TreeNode('awaiting_district', self.awaiting_district)
        self.awaiting_town_node = TreeNode('awaiting_town', self.awaiting_town)
        self.awaiting_identifier_node = TreeNode('awaiting_identifier', self.awaiting_identifier)
        self.awaiting_fault_type_node = TreeNode('awaiting_fault_type', self.awaiting_fault_type)
        self.confirm_details_node = TreeNode('confirm_details', self.confirm_details)
        self.exit_node = TreeNode('exit', self.exit_request)

        # Initialize nodes for incident reporting workflow
        self.awaiting_incident_type_node = TreeNode('awaiting_incident_type', self.awaiting_incident_type)
        self.awaiting_severity_node = TreeNode('awaiting_severity', self.awaiting_severity)
        self.awaiting_details_node = TreeNode('awaiting_details', self.awaiting_details)
        self.confirm_incident_details_node = TreeNode('confirm_incident_details', self.confirm_incident_details)
        self.exit_incident_node = TreeNode('exit_incident', self.exit_incident_request)

        # Set up fault reporting workflow
        self.root.add_child('awaiting_district', self.awaiting_district_node)
        self.root.add_child('awaiting_incident_type', self.awaiting_incident_type_node)
        
        # Fault reporting path
        self.awaiting_district_node.add_child('awaiting_town', self.awaiting_town_node)
        self.awaiting_town_node.add_child('awaiting_identifier', self.awaiting_identifier_node)
        self.awaiting_identifier_node.add_child('awaiting_fault_type', self.awaiting_fault_type_node)
        self.awaiting_fault_type_node.add_child('confirm_details', self.confirm_details_node)
        self.confirm_details_node.add_child('exit', self.exit_node)

        # Incident reporting path
        self.awaiting_incident_type_node.add_child('awaiting_severity', self.awaiting_severity_node)
        self.awaiting_severity_node.add_child('awaiting_details', self.awaiting_details_node)
        self.awaiting_details_node.add_child('confirm_incident_details', self.confirm_incident_details_node)
        self.confirm_incident_details_node.add_child('exit_incident', self.exit_incident_node)

    def handle_state(self, user_message, session):
        try:
            # Handle global commands
            if 'exit' in user_message.lower():
                session['current_state'] = 'exit'
            if 'restart' in user_message.lower():
                return self.reset_reporting(session)
            if 'emergency' in user_message.lower():
                return self._handle_emergency()

            current_state = session.get('current_state', 'awaiting_report_type')
            current_node = self._find_node(self.root, current_state)
            return current_node.handle(user_message, session) if current_node else self.reset_reporting(session)

        except Exception as e:
            return "I apologize for the inconvenience. Please try again or contact our support team."

    def _find_node(self, current_node, state_name):
        if current_node.name == state_name:
            return current_node
        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def awaiting_report_type(self, user_message, session):
        report_type = user_message.lower().strip()
        if report_type in ['1', 'fault report', 'fault']:
            session['report_type'] = 'fault'
            session['current_state'] = 'awaiting_district'
            districts = ", ".join(get_districts()[:5]) + "..."
            response = f"Please provide a district name. Examples: {districts}"
        elif report_type in ['2', 'incident report', 'incident']:
            session['report_type'] = 'incident'
            session['current_state'] = 'awaiting_incident_type'
            response = self._get_incident_type_prompt()
        else:
            response = self._get_report_type_prompt()
        
        update_chat_history(session, "bot", response)
        return response

    def _get_report_type_prompt(self):
        return """
        <div>
            <p>What type of report would you like to submit?</p>
            <button class="language-button" onclick="sendMessage('Fault Report', this)">1. Fault Report</button>
            <button class="language-button" onclick="sendMessage('Incident Report', this)">2. Incident Report</button>
            <p>Please select the type of report or enter the corresponding number.</p>
        </div>
        """

    def awaiting_district(self, user_message, session):
        district = extract_district(user_message)
        if district:
            session['district'] = district
            session['current_state'] = 'awaiting_town'
            response = self._choose_response([
                f"District recorded: {district}. Please provide the nearest town.",
                f"Got it, {district}. Which town are you in?",
                f"Thank you. Now, what town in {district} is affected?"
            ])
        else:
            districts = ", ".join(get_districts()[:5]) + "..."
            response = f"Please provide a district name. Examples: {districts}"
        update_chat_history(session, "bot", response)
        return response

    def awaiting_town(self, user_message, session):
        town = extract_town(user_message)
        if town:
            session['town'] = town
            session['current_state'] = 'awaiting_identifier'
            response = ("Please provide \n"
                       " your account number or \n"
                       " your contact number \n\n"
                       "to proceed with the report.")
        else:
            response = f"Please provide a town name in {session.get('district', 'your district')}."
        update_chat_history(session, "bot", response)
        return response

    def awaiting_identifier(self, user_message, session):
        account_number = extract_account_number(user_message)
        contact_number = extract_contact(user_message)
        
        if account_number:
            session['identifier_type'] = 'account'
            session['identifier'] = account_number
            if session['report_type'] == 'fault':
                session['current_state'] = 'awaiting_fault_type'
                response = self._get_fault_type_prompt()
            else:
                session['current_state'] = 'awaiting_incident_type'
                response = self._get_incident_type_prompt()
        elif contact_number:
            session['identifier_type'] = 'contact'
            session['identifier'] = contact_number
            if session['report_type'] == 'fault':
                session['current_state'] = 'awaiting_fault_type'
                response = self._get_fault_type_prompt()
            else:
                session['current_state'] = 'awaiting_incident_type'
                response = self._get_incident_type_prompt()
        else:
            response = ("Please provide either:\n"
                       "- A valid account number (format: ACC123456)\n"
                       "- A valid contact number (format: 077-1234567)")
        
        update_chat_history(session, "bot", response)
        return response

    def awaiting_fault_type(self, user_message, session):
        fault_type = self._extract_fault_type(user_message)
        if fault_type:
            session['fault_type'] = fault_type
            session['current_state'] = 'confirm_details'
            response = self._generate_confirmation(session)
        else:
            response = self._get_fault_type_prompt()
        update_chat_history(session, "bot", response)
        return response

    def _get_fault_type_prompt(self):
        return """
        <div>
            <p>What type of fault are you experiencing?</p>
            <button class="language-button" onclick="sendMessage('Power failure', this)">1. Power failure</button>
            <button class="language-button" onclick="sendMessage('Voltage issue', this)">2. Voltage issue</button>
            <button class="language-button" onclick="sendMessage('Broken line', this)">3. Broken line</button>
            <button class="language-button" onclick="sendMessage('Transformer problem', this)">4. Transformer problem</button>
            <button class="language-button" onclick="sendMessage('Electric shock', this)">5. Electric shock</button>
            <button class="language-button" onclick="sendMessage('Other', this)">6. Other</button>
            <p>You can either type the fault type or enter the corresponding number.</p>
        </div>
        """

    def confirm_details(self, user_message, session):
        if 'yes' in user_message.lower() or 'correct' in user_message.lower():
            session['current_state'] = 'exit'
            return self._generate_summary(session)
        elif 'no' in user_message.lower():
            return self._handle_correction(session)
        return "Please confirm if the details are correct (yes/no)."

    def _generate_confirmation(self, session):
        identifier_type = "Account Number" if session.get('identifier_type') == 'account' else "Contact Number"
        return f"""
        <div>
            <p>Please confirm if these details are correct:</p>
            <p>District: {session.get('district')}</p>
            <p>Town: {session.get('town')}</p>
            <p>{identifier_type}: {session.get('identifier')}</p>
            <p>Fault Type: {session.get('fault_type')}</p>
            
            <button class="language-button" onclick="sendMessage('yes', this)">Yes</button>
            <button class="language-button" onclick="sendMessage('no', this)">No</button>
            
            <p>You can click a button or type 'yes' or 'no'.</p>
        </div>
        """

    def _generate_summary(self, session):
        identifier = session.get('identifier', '')
        ref_number = f"FR{datetime.now().strftime('%y%m%d')}{identifier[-4:]}"
        identifier_type = "Account Number" if session.get('identifier_type') == 'account' else "Contact Number"
        
        return (
            "===== FAULT REPORT SUMMARY =====\n"
            f"Reference: {ref_number}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"{identifier_type}: {session.get('identifier')}\n"
            f"Location: {session.get('district')}, {session.get('town')}\n"
            f"Fault Type: {session.get('fault_type')}\n"
            f"\nStatus: Your complaint has been registered.\n"
            f"We will inform the relevant authorities\n"
            f"for further action. Thank you!\n"
            f"We will contact you shortly with updates."
        )

    def exit_request(self, user_message, session):
        identifier = session.get('identifier', '')
        ref_number = f"FR{datetime.now().strftime('%y%m%d')}{identifier[-4:]}"
        response = (
            f"Thank you for reporting the fault. Your reference number is {ref_number}. "
            "Our team will contact you shortly with updates."
        )
        update_chat_history(session, "bot", response)
        session.clear()
        return response

    def reset_reporting(self, session):
        session['current_state'] = 'awaiting_report_type'
        session['chat_history'] = []
        response = self._get_report_type_prompt()
        update_chat_history(session, "bot", response)
        return response

    def _handle_correction(self, session):
        session['current_state'] = 'awaiting_report_type'
        return ("Let's start over to ensure accurate information. "
                "What type of report would you like to submit?")

    def _extract_fault_type(self, message):
        fault_keywords = {
            "power failure": ["no power", "electricity out", "blackout"],
            "voltage issue": ["fluctuation", "dim lights", "voltage drop"],
            "broken line": ["fallen wire", "damaged line", "wire down"],
            "transformer problem": ["transformer", "explosion", "loud bang"],
            "electric shock": ["shock", "current leak", "earthing"]
        }

        fault_type_mapping = {
            "1": "power failure",
            "2": "voltage issue",
            "3": "broken line",
            "4": "transformer problem",
            "5": "electric shock"
        }

        message = message.lower().strip()
        
        if message in fault_type_mapping:
            return fault_type_mapping[message]
        
        if message in fault_keywords:
            return message
            
        for fault, keywords in fault_keywords.items():
            if any(keyword in message for keyword in keywords):
                return fault
                
        return None

    def _choose_response(self, responses):
        return random.choice(responses)

    def _handle_emergency(self):
        return ("⚠️ EMERGENCY GUIDANCE ⚠️\n"
                "1. Stay away from any electrical equipment or wires\n"
                "2. Call emergency services immediately: 1987\n"
                "3. Keep others away from the danger area\n"
                "4. Do not attempt to handle electrical emergencies yourself\n"
                "5. Wait for professional help to arrive")

   
          
    
 # New incident reporting methods
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
            response = "Please provide additional details about the incident:\n\n"
            "** What happened?**\n"
            "** Are there any injuries?**\n"
            "** What is the current situation?**\n"
            "** Provide a contact number for follow-up.**"
        else:
            response = self._get_severity_prompt()
        update_chat_history(session, "bot", response)
        return response

    def awaiting_details(self, user_message, session):
        if len(user_message) > 10:  # Basic validation for details
            session['details'] = user_message
            session['current_state'] = 'confirm_incident_details'
            response = self._generate_incident_confirmation(session)
        else:
            response = "Please provide more detailed information about the incident."
        update_chat_history(session, "bot", response)
        return response

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
            <button class="language-button" onclick="sendMessage('Other Electrical Hazard', this)">7. Other Electrical Hazard</button>
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
        </div>
        """

    def _generate_incident_confirmation(self, session):
        identifier_type = "Account Number" if session.get('identifier_type') == 'account' else "Contact Number"
        identifier = session.get('identifier', '')
        
        return f"""
        <div>
            <p>Please confirm these incident details:</p>
            <p>{identifier_type}: {identifier}</p>
            <p>Location: {session.get('district')}, {session.get('town')}</p>
            <p>Incident Type: {session.get('incident_type')}</p>
            <p>Severity: {session.get('severity')}</p>
            <p>Details: {session.get('details')}</p>
            
            <button class="language-button" onclick="sendMessage('yes', this)">Yes - Confirm these details</button>
            <button class="language-button" onclick="sendMessage('no', this)">No - Make corrections</button>
            
            <p>You can click a button or type 'yes' or 'no'.</p>
        </div>
        """

    def confirm_incident_details(self, user_message, session):
        if 'yes' in user_message.lower() or 'correct' in user_message.lower():
            session['current_state'] = 'exit_incident'
            return self._generate_incident_summary(session)
        elif 'no' in user_message.lower():
            return self._handle_incident_correction(session)
        return "Please confirm if the details are correct (yes/no)."

    def _generate_incident_summary(self, session):
        incident_ref = self._generate_incident_reference(session)
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        identifier_type = "Account Number" if session.get('identifier_type') == 'account' else "Contact Number"
        
        return (
            f"===== INCIDENT REPORT ======\n"
            f"Reference: {incident_ref}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"{identifier_type}: {session.get('identifier')}\n"
            f"Location: {session.get('district')}, {session.get('town')}\n"
            f"Type: {session.get('incident_type')}\n"
            f"Severity: {severity_emoji.get(session.get('severity', 'low'), '⚪')} {session.get('severity')}\n"
            f"Details: {session.get('details')}\n"
            f"\nOur team has been notified and will respond according to severity.\n"
            f"For emergencies, call: 1987\n"
            f"You will receive updates via SMS."
        )

    def _generate_incident_reference(self, session):
        timestamp = datetime.now().strftime('%y%m%d%H%M')
        severity_code = {'critical': 'C', 'high': 'H', 'medium': 'M', 'low': 'L'}
        sev = severity_code.get(session.get('severity', 'low'), 'X')
        return f"INC{timestamp}{sev}"

    def _handle_emergency(self):
        return ("⚠️ EMERGENCY GUIDANCE ⚠️\n"
                "1. Stay away from any electrical equipment or wires\n"
                "2. Call emergency services immediately: 1987\n"
                "3. Keep others away from the danger area\n"
                "4. Do not attempt to handle electrical emergencies yourself\n"
                "5. Wait for professional help to arrive")

    def exit_incident_request(self, user_message, session):
        response = "Thank you for reporting the incident. Our team will contact you shortly with updates."
        update_chat_history(session, "bot", response)
        session.clear()
        return response

    def _handle_incident_correction(self, session):
        session['current_state'] = 'awaiting_incident_type'
        return "Let's revise your incident report. What type of incident are you reporting?"

    def _extract_incident_type(self, message):
        incident_types = {
            "1": "Electrical Fire",
            "2": "Fallen Power Line",
            "3": "Transformer Explosion",
            "4": "Electrical Shock",
            "5": "Equipment Failure",
            "6": "Power Surge Damage",
            "7": "Other Electrical Hazard"
        }
        message = message.lower().strip()
        
        # Check for number input
        if message in incident_types:
            return incident_types[message]
            
        # Check for text input
        for incident_type in incident_types.values():
            if incident_type.lower() in message:
                return incident_type
                
        return None

    def _extract_severity(self, message):
        severity_levels = {
            "1": "critical",
            "2": "high",
            "3": "medium",
            "4": "low"
        }
        message = message.lower().strip()
        
        # Check for number input
        if message in severity_levels:
            return severity_levels[message]
            
        # Check for text input
        if any(level in message for level in ["critical", "high", "medium", "low"]):
            for level in ["critical", "high", "medium", "low"]:
                if level in message:
                    return level
                    
        return None

# Utility functions
def get_districts():
    return [
        "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya",
        "Galle", "Matara", "Hambantota", "Jaffna", "Kilinochchi", "Mannar",
        "Vavuniya", "Mullaitivu", "Batticaloa", "Ampara", "Trincomalee",
        "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla",
        "Monaragala", "Ratnapura", "Kegalle"
    ]

def extract_district(message):
    districts = get_districts()
    for district in districts:
        if district.lower() in message.lower():
            return district
    return None

def extract_town(message):
    towns = ["Hindagala", "Peradeniya", "Kandy", "Gampola", "Kolonnawa", "Wellampitiya", 
             "Gothatuwa", "Orugodawatta", "Dematagoda", "Grandpass", "Mattakkuliya", 
             "Modara", "Bloemendhal", "Kotahena", "Fort", "Pettah", "Maradana", 
             "Slave Island", "Borella", "Cinnamon Gardens", "Thimbirigasyaya", 
             "Havelock Town", "Kirulapone", "Narahenpita", "Pamankada", "Wellawatte",
             "Bambalapitiya", "Kollupitiya", "Dehiwala", "Mount Lavinia", "Ratmalana",
             "Moratuwa", "Panadura"]
    for town in towns:
        if town.lower() in message.lower():
            return town
    return None

def extract_contact(message):
    pattern = r'(?:0|94)?(?:(11|21|23|24|25|26|27|31|32|33|34|35|36|37|38|41|45|47|51|52|54|55|57|63|65|66|67|81|91)(0|2|3|4|5|7|9)|7(0|1|2|4|5|6|7|8)\d)\d{6}'
    match = re.search(pattern, message.replace(" ", ""))
    return match.group(0) if match else None

def extract_account_number(message):
    # Account number format: ACC followed by 6 digits
    pattern = r'ACC\d{6}'
    match = re.search(pattern, message.upper().replace(" ", ""))
    return match.group(0) if match else None

def load_towns_from_json(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            towns = json.load(file)
        return towns
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return []  
    


