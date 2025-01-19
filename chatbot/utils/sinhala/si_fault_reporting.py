from ...models import TreeNode
from .si_connectionRequest import update_chat_history

# Main handler for fault reporting
def handle_fault_reporting(user_message, session):
    fault_tree = FaultReportingTree()
    return fault_tree.handle_state(user_message, session)

class FaultReportingTree:
    def __init__(self):
        self.root = TreeNode('awaiting_fault_description', self.awaiting_fault_description)
        self.exit_node = TreeNode('exit', self.exit_request)
        self.root.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'
        current_state = session.get('current_state', 'awaiting_fault_description')
        current_node = self._find_node(self.root, current_state)
        if current_node:
            response = current_node.handle(user_message, session)
            return response
        else:
            return self.reset_fault_reporting(session)

    def _find_node(self, current_node, state_name):
        if current_node.name == state_name:
            return current_node
        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def awaiting_fault_description(self, user_message, session):
        session['fault_description'] = user_message
        session['current_state'] = 'exit'
        response = "Thank you for reporting the fault. Our team will look into it and get back to you shortly."
        update_chat_history(session, "bot", response)
        return response

    def exit_request(self, user_message, session):
        response = "Thank you for using our service. If you need further assistance, feel free to ask!"
        update_chat_history(session, "bot", response)
        session.clear()
        return response

    def reset_fault_reporting(self, session):
        session['current_state'] = 'awaiting_fault_description'
        session['chat_history'] = []
        response = "Please describe the fault you're experiencing."
        update_chat_history(session, "bot", response)
        return response
