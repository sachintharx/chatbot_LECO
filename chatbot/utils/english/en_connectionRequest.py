from ...models import TreeNode
import random
import json

class ConnectionRequestTree_EN:
    def __init__(self):
        # Create nodes for different states
        self.root = TreeNode('awaiting_district', self.awaiting_district)

        # Create nodes for awaiting_town state and exit
        self.awaiting_town_node = TreeNode('awaiting_town', self.awaiting_town)
        self.exit_node = TreeNode('exit', self.exit_request)

        # Add children nodes (state transitions)
        self.root.add_child('awaiting_town', self.awaiting_town_node)
        self.awaiting_town_node.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        # Check if user wants to end the session
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'

        # Get the current state from the session (default to 'awaiting_district')
        current_state = session.get('current_state', 'awaiting_district')

        # Traverse the tree from the root based on current state
        current_node = self._find_node(self.root, current_state)

        if current_node:
            # Handle the current state and proceed
            response = current_node.handle(user_message, session)

            # If the state has transitioned, the response will be returned
            return response
        else:
            return self.reset_connection_request(session)

    def _find_node(self, current_node, state_name):
        # Traverse the tree to find the node corresponding to the state_name
        if current_node.name == state_name:
            return current_node

        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def awaiting_district(self, user_message, session):
        # Extract district from user message
        district = extract_district(user_message)

        if district:
            session['district'] = district
            session['current_state'] = 'awaiting_town'  # Transition to the next state
            response = self._choose_response([
                f"Thank you for providing your district: {district}. Please provide the nearest town.",
                f"Got it! Your district is {district}. Now, tell me your nearest town.",
                f"Thank you for providing your district: {district}. Can you also share the nearest town?"
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)
        else:
            response = self._choose_response([
                "Please enter your district to request a new connection.",
                "Could you please provide your district?",
                "We need your district to proceed with the request."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def awaiting_town(self, user_message, session):
        # Extract town from user message
        town = extract_town(user_message)

        if town:
            session['town'] = town
            session['current_state'] = 'exit'  # After receiving town, transition to exit state
            response = self._choose_response([
                f"Thank you for providing your town: {town}. A representative will contact you shortly.",
                f"Great! Your town is {town}. A representative will be in touch soon.",
                f"Thank you for providing your town: {town}. You will be contacted shortly."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)
        else:
            response = self._choose_response([
                "Please provide a valid town near your district.",
                "Could you share the town closest to your district?",
                "We need a town near your district to proceed."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def exit_request(self, user_message, session):
        # Handle customer exit request
        response = "Thank you for using our service. If you need further assistance, feel free to ask!"
        update_chat_history(session, "bot", response)
        session.clear()  # End the session
        return response

    def reset_connection_request(self, session):
        # Reset the session to the initial state
        session['current_state'] = 'awaiting_district'
        session['chat_history'] = []  # Reset chat history

        response = "Please enter your district to request a new connection."
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
def extract_district(message):
    # Extract district from message
    sri_lankan_districts = [
        "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya",
        "Galle", "Matara", "Hambantota", "Jaffna", "Kilinochchi", "Mannar",
        "Vavuniya", "Mullaitivu", "Batticaloa", "Ampara", "Trincomalee",
        "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla",
        "Monaragala", "Ratnapura", "Kegalle"
    ]
    for district in sri_lankan_districts:
        if district.lower() in message.lower():
            return district
    return None


def extract_town(message):
    sl_towns = [
        "Hindagala","Peradeniya" 
    ]
    for town in sl_towns:
        if town.lower() in message.lower():
            return town
    return None


def load_towns_from_json(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as json_file:
            towns = json.load(json_file)
        return towns
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return []

# def extract_town(message, json_file='towns.json'):
#     # Get the absolute path for the JSON file
#     json_file_path = os.path.join(os.getcwd(), json_file)

#     # Load the list of towns from the JSON file
#     try:
#         with open(json_file_path, 'r', encoding='utf-8') as file:
#             sl_towns = json.load(file)
#     except FileNotFoundError:
#         print(f"Error: JSON file not found at {json_file_path}.")
#         return None
#     except json.JSONDecodeError:
#         print("Error: Failed to decode JSON.")
#         return None

#     # Check if any town name is present in the message (case-insensitive)
#     for town in sl_towns:
#         if town.lower() in message.lower():  # Ensure case-insensitive matching
#             return town
#     return None

def update_chat_history(session, sender, message):
    if 'chat_history' not in session:
        session['chat_history'] = []
    session['chat_history'].append({'sender': sender, 'message': message})
    session.modified = True






