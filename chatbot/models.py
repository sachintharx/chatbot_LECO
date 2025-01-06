from django.db import models

class TreeNode:
    def __init__(self, name, handler=None):
        self.name = name
        self.handler = handler  # State handler function
        self.children = {}  # Children nodes for state transitions

    def add_child(self, state_name, child_node):
        self.children[state_name] = child_node

    def handle(self, user_message, session):
        # If the state has a handler, execute it
        if self.handler:
            return self.handler(user_message, session)
        else:
            return None
        
        
    