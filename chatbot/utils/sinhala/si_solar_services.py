from ...models import TreeNode
from .si_connectionRequest import update_chat_history

# Main handler for solar services
def handle_solar_services(user_message, session):
    solar_tree = SolarServicesTree()
    return solar_tree.handle_state(user_message, session)

class SolarServicesTree:
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
        session['solar_service_details'] = user_message
        session['current_state'] = 'exit'
        response = "Thank you for your interest in our solar services. Our team will contact you shortly."
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
