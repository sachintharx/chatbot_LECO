from .english.en_fault_reporting import FaultReportingTree_EN



# In another file (e.g., utils/some_file.py)
def handle_fault_reporting(user_message, session):
    language = session.get('selected_language', 'unknown')
    if language.lower() == 'english':
        bill_inquiries_tree = FaultReportingTree_EN()
        return bill_inquiries_tree.handle_state(user_message, session)
    elif language.lower() == 'sinhala':
        connection_tree = FaultReportingTree_EN()
        return connection_tree.handle_state(user_message, session)
    elif language.lower() == 'tamil':
        connection_tree = FaultReportingTree_EN()
        return connection_tree.handle_state(user_message, session)
    else:
        return f"Performing task in default language: {language}"