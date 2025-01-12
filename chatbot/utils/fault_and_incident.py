from .english.en_fault_reporting import Fault_and_Incident_ReportingTree_EN



# In another file (e.g., utils/some_file.py)
def handle_fault_and_incident_reporting(user_message, session):
    language = session.get('selected_language', 'unknown')
    if language.lower() == 'english':
        fault_and_incident_tree = Fault_and_Incident_ReportingTree_EN()
        return fault_and_incident_tree.handle_state(user_message, session)
    elif language.lower() == 'sinhala':
        connection_tree = Fault_and_Incident_ReportingTree_EN()
        return connection_tree.handle_state(user_message, session)
    elif language.lower() == 'tamil':
        connection_tree = Fault_and_Incident_ReportingTree_EN()
        return connection_tree.handle_state(user_message, session)
    else:
        return f"Performing task in default language: {language}"