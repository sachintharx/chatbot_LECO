from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib
from .utils.chat_workflows import rule_based_response
from .utils.english.en_connectionRequest import update_chat_history
from .utils.connectionRequest import handle_connection_request
from .utils.bill_inquiries import handle_bill_inquiries
from .utils.fault_and_incident import handle_fault_and_incident_reporting
from .utils.solar_services import handle_solar_services
from .utils.language_selection import (
    get_language_selection_response,
    handle_language_selection,
    get_main_menu_response_EN,
)
from .utils.chat_histories import save_chat_history, generate_customer_id
from .utils.session_time import check_session_timeout
from chatbot.utils import fault_and_incident

# Load saved model and vectorizer
loaded_classifier = joblib.load('best_rf_classifier_model_V_5.joblib')
loaded_vectorizer = joblib.load('tfidf_vectorizer_V_5.joblib')

# Categories for prediction
categories = [
    'greetings',
    'Fault Reporting',
    'Bill Inquiries',
    'New Connection Requests',
    'Incident Reports',
    'Solar Services',
    
]

@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse({'response': 'Invalid request method.'})

    # Extract user message and customer ID from the request
    user_message = request.POST.get('message')
    customer_id = request.POST.get('customer_id', 'UNKNOWN')
    session = request.session

    # Generate a customer ID if not provided
    if not customer_id or customer_id == 'UNKNOWN':
        customer_id = generate_customer_id()
    session['customer_id'] = customer_id

    # Check for session timeout
    timeout_message = check_session_timeout(session)
    if (timeout_message):
        return JsonResponse({'response': timeout_message, 'chat_history': []})

    # Validate user message
    if not user_message:
        return JsonResponse({'response': 'Please provide a message.'})

    # Initialize session variables if not already set
    session.setdefault('chat_history', [])
    session.setdefault('current_workflow', None)
    session.setdefault('workflow_state', None)
    session.setdefault('language_selected', False)
    session.setdefault('selected_language', None)
    session.setdefault('mistake_count', 0)

    # Language selection flow
    if not session['language_selected']:
        response = handle_language_selection(user_message, session)
        session['selected_language'] = user_message.upper()
        update_chat_history(session, "bot", response)
        return JsonResponse({'response': response, 'chat_history': session['chat_history']})

    # Handle exit keyword
    if "exit" in user_message.lower():
        response = "Thank you for using our service. If you need further assistance, feel free to ask!"
        if session['chat_history']:
            save_chat_history(
                customer_id=customer_id,
                language=session.get('selected_language', 'unknown'),
                category=session.get('current_workflow', 'unknown'),
                messages=session['chat_history'],
            )
        session.clear()
        return JsonResponse({'response': response, 'chat_history': []})

    # Handle change language option
    if "change language" in user_message.lower():
        session['language_selected'] = False
        response = get_language_selection_response()
        update_chat_history(session, "bot", response)
        return JsonResponse({'response': response, 'chat_history': session['chat_history']})
    
   

    # Store user message in chat history
    update_chat_history(session, "user", user_message)

    # Workflow handling
    current_workflow = session.get('current_workflow')
    if current_workflow:
        response = rule_based_response(current_workflow, user_message, session, session.get('selected_language', 'unknown'))
        if session.get("workflow_state") == "exit":
            save_chat_history(
                customer_id=customer_id,
                language=session.get('selected_language', 'unknown'),
                category=current_workflow,
                messages=session['chat_history'],
            )
            # handle_connection_request(user_message, session)
            # session['current_workflow'] = None
            # session['workflow_state'] = None
            
            # Dynamically call the appropriate handler based on the workflow
            if current_workflow == "New Connection Requests":
                handle_connection_request(user_message, session)
            elif current_workflow == "Bill Inquiries":
                handle_bill_inquiries(user_message, session)
            elif current_workflow == "Fault Reporting":
                handle_fault_and_incident_reporting(user_message, session)
            elif current_workflow == "Solar Services":
                handle_solar_services(user_message, session)
                
            
            session['current_workflow'] = None
            session['workflow_state'] = None
            
            
    else:
        # Predict category for user message
        message_vect = loaded_vectorizer.transform([user_message])
        new_predictions = loaded_classifier.predict(message_vect)
        predicted_labels = [
            categories[i] for i in range(len(categories)) if new_predictions[0][i] == 1
        ]

        # Handle predictions
        if predicted_labels:
            for label in predicted_labels:
                if label in categories[1:]:  # Skip 'greetings'
                    session['current_workflow'] = label
                    session['workflow_state'] = "start"
                    break
            response = rule_based_response(predicted_labels[0], user_message, session) if predicted_labels else "Sorry, I couldn't understand that."
            session['mistake_count'] = 0
        else:
            # Handle misunderstanding
            session['mistake_count'] += 1
            if session['mistake_count'] >= 2:
                response = get_main_menu_response_EN()
                session['mistake_count'] = 0
            else:
                response = "Sorry, I couldn't understand that."

    # Store bot response in chat history
    if not session['chat_history'] or session['chat_history'][-1]['message'] != response:
        update_chat_history(session, "bot", response)

    return JsonResponse({
        'response': response,
        'current_workflow': session.get('current_workflow'),
        'chat_history': session['chat_history'],
    })

def index(request):
    return render(request, 'index.html')


# python manage.py runserver