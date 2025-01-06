from ...models import TreeNode
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
        return response
