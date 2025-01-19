from .english.en_other_services import OtherServices_EN



# In another file (e.g., utils/some_file.py)
def handle_other_services(user_message, session):
    
    language = session.get('selected_language', 'unknown')
    if language.lower() == 'english':
        other_services_tree = OtherServices_EN()
        return other_services_tree.handle_state(user_message, session)
    elif language.lower() == 'sinhala':
        other_services_tree = OtherServices_EN()
        return other_services_tree.handle_state(user_message, session)
    elif language.lower() == 'tamil':
        other_services_tree = OtherServices_EN()
        return other_services_tree.handle_state(user_message, session)
    else:
        return f"Performing task in default language: {language}"