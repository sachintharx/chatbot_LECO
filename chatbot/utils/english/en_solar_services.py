from ...models import TreeNode
from .en_connectionRequest import update_chat_history
import requests


class SolarServicesTree_EN:
    def __init__(self):
        # Define states for the initial menu and options
        self.root = TreeNode('initial_selection', self.initial_selection)
        self.solar_details_node = TreeNode('solar_details', self.solar_details)
        self.request_solar_node = TreeNode('request_solar', self.request_solar)
        self.exit_node = TreeNode('exit', self.exit_request)

        # Link nodes to the root
        self.root.add_child('solar_details', self.solar_details_node)
        self.root.add_child('request_solar', self.request_solar_node)
        self.root.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'
            

        # Default to the initial selection if no state is found
        current_state = session.get('current_state', 'initial_selection')
        current_node = self._find_node(self.root, current_state)
        if current_node:
            response = current_node.handle(user_message, session)
            return response
        else:
            return self.reset_to_initial(session)

    def _find_node(self, current_node, state_name):
        if current_node.name == state_name:
            return current_node
        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    # State: Initial selection
    def initial_selection(self, user_message, session):
        if '1' in user_message:
            session['current_state'] = 'solar_details'
            return "You've selected Solar Details. Please ask any question about our solar services."
        elif '2' in user_message:
            session['current_state'] = 'request_solar'
            return "Please provide the details for your solar service request."
        else:
            return "Welcome! Please select an option:\n1. Solar Details\n2. Request Solar\nType 'exit' to leave."

    # State: Solar Details
    def solar_details(self, user_message, session):
        chatbot_response = self.fetch_chatbot_response(user_message, session)
        update_chat_history(session, "bot", chatbot_response)
        return chatbot_response

    # State: Request Solar
    def request_solar(self, user_message, session):
        session['solar_service_details'] = user_message
        session['current_state'] = 'exit'
        response = "Thank you for your request. Our team will contact you shortly."
        update_chat_history(session, "bot", response)
        return response

    # State: Exit
    def exit_request(self, user_message, session):
        response = "Thank you for using our service. If you need further assistance, feel free to ask!"
        update_chat_history(session, "bot", response)
        session.clear()
        return response

    def reset_to_initial(self, session):
        session['current_state'] = 'initial_selection'
        response = "Let's start over. Please select an option:\n1. Solar Details\n2. Request Solar\nType 'exit' to leave."
        update_chat_history(session, "bot", response)
        return response

    # def fetch_chatbot_response(self, user_message, session):
    #     """Fetch a response from the chatbot API."""
    #     api_url = "http://localhost:8001/chat/"  # Replace with the actual URL of your API
    #     payload = {
    #         "question": user_message,
    #         "session_id": session.get("session_id", None)
    #     }
    #     try:
    #         response = requests.post(api_url, json=payload)
    #         response_data = response.json()
    #         if 'session_id' in response_data:
    #             session["session_id"] = response_data["session_id"]
    #         return response_data.get("response", "I'm sorry, I couldn't understand that.")
    #     except Exception as e:
    #         return f"An error occurred while fetching the chatbot response: {str(e)}"
    
    def fetch_chatbot_response(self, user_message, session):
    
        api_url = "http://localhost:8001/chat/"  # URL of the FastAPI endpoint
        payload = {
            "question": user_message,
            "session_id": session.get("session_id", "default")  # Default session if not provided
        }
        
        try:
            # Send POST request to the FastAPI server
            response = requests.post(api_url, json=payload)
            
            # Check if the response is successful
            if response.status_code == 200:
                response_data = response.json()
                
                # Update session with the new session_id if returned
                if 'session_id' in response_data:
                    session["session_id"] = response_data["session_id"]
                
                # Return the chatbot's response
                return response_data.get("response", "I'm sorry, I couldn't understand that.")
            else:
                return f"Error: {response.status_code}, Unable to get response from the chatbot."
        
        except Exception as e:
            return f"An error occurred while fetching the chatbot response: {str(e)}"
