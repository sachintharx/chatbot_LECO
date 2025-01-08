from ...models import TreeNode
from .en_connectionRequest import update_chat_history
import requests


class SolarServicesTree_EN:
    def __init__(self):
        self.root = TreeNode('awaiting_solar_service_details', self.awaiting_solar_service_details)
        self.exit_node = TreeNode('exit', self.exit_request)
        self.root.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'
        current_state = session.get('current_state', 'awaiting_solar_service_details')
        current_node = self._find_node(self.root, current_state)
        if current_node:
            response = current_node.handle(user_message, session)
            return response
        else:
            return self.reset_solar_services(session)

    def _find_node(self, current_node, state_name):
        if current_node.name == state_name:
            return current_node
        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def awaiting_solar_service_details(self, user_message, session):
        # Step 1: Fetch response from the chatbot API
        chatbot_response = self.fetch_chatbot_response(user_message, session)

        # Step 2: Update the session details
        session['solar_service_details'] = user_message
        session['current_state'] = 'exit'

        # Step 3: Combine API response with a custom message (optional)
        response = f"{chatbot_response} Our team will contact you shortly."
        update_chat_history(session, "bot", response)

        return response

    def exit_request(self, user_message, session):
        response = "Thank you for using our service. If you need further assistance, feel free to ask!"
        update_chat_history(session, "bot", response)
        session.clear()
        return response

    def reset_solar_services(self, session):
        session['current_state'] = 'awaiting_solar_service_details'
        session['chat_history'] = []
        response = "Please provide details about the solar services you are interested in."
        update_chat_history(session, "bot", response)
        return response

    def fetch_chatbot_response(self, user_message, session):
        """Fetch a response from the chatbot API."""
        # Define the API endpoint
        api_url = "http://localhost:8000/chat/"  # Replace with the actual URL of your API

        # Prepare the request payload
        payload = {
            "question": user_message,
            "session_id": session.get("session_id", None)
        }

        try:
            # Make a POST request to the chatbot API
            response = requests.post(api_url, json=payload)
            response_data = response.json()

            # Update session with the returned session_id
            if 'session_id' in response_data:
                session["session_id"] = response_data["session_id"]

            # Return the chatbot's response
            return response_data.get("response", "I'm sorry, I couldn't understand that.")
        except Exception as e:
            return f"An error occurred while fetching the chatbot response: {str(e)}"
