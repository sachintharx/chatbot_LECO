from ...models import TreeNode
import random
import json

class ConnectionRequestTree_TA:
    def __init__(self):
        # வெவ்வேறு நிலைகளைச் சிக்கெடுக்க நொடுகளை உருவாக்குதல்
        self.root = TreeNode('awaiting_district', self.awaiting_district)

        # awaiting_town நிலைக்கு மற்றும் exit க்கு நொடுகளை உருவாக்குதல்
        self.awaiting_town_node = TreeNode('awaiting_town', self.awaiting_town)
        self.exit_node = TreeNode('exit', self.exit_request)

        # குழந்தை நொடுகள் சேர்த்தல் (நிலை மாற்றங்கள்)
        self.root.add_child('awaiting_town', self.awaiting_town_node)
        self.awaiting_town_node.add_child('exit', self.exit_node)

    def handle_state(self, user_message, session):
        # பயனர் அமர்வை முடிக்க விரும்பினால் சரிபார்க்கவும்
        if 'exit' in user_message.lower():
            session['current_state'] = 'exit'

        # தற்போதைய நிலையை அமர்விலிருந்து பெறவும் ('awaiting_district' என தோராயமாக அமைக்கவும்)
        current_state = session.get('current_state', 'awaiting_district')

        # தற்போதைய நிலையை அடிப்படையாகக் கொண்டு ரூட்டிலிருந்து மரத்தைச் சிக்கெடுக்கவும்
        current_node = self._find_node(self.root, current_state)

        if current_node:
            # தற்போதைய நிலையை நடத்தி தொடர்ந்து செல்லவும்
            response = current_node.handle(user_message, session)

            # நிலை மாற்றப்பட்டால் பதில் திரும்பும்
            return response
        else:
            return self.reset_connection_request(session)

    def _find_node(self, current_node, state_name):
        # state_name-க்கு நேர்மையான நொடியை மரத்தைச் சிக்கெடுக்கவும்
        if current_node.name == state_name:
            return current_node

        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def awaiting_district(self, user_message, session):
        # பயனர் செய்தியிலிருந்து மாவட்டத்தை பெறுதல்
        district = extract_district(user_message)

        if district:
            session['district'] = district
            session['current_state'] = 'awaiting_town'  # அடுத்த நிலைக்கு மாற்றம் செய்யவும்
            response = self._choose_response([
                f"உங்கள் மாவட்டத்தை வழங்கியதற்கு நன்றி: {district}. தயவுசெய்து அருகிலுள்ள நகரத்தை வழங்கவும்.",
                f"சரி! உங்கள் மாவட்டம் {district}. இப்போது, அருகிலுள்ள நகரத்தைச் சொல்லுங்கள்.",
                f"உங்கள் மாவட்டத்தை வழங்கியதற்கு நன்றி: {district}. அருகிலுள்ள நகரத்தை பகிர்ந்து கொள்ள முடியுமா?"
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)
        else:
            response = self._choose_response([
                "ஒரு புதிய இணைப்பை கோர, உங்கள் மாவட்டத்தைச் சீர்க்கவும்.",
                "உங்கள் மாவட்டத்தைச் சொல்ல முடியுமா?",
                "கோரிக்கையை முன்னெடுக்க உங்கள் மாவட்டம் தேவைப்படுகிறது."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def awaiting_town(self, user_message, session):
        # பயனர் செய்தியிலிருந்து நகரத்தை பெறுதல்
        town = extract_town(user_message)

        if town:
            session['town'] = town
            session['current_state'] = 'exit'  # நகரத்தைப் பெற்ற பிறகு exit நிலைக்கு மாற்றம் செய்யவும்
            response = self._choose_response([
                f"உங்கள் நகரத்தை வழங்கியதற்கு நன்றி: {town}. ஒரு பிரதிநிதி விரைவில் தொடர்பு கொள்ளுவார்.",
                f"மிக அருமை! உங்கள் நகரம் {town}. ஒரு பிரதிநிதி விரைவில் தொடர்பு கொள்வார்.",
                f"உங்கள் நகரத்தை வழங்கியதற்கு நன்றி: {town}. விரைவில் தொடர்பு கொள்வார்கள்."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)
        else:
            response = self._choose_response([
                "உங்கள் மாவட்டத்திற்கு அருகிலுள்ள நகரத்தைச் சரியாக வழங்கவும்.",
                "உங்கள் மாவட்டத்திற்கு அருகிலுள்ள நகரத்தை பகிர முடியுமா?",
                "நீங்கள் நகரத்தை வழங்க வேண்டும்."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def exit_request(self, user_message, session):
        # பயனர் exit கோரிக்கையை நிர்வகிக்கவும்
        response = "எங்கள் சேவையைப் பயன்படுத்தியதற்கு நன்றி. மேலும் உதவி தேவைப்பட்டால் கேட்கவும்!"
        update_chat_history(session, "bot", response)
        session.clear()  # அமர்வை முடிக்கவும்
        return response

    def reset_connection_request(self, session):
        # அமர்வை தொடக்க நிலைக்கு மீட்டமைக்கவும்
        session['current_state'] = 'awaiting_district'
        session['chat_history'] = []  # உரையாடல் வரலாற்றை மீட்டமைக்கவும்

        response = "ஒரு புதிய இணைப்பை கோர, உங்கள் மாவட்டத்தைச் சொல்லவும்."
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def _choose_response(self, responses):
        # பதில்களில் இருந்து எதார்த்தமாக தேர்வு செய்யவும்
        return random.choice(responses)

    def _split_message(self, message, max_length=160):
        # நீளமான செய்திகளைப் பல சிறிய பகுதிகளாகப் பிரிக்கவும்
        if len(message) <= max_length:
            return message

        parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        return parts


# உதவித் தகுதிகள்
def extract_district(message):
    # செய்தியிலிருந்து மாவட்டத்தைப் பெறுதல்
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
        "Hindagala", "Peradeniya"
    ]
    for town in sl_towns:
        if town.lower() in message.lower():
            return town
    return None


def update_chat_history(session, sender, message):
    if 'chat_history' not in session:
        session['chat_history'] = []
    session['chat_history'].append({'sender': sender, 'message': message})
    session.modified = True
