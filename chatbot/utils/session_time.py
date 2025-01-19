import time
from .chat_histories import save_chat_history

def check_session_timeout(session):
    """
    Checks if the session has been inactive for 30 seconds.
    If inactive, clears the session and returns a timeout message.
    """
    current_time = time.time()
    last_activity = session.get('last_activity', current_time)
    
    # If inactive for 30 seconds or more, end the session
    if current_time - last_activity >= 360000:
        # Save chat history before clearing session
        if session.get('chat_history'):
            save_chat_history(
                customer_id=session.get('customer_id', 'UNKNOWN'),
                language=session.get('selected_language', 'unknown'),
                category=session.get('current_workflow', 'unknown'),
                messages=session['chat_history']
            )
        session.clear()  # Clear session data
        return "Your session has timed out due to inactivity. Please start a new chat if you need further assistance."
    
    # Update the last activity timestamp
    session['last_activity'] = current_time
    return None
