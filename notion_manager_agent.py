import requests
import os
import json

api_key = os.getenv("NOTION_API_KEY")

def determine_user_intent(user_input):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }


    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": """
            
            You are a helpful assistant that helps the user manage their Notion schedule.
            You are responsible for determining the user's intent and responding accordingly.

            The user will ask you to complete a task for them. You need to classify the task into one of the following INTENT TYPES:

            1. CREATE_TASK - User wants to add new task(s) to their Notion schedule
            2. QUERY_TASKS - User wants to query their Notion schedule for tasks
            3. UPDATE_TASK - User wants to update an existing task in their Notion schedule (e.g. change the due date, priority, status, etc.)
            4. DELETE_TASK - User wants to delete an existing task in their Notion schedule
            5. SEARCH_TASKS - User wants to search their Notion schedule for tasks
            6. UNKNOWN - User's intent is not clear

            EXAMPLES:
            - "Add a meeting tomorrow at 2pm" → CREATE_TASK
            - "Show me my tasks for this week" → QUERY_TASKS
            - "What tasks do I have today?" → QUERY_TASKS
            - "Mark the workout task as completed" → UPDATE_TASK
            - "Change the meeting time to 3pm" → UPDATE_TASK
            - "Delete the old task" → DELETE_TASK
            - "Find tasks about project planning" → SEARCH_TASKS
            - "Hello" → UNKNOWN

            Only respond with the intent type (CREATE_TASK, QUERY_TASKS, UPDATE_TASK, DELETE_TASK, SEARCH_TASKS, UNKNOWN), no other text.

            User Input: """ + user_input + """
            """
            
            }
        ]
        }
    ],
    
    "max_tokens": 50
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            intent = response_data['choices'][0]['message']['content'].strip()
            return intent
        else:
            return "UNKNOWN"
    except Exception as e:
        print(f"Error classifying intent: {e}")
        return "UNKNOWN"