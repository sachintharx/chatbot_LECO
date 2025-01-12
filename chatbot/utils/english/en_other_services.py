

class OtherServices_EN():
    def __init__(self):
        self.transitions = {
            "start": self.start,
            "end": self.end,
            "default": self.default,
        }

    def start(self, user_message, session):
        response = """
            <div>
                <p>Please select an option:</p>
                <button class="language-button" onclick="sendMessage('New Connection Requests', this)">New Connection Requests</button>
                <button class="language-button" onclick="sendMessage('Bill Inquiries', this)">Bill Inquiries</button>
                <button class="language-button" onclick="sendMessage('Fault Reporting', this)">Fault Reporting</button>
                <button class="language-button" onclick="sendMessage('Solar Services', this)">Solar Services</button>
                <button class="language-button" onclick="sendMessage('Other Services', this)">Other Services</button>
                <button class="language-button" onclick="sendMessage('Change Language', this)">Change Language</button>
            </div>
        """
        return response, "end"

    def end(self, user_message, session):
        return self.default(user_message, session)

    def default(self, user_message, session):
        response = "Sorry, I couldn't understand that."
        return response, "end"

    def handle_state(self, user_message, session):
        state = session.get('workflow_state', 'start')
        return self.transitions[state](user_message, session)