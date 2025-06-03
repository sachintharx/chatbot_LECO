# chat_workflows.py 
from __future__ import annotations
import random
from chatbot.utils import other_services
from .connectionRequest import handle_connection_request
from .bill_inquiries import handle_bill_inquiries
from .fault_and_incident import handle_fault_and_incident_reporting
from .solar_services import handle_solar_services
from .other_services import handle_other_services

# Rule-based response function
def rule_based_response(category, user_message=None, session=None, language='english'):
    if category == 'New Connection Requests':
        return handle_connection_request(user_message, session)
    
    elif category == 'Bill Inquiries':
        print(category)
        return handle_bill_inquiries(user_message, session)
    
    elif category == 'Fault Reporting':
        print(category)
        return handle_fault_and_incident_reporting(user_message, session)
        
    elif category == 'Incident Reports':
        return handle_fault_and_incident_reporting(user_message, session)      
    
    elif category == 'Solar Services':
        return handle_solar_services(user_message, session)
    
    elif category == 'Other Services':
        return handle_other_services(user_message, session)
    
    elif category == 'greetings':
        greetings_responses = [
            "Hello! Welcome to LECO. How can I assist you?",
            "Hi there! How can I help you today?",
            "Hello! How can LECO assist you today?",
            "Hi! Need help with something? I'm here for you."
        ]
        return random.choice(greetings_responses)
    
    return "I'm not sure how to respond to that. Could you clarify?"

