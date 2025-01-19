from .english.en_connectionRequest import ConnectionRequestTree_EN
from .sinhala.si_connectionRequest import ConnectionRequestTree_SI
from .tamil.ta_connectionRequest import ConnectionRequestTree_TA


# In another file (e.g., utils/some_file.py)
def handle_connection_request(user_message, session):
    language = session.get('selected_language', 'unknown')
    if language.lower() == 'english':
        connection_tree = ConnectionRequestTree_EN()
        return connection_tree.handle_state(user_message, session)
    elif language.lower() == 'sinhala':
        connection_tree = ConnectionRequestTree_SI()
        return connection_tree.handle_state(user_message, session)
    elif language.lower() == 'tamil':
        connection_tree = ConnectionRequestTree_TA()
        return connection_tree.handle_state(user_message, session)
    else:
        return f"Performing task in default language: {language}"