# fault_and_incident.py

from .english.en_fault_reporting import Fault_and_Incident_ReportingTree_EN

def handle_fault_and_incident_reporting(user_message, session):
    language = session.get('selected_language', 'unknown')
    print(user_message,language)
    if language.lower() == 'english':
        fault_and_incident_tree = Fault_and_Incident_ReportingTree_EN()
        return fault_and_incident_tree.handle_state(user_message, session)
    elif language.lower() == 'sinhala':
        fault_and_incident_tree = Fault_and_Incident_ReportingTree_EN()
        return fault_and_incident_tree.handle_state(user_message, session)
    elif language.lower() == 'tamil':
        fault_and_incident_tree = Fault_and_Incident_ReportingTree_EN()
        return fault_and_incident_tree.handle_state(user_message, session)
    else:
        return f"Performing task in default language: {language}"