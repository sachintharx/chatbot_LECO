import random

def get_language_selection_response():
    return """
        <div>
            <p>Please select a language:</p>
            <button class="language-button" onclick="sendMessage('Sinhala', this)">සිංහල</button>
            <button class="language-button" onclick="sendMessage('Tamil', this)">தமிழ்</button>
            <button class="language-button" onclick="sendMessage('English', this)">English</button>
        </div>
    """

def handle_language_selection(user_message, session):
    if user_message.lower() == 'sinhala':
        session['language_selected'] = True
        response = get_main_menu_response_SI()
    elif user_message.lower() == 'tamil':
        session['language_selected'] = True
        response = get_main_menu_response_TA()
    elif user_message.lower() == 'english':
        session['language_selected'] = True
        greetings_responses = [
            "Hello! Welcome to LECO. How can I assist you?",
            "Hi there! How can I help you today?",
            "Hello! How can LECO assist you today?",
            "Hi! Need help with something? I'm here for you."
        ]
        return random.choice(greetings_responses)
    else:
        response = get_language_selection_response()
    return response

def get_main_menu_response_EN():
    return """
        <div>
            <p>Please select an option:</p>
            <button class="language-button" onclick="sendMessage('New Connection Requests', this)">New Connection Requests</button>
            <button class="language-button" onclick="sendMessage('Bill Inquiries', this)">Bill Inquiries</button>
            <button class="language-button" onclick="sendMessage('Change Language', this)">Change Language</button>
        </div>
    """
    
def get_main_menu_response_SI():
    return """
        <div>
            <p>කරුණාකර විධානයක් තෝරන්න:</p>
            <button class="language-button" onclick="sendMessage('New Connection Requests', this)">නව සම්බන්ධතා ඉල්ලීම්</button>
            <button class="language-button" onclick="sendMessage('Bill Inquiries', this)">බිල් විමසීම්</button>
            <button class="language-button" onclick="sendMessage('Change Language', this)">භාෂාව වෙනස් කිරීම</button>
        </div>
    """    
    
def get_main_menu_response_TA():
    return """
        <div>
            <p>தயவுசெய்து ஒரு விருப்பத்தைத் தேர்ந்தெடுக்கவும்:</p>
            <button class="language-button" onclick="sendMessage('New Connection Requests', this)">புதிய இணைப்பு கோரிக்கைகள்</button>
            <button class="language-button" onclick="sendMessage('Bill Inquiries', this)">பில் விசாரணைகள்</button>
            <button class="language-button" onclick="sendMessage('Change Language', this)">மொழியை மாற்றவும்</button>
        </div>
    """