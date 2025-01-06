from ...models import TreeNode
import random
import json

class ConnectionRequestTree_SI:
    def __init__(self):
        # විවිධ තත්වයන් සඳහා නෝඩ් සෑදීම
        self.root = TreeNode('district_ganna', self.district_ganna)

        # නගරය ලබාගැනීමේ තත්වය හා නිමාව සඳහා නෝඩ් සෑදීම
        self.town_ganna_node = TreeNode('town_ganna', self.town_ganna)
        self.exit_node = TreeNode('niwama', self.niwama_ganna)

        # දර නෝඩ් (තත්ව මාරුවීම්) එකතු කිරීම
        self.root.add_child('town_ganna', self.town_ganna_node)
        self.town_ganna_node.add_child('niwama', self.exit_node)

    def handle_state(self, user_message, session):
        # පරිශීලකයා විවෘත කිරීමට කැමතිද කියා පරීක්ෂා කිරීම
        if 'niwama' in user_message.lower():
            session['current_state'] = 'niwama'

        # පරිශීලකයේ වර්තමාන තත්වය ලබාගන්න (පෙරනිමි 'district_ganna' වේ)
        current_state = session.get('current_state', 'district_ganna')

        # වර්තමාන තත්වය අනුව ගසෙන් යාත්‍රා කිරීම
        current_node = self._find_node(self.root, current_state)

        if current_node:
            # වර්තමාන තත්වය සකසමින් ඉදිරියට ගමන් කිරීම
            response = current_node.handle(user_message, session)
            return response
        else:
            return self.reset_connection_request(session)

    def _find_node(self, current_node, state_name):
        # තත්ව නාමයට අනුව ගසෙන් නෝඩ් එකක් සොයන්න
        if current_node.name == state_name:
            return current_node

        for child in current_node.children.values():
            node = self._find_node(child, state_name)
            if node:
                return node
        return None

    def district_ganna(self, user_message, session):
        # දිස්ත්‍රික්කය පරිශීලක පණිවිඩයෙන් ලබාගන්න
        district = extract_district(user_message)

        if district:
            session['district'] = district
            session['current_state'] = 'town_ganna'  # ඊළඟ තත්වයට මාරු වේ
            response = self._choose_response([
                f"ඔබගේ දිස්ත්‍රික්කය ලබාදීමේ ස්තුතියි: {district}. කරුණාකර ආසන්න නගරය ලබාදෙන්න.",
                f"ඔබගේ දිස්ත්‍රික්කය {district} ලෙස ලියාගත්තා. දැන් ආසන්න නගරය කියන්න.",
                f"ඔබගේ දිස්ත්‍රික්කය: {district} ලෙස ලබාගත්තා. ආසන්න නගරයත් ලබාදෙන්න."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)
        else:
            response = self._choose_response([
                "කනගාටුයි! කරුණාකර ඔබගේ දිස්ත්‍රික්කය ඇතුළත් කරන්න.",
                "ඔබගේ දිස්ත්‍රික්කය ලබාදෙන්න.",
                "අපට ඔබගේ දිස්ත්‍රික්කය අවශ්‍යයි ඉදිරියට යාමට."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def town_ganna(self, user_message, session):
        # නගරය පරිශීලක පණිවිඩයෙන් ලබාගන්න
        town = extract_town(user_message)

        if town:
            session['town'] = town
            session['current_state'] = 'niwama'  # නිමාවට මාරු වේ
            response = self._choose_response([
                f"ඔබගේ නගරය ලබාදීමේ ස්තුතියි: {town}. නියෝජිතයෙකු ඔබව සම්බන්ධ කරගනී.",
                f"හොඳයි! ඔබගේ නගරය {town} ලෙස ලියාගත්තා.",
                f"ඔබගේ නගරය: {town} ලබාගත්තා. ඉක්මනින් සම්බන්ධ වේ."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)
        else:
            response = self._choose_response([
                "කරුණාකර ඔබේ දිස්ත්‍රික්කයට ආසන්න නගරයක් ඇතුළත් කරන්න.",
                "ඔබේ දිස්ත්‍රික්කයට ආසන්න නගරය ලබාදෙන්න.",
                "අපට ඔබේ දිස්ත්‍රික්කයට ආසන්න නගරයක් අවශ්‍යයි."
            ])
            update_chat_history(session, "bot", response)
            return self._split_message(response)

    def niwama_ganna(self, user_message, session):
        # පරිශීලකයාගේ ඉල්ලා අස්වීමේ ඉල්ලීම සකසන්න
        response = "අපේ සේවාව භාවිතා කිරීමේ ස්තුතියි. මැදිහත්වීම් අවශ්‍ය නම් නැවත පැමිණෙන්න!"
        update_chat_history(session, "bot", response)
        session.clear()  # සෙෂන් අවසන් වේ
        return response

    def reset_connection_request(self, session):
        # සෙෂන් ආරම්භක තත්වයට යළි සකසන්න
        session['current_state'] = 'district_ganna'
        session['chat_history'] = []  # කතා මාලාව යළි සකසන්න

        response = "කරුණාකර ඔබගේ දිස්ත්‍රික්කය ඇතුළත් කරන්න."
        update_chat_history(session, "bot", response)
        return self._split_message(response)

    def _choose_response(self, responses):
        # විකල්ප ප්‍රතිචාර වලින් එකක් නිර්ධාරිතව තෝරන්න
        return random.choice(responses)

    def _split_message(self, message, max_length=160):
        # දිගු පණිවිඩ සෑහීමකට පරිච්ඡේද කරන්න
        if len(message) <= max_length:
            return message

        parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        return parts

# උපයෝගී කාර්යයන්
def extract_district(message):
    sri_lankan_districts = [
        "කොළඹ", "ගම්පහ", "කළුතර", "මහනුවර", "මාතලේ", "නුවරඑළිය",
        "ගාල්ල", "මාතර", "හම්බන්තොට", "යාපනය", "කිලිනොච්චි", "මන්නාරම",
        "වවුනියාව", "මුලතිව්", "මඩකලපුව", "අම්පාර", "ත්‍රිකුණාමලය",
        "කුරුණෑගල", "පුත්තලම", "අනුරාධපුර", "පොළොන්නරුව", "බදුල්ල",
        "මොණරාගල", "රත්නපුර", "කෑගල්ල"
    ]
    for district in sri_lankan_districts:
        if district.lower() in message.lower():
            return district
    return None

def extract_town(message):
    sl_towns = ["හින්දගල", "පේරාදෙණිය"]
    for town in sl_towns:
        if town.lower() in message.lower():
            return town
    return None

def update_chat_history(session, sender, message):
    if 'chat_history' not in session:
        session['chat_history'] = []
    session['chat_history'].append({'sender': sender, 'message': message})
    session.modified = True
