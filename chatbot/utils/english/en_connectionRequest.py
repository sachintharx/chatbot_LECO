from ...models import TreeNode
from ..chat_histories import update_chat_history
import random

class ConnectionRequestTree_EN:
    def _init_(self):
        # Create nodes for different states
        self.root = TreeNode('awaiting_form_download', self.awaiting_form_download)
        self.exit_node = TreeNode('exit', self.exit_request)

        # Add children nodes (state transitions)
        self.root.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        # Check if user wants to end the session
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'

        # Get the current state from the session (default to 'awaiting_form_download')
        current_state = session.get('current_state', 'awaiting_form_download')

        # Traverse the tree from the root based on current state
        current_node = self._find_node(self.root, current_state)

        if current_node:
            # Handle the current state and proceed
            response = current_node.handle(user_message, session)
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

    def awaiting_form_download(self, user_message, session):
        # Provide the form download link and guide the customer to visit the nearest branch
        form_download_link = "https://www.leco.lk/content/files/applications/LECO-CSC-FO-24.pdf"  # Replace with the actual form download link
        response = self._choose_response([
            f"Please download the form by clicking this link: <a href='{form_download_link}' download>Download Form</a>. Once you have filled it out, please submit it at your nearest branch.",
            f"Here is the link to download the form: <a href='{form_download_link}' download>Download Form</a>. After filling it, kindly visit the nearest branch to submit it.",
            f"Download the form here: <a href='{form_download_link}' download>Download Form</a>. Please visit the nearest branch to submit your completed form."
        ])
        session['current_state'] = 'exit'  # Transition directly to the exit state
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
        session['current_state'] = 'awaiting_form_download'
        session['chat_history'] = []  # Reset chat history

        response = "Please download and submit the form at the nearest branch to request a new connection."
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