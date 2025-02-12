
from ...models import TreeNode
from ..chat_histories import update_chat_history
import random
import re
from datetime import datetime
from typing import Optional, Dict, Any
import json



class Fault_and_Incident_ReportingTree_EN:
    def __init__(self):
        # Initialize nodes
        self.root = TreeNode('awaiting_district', self.awaiting_district)
        self.awaiting_town_node = TreeNode('awaiting_town', self.awaiting_town)
        self.awaiting_identifier_node = TreeNode('awaiting_identifier', self.awaiting_identifier)
        self.awaiting_fault_type_node = TreeNode('awaiting_fault_type', self.awaiting_fault_type)
        self.confirm_details_node = TreeNode('confirm_details', self.confirm_details)
        self.exit_node = TreeNode('exit', self.exit_request)

        # Set up workflow
        self.root.add_child('awaiting_town', self.awaiting_town_node)
        self.awaiting_town_node.add_child('awaiting_identifier', self.awaiting_identifier_node)
        self.awaiting_identifier_node.add_child('awaiting_fault_type', self.awaiting_fault_type_node)
        self.awaiting_fault_type_node.add_child('confirm_details', self.confirm_details_node)
        self.confirm_details_node.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        try:
            # Handle global commands
            if 'exit' in user_message.lower():
                session['current_state'] = 'exit'
            if 'restart' in user_message.lower():
                return self.reset_fault_reporting(session)

            current_state = session.get('current_state', 'awaiting_district')
            current_node = self._find_node(self.root, current_state)
            return current_node.handle(user_message, session) if current_node else self.reset_fault_reporting(session)

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
            response = f"Please provide a  district name. Examples: {districts}"
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
                       "to proceed with the fault report.")
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
            session['current_state'] = 'awaiting_fault_type'
            response = self._get_fault_type_prompt()
        elif contact_number:
            session['identifier_type'] = 'contact'
            session['identifier'] = contact_number
            session['current_state'] = 'awaiting_fault_type'
            response = self._get_fault_type_prompt()
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
            response = ("Please specify the type of electrical fault:\n")
                       #"1. Power failure\n"
                       #"2. Voltage issue\n"
                       #"3. Broken line\n"
                       #"4. Transformer problem\n"
                       #"5. Electric shock\n\n"
                       #"You can either type the fault type or enter the corresponding number.")
        update_chat_history(session, "bot", response)
        return response

    def _extract_fault_type(self, message):
        fault_keywords = {
            "power failure": ["no power", "electricity out", "blackout"],
            "voltage issue": ["fluctuation", "dim lights", "voltage drop"],
            "broken line": ["fallen wire", "damaged line", "wire down"],
            "transformer problem": ["transformer", "explosion", "loud bang"],
            "electric shock": ["shock", "current leak", "earthing"]
        }

        # Mapping of numbers to fault types
        fault_type_mapping = {
            "1": "power failure",
            "2": "voltage issue",
            "3": "broken line",
            "4": "transformer problem",
            "5": "electric shock"
        }

        message = message.lower().strip()
        
        # Check if the message is a number corresponding to a fault type
        if message in fault_type_mapping:
            return fault_type_mapping[message]
        
        # Direct match
        if message in fault_keywords:
            return message
            
        # Keyword match
        for fault, keywords in fault_keywords.items():
            if any(keyword in message for keyword in keywords):
                return fault
                
        return None

    def confirm_details(self, user_message, session):
        if 'yes' in user_message.lower() or 'correct' in user_message.lower():
            session['current_state'] = 'exit'
            return self._generate_summary(session)
        elif 'no' in user_message.lower():
            return self._handle_correction(session)
        return "Please confirm if the details are correct (yes/no)."

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

    def reset_fault_reporting(self, session):
        session['current_state'] = 'awaiting_district'
        session['chat_history'] = []
        response = "Please provide your district to report a fault."
        update_chat_history(session, "bot", response)
        return response

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
        </div>
        """

    def _generate_summary(self, session):
        identifier = session.get('identifier', '')
        ref_number = f"FR{datetime.now().strftime('%y%m%d')}{identifier[-4:]}"
        identifier_type = "Account Number" if session.get('identifier_type') == 'account' else "Contact Number"
         # Create decorative borders
        
        return (
            
        "FAULT REPORT SUMMARY \n"
        
        f"District: {session.get('district')}\n"
        f"Town: {session.get('town')}\n"
        f"{identifier_type}: {session.get('identifier')}\n"
        f"Fault Type: {session.get('fault_type')}\n"
        f"Reference Number: {ref_number}\n"
        
        "Status: Your complaint has been registered.\n"
        "We will inform the relevant authorities\n"
        "for further action. Thank you!\n"
        "We will contact you shortly with updates.\n"
        
        )

    def _handle_correction(self, session):
        session['current_state'] = 'awaiting_district'
        return ("Let's start over to ensure accurate information. "
                "Please provide your district name.")

    def _choose_response(self, responses):
        return random.choice(responses)

    def _get_fault_type_prompt(self):
        return """
        <div>
            <p>What type of fault are you experiencing?</p>
            <p>Please select from the following options:</p>
            <button class="language-button" onclick="sendMessage('Power failure', this)">1. Power failure</button>
            <button class="language-button" onclick="sendMessage( 'Voltage issue',this)">2. Voltage issue</button>
            <button class="language-button" onclick="sendMessage('Broken line', this)">3. Broken line</button>
            <button class="language-button" onclick="sendMessage( 'Transformer problem',this)">4. Transformer problem</button>
            <button class="language-button" onclick="sendMessage( 'Electric shock',this)">5. Electric shock</button>
            <button class="language-button" onclick="sendMessage('Other', this)">6. Other</button>
            <p>You can either type the fault type or enter the corresponding number.</p>
        </div>
    """

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
        return response


