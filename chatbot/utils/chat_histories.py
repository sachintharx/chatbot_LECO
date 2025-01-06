import json
from datetime import datetime
from pathlib import Path
import os
import re

def generate_customer_id(base_path='chat_histories'):
    
    # Create directory if it doesn't exist
    Path(base_path).mkdir(parents=True, exist_ok=True)
    
    # Get all existing customer IDs from files and their JSON content
    existing_ids = set()
    for filename in os.listdir(base_path):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(base_path, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'customer_id' in data:
                        match = re.match(r'LECO(\d+)', data['customer_id'])
                        if match:
                            existing_ids.add(int(match.group(1)))
            except json.JSONDecodeError:
                # Skip files with invalid JSON
                continue
            except Exception as e:
                # Handle any other unexpected errors gracefully
                print(f"Error processing file {filename}: {e}")
    
    # Find the next available number
    next_number = max(existing_ids, default=0) + 1

    # Format the new ID with leading zeros (e.g., LECO001)
    return f"LECO{next_number:03d}"

def save_chat_history(customer_id, language, category, messages, base_path='chat_histories'):
   
    # Create directory if it doesn't exist
    Path(base_path).mkdir(parents=True, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{customer_id}_{timestamp}.json"
    filepath = os.path.join(base_path, filename)
    
    # Prepare chat history data
    chat_data = {
        "customer_id": customer_id,
        "timestamp": datetime.now().isoformat(),
        "selected_language": language,
        "selected_category": category,
        "chat_messages": messages
    }
    
    # Save to JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, indent=4, ensure_ascii=False)