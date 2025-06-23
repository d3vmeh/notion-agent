import requests
import os
import json
from datetime import datetime, timedelta
from notion_tools import add_tasks_to_notion, get_tasks_from_notion, update_task_in_notion, delete_task_from_notion, search_tasks_in_notion
from speech_tools import *
import ast

api_key = os.getenv("OPENAI_API_KEY")

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

            Today's date is """ + str(datetime.now().strftime("%Y-%m-%d")) + """.

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
            - "Mark the workout task as Done" → UPDATE_TASK
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

"""
TASK CREATION
"""

def request_task_addition(question):
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
            
            You are an assistant that helps make and maintain a daily schedule on Notion.

            The user will ask you to add one or more tasks to their Notion schedule and provide you the details.

            You must respond in a JSON format with the following structure - an array of tasks:

            [
                {
                    "task_name": "The name/title of the task",
                    "due_date": "YYYY-MM-DD HH:MM",
                    "priority": "Low/Medium/High",
                    "category": "General/Personal/Fitness/Fun/School",
                    "status": "To-Do/In Progress/Done",
                    "notes": "Additional details, description, or context about the task"
                }
            ]

            IMPORTANT RULES:
            1. The due_date must be in the format "YYYY-MM-DD HH:MM" (24-hour format)
            2. Priority must be exactly one of: "Low", "Medium", or "High" (case-sensitive)
            3. Category must be exactly one of: "General", "Personal", "Fitness", "Fun", or "School" (case-sensitive)
            4. Status must be exactly one of: "To-Do", "In Progress", or "Done" (case-sensitive)
            5. Notes should contain relevant details, context, or description about the task
            6. If the user doesn't specify a field, use these defaults:
               - priority: "Medium"
               - category: "General"
               - status: "To-Do"
               - notes: "" (empty string if no details provided)
            7. For the due_date, if the user doesn't specify a time, default to "12:00"
            8. If the user doesn't specify a date, use today's date. Today's date is """ + str(datetime.now().strftime("%Y-%m-%d")) + """
            9. ALWAYS return an array, even if there's only one task
            10. If the user mentions multiple tasks, separate them into individual objects in the array

            EXAMPLES:

            User: "Add a meeting with John tomorrow at 2pm to discuss the new project requirements"
            Response: [
                {
                    "task_name": "Meeting with John",
                    "due_date": "2025-06-12 14:00",
                    "priority": "Medium",
                    "category": "General",
                    "status": "To-Do",
                    "notes": "Discuss new project requirements"
                }
            ]

            User: "Add three tasks: workout tomorrow at 6am, buy groceries today at 5pm, and call mom on Friday at 3pm"
            Response: [
                {
                    "task_name": "Workout",
                    "due_date": "2025-06-17 06:00",
                    "priority": "Medium",
                    "category": "Fitness",
                    "status": "To-Do",
                    "notes": ""
                },
                {
                    "task_name": "Buy groceries",
                    "due_date": "2025-06-16 17:00",
                    "priority": "Medium",
                    "category": "General",
                    "status": "To-Do",
                    "notes": ""
                },
                {
                    "task_name": "Call mom",
                    "due_date": "2025-06-20 15:00",
                    "priority": "Medium",
                    "category": "Personal",
                    "status": "To-Do",
                    "notes": ""
                }
            ]

            User: "High priority workout session - need to focus on cardio and strength training"
            Response: [
                {
                    "task_name": "Workout session",
                    "due_date": "2025-06-16 12:00",
                    "priority": "High",
                    "category": "Fitness",
                    "status": "To-Do",
                    "notes": "Focus on cardio and strength training"
                }
            ]

            User: "Complete the math homework for school - chapters 5 and 6, due next week"
            Response: [
                {
                    "task_name": "Complete math homework",
                    "due_date": "2025-06-22 12:00",
                    "priority": "Medium",
                    "category": "School",
                    "status": "To-Do",
                    "notes": "Chapters 5 and 6, due next week"
                }
            ]

            User: "Watch a movie tonight at 8pm for fun - planning to watch the new sci-fi film"
            Response: [
                {
                    "task_name": "Watch a movie",
                    "due_date": "2025-06-16 20:00",
                    "priority": "Low",
                    "category": "Fun",
                    "status": "To-Do",
                    "notes": "Planning to watch the new sci-fi film"
                }
            ]

            User: "Doctor appointment next Friday at 10am for annual checkup"
            Response: [
                {
                    "task_name": "Doctor appointment",
                    "due_date": "2025-06-20 10:00",
                    "priority": "High",
                    "category": "Personal",
                    "status": "To-Do",
                    "notes": "Annual checkup"
                }
            ]

            CRITICAL: Respond with ONLY valid JSON. No comments, no explanations, no additional text outside the JSON structure.

            Here is the task(s) the user wants to add: """ + question + """
            """
            
            }
        ]
        }
    ],
    
    "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()
    
    if 'choices' in response_data and len(response_data['choices']) > 0:
        structured_response = response_data['choices'][0]['message']['content']
        cleaned_response = structured_response.strip('```json\n').strip('```').strip()
        print("Cleaned response:", cleaned_response)
        try:
            response_dict = json.loads(cleaned_response)
            return response_dict
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            try:
                response_dict = ast.literal_eval(cleaned_response)
                return response_dict
            except Exception as ast_error:
                print(f"AST literal_eval error: {ast_error}")
                return {"error": "Failed to decode response as JSON", "content": cleaned_response}
    else:
        return {"error": "No valid response from model"}

def handle_task_creation(user_input):
    """
    Task Creation Handler
    This function orchestrates the task creation process:
    1. Calls request_task_addition to parse the user input
    2. Calls add_tasks_to_notion to save to Notion
    3. Provides feedback to the user
    """
    print(f"\n📝 Processing task creation: '{user_input}'")
    
    response = request_task_addition(user_input)
    
    if "error" in response:
        print("❌ Error occurred:", response["error"])
        return False
    
    if not isinstance(response, list):
        print("❌ Unexpected response format - expected list of tasks")
        return False
    
    tasks = response
    print(f"\n📋 Found {len(tasks)} task(s) to add:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task['task_name']} - {task['due_date']} ({task['priority']} priority)")
    
    try:
        results = add_tasks_to_notion(tasks)
        
        successful = 0
        failed = 0
        for result in results:
            if result['status'] == 'success':
                successful += 1
                print(f"✅ Added: {result['task']}")
            else:
                failed += 1
                print(f"❌ Failed to add {result['task']}: {result['error']}")
        
        if successful > 0:
            print(f"\n🎉 Successfully added {successful} task(s) to Notion!")
        if failed > 0:
            print(f"⚠️  Failed to add {failed} task(s)")
        
        return True
            
    except Exception as e:
        print(f"❌ Error adding tasks to Notion: {e}")
        return False

"""
TASK QUERYING
"""

def parse_query_parameters(user_input):
    """
    Parse user input to extract query parameters for task retrieval.
    This function converts natural language into structured query parameters.
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": f"""
                Parse the user's query to extract filtering and sorting parameters for task retrieval.
                
                Extract the following information:
                1. Date range (today, this week, this month, tomorrow, next week, etc.)
                2. Category filter (General, Personal, Fitness, Fun, School)
                3. Priority filter (Low, Medium, High)
                4. Status filter (To-Do, In Progress, Done)
                5. Sort preference (by due date, priority, etc.)
                6. Limit (how many tasks to show)
                
                Respond in JSON format:
                {{
                    "filters": {{
                        "category": "string or null",
                        "priority": "string or null", 
                        "status": "string or null",
                        "date_range": ["start_date", "end_date"] or null
                    }},
                    "sort_by": {{
                        "property": "due_date or priority",
                        "direction": "ascending or descending"
                    }} or null,
                    "limit": number
                }}
                
                Today's date is {datetime.now().strftime("%Y-%m-%d")}.
                
                Examples:
                - "Show me tasks for this week" → {{"filters": {{"date_range": ["2025-06-16", "2025-06-22"]}}, "sort_by": {{"property": "due_date", "direction": "ascending"}}, "limit": 50}}
                - "High priority tasks" → {{"filters": {{"priority": "High"}}, "sort_by": {{"property": "due_date", "direction": "ascending"}}, "limit": 50}}
                - "Completed fitness tasks" → {{"filters": {{"category": "Fitness", "status": "Done"}}, "sort_by": null, "limit": 50}}
                - "All tasks" → {{"filters": {{}}, "sort_by": {{"property": "due_date", "direction": "ascending"}}, "limit": 50}}
                
                User input: "{user_input}"
                """
            }
        ],
        "max_tokens": 500
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            content = response_data['choices'][0]['message']['content'].strip()
            content = content.strip('```json\n').strip('```').strip()
            return json.loads(content)
        else:
            return {"filters": {}, "sort_by": None, "limit": 50}
    except Exception as e:
        print(f"Error parsing query parameters: {e}")
        return {"filters": {}, "sort_by": None, "limit": 50}

def format_task_display(tasks, title="Tasks"):
    """
    Use LLM to generate a natural language summary of the retrieved tasks.
    """

    if not tasks:
        return f"No tasks found for {title}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    task_summaries = []
    for i, task in enumerate(tasks, 1):
        due_date_str = "No due date"
        if task.get('due_date'):
            try:
                if isinstance(task['due_date'], str):
                    dt = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                    due_date_str = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    due_date_str = task['due_date']
            except:
                due_date_str = str(task['due_date'])
        
        task_summary = {
            "number": i,
            "name": task.get('task_name', 'Untitled'),
            "due_date": due_date_str,
            "priority": task.get('priority', 'N/A'),
            "category": task.get('category', 'N/A'),
            "status": task.get('status', 'N/A'),
            "notes": task.get('notes', ''),
            "id": task.get('id', '')[:8] if task.get('id') else ''
        }
        task_summaries.append(task_summary)

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": f"""
                You are a helpful assistant that summarizes task information in a conversational, natural way.
                
                Today's date is {datetime.now().strftime("%Y-%m-%d")}.
                
                I have retrieved {len(tasks)} tasks from a Notion database. Please provide a natural language summary that:
                
                1. Uses a friendly, conversational tone
                2. Highlights the most important information (due dates, priorities, status)
                3. Groups tasks by priority, category, or status when helpful
                4. Mentions any urgent or overdue tasks prominently
                5. Provides actionable insights (e.g., "You have 3 high-priority tasks due today")
                6. Keeps the summary concise but informative
                
                Task data:
                {json.dumps(task_summaries, indent=2)}
                
                Original query context: "{title}"
                
                Respond with a natural, conversational summary that would be helpful for someone managing their tasks.
                However, be concise and to the point, as the user is likely busy.
                """
            }
        ],
        "max_tokens": 800
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            summary = response_data['choices'][0]['message']['content'].strip()
            return f"\n📋 {title} ({len(tasks)} found):\n" + "=" * 80 + "\n\n" + summary + "\n"
        else:
            # If LLM fails, return a simple formatting
            return f"\n📋 {title} ({len(tasks)} found):\n" + "=" * 80 + "\n" + "❌ Error generating summary - please check the raw data above.\n"
    
    except Exception as e:
        print(f"Error generating task summary: {e}")
        # Return simple formatting
        output = f"\n📋 {title} ({len(tasks)} found):\n"
        output += "=" * 80 + "\n"
        for i, task in enumerate(tasks, 1):
            due_date_str = "No due date"
            if task.get('due_date'):
                try:
                    if isinstance(task['due_date'], str):
                        dt = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                        due_date_str = dt.strftime("%Y-%m-%d %H:%M")
                    else:
                        due_date_str = task['due_date']
                except:
                    due_date_str = str(task['due_date'])
            
            priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task.get('priority', ''), "⚪")
            status_emoji = {"To-Do": "⏳", "In Progress": "🔄", "Done": "✅"}.get(task.get('status', ''), "❓")
            category_emoji = {
                "General": "📝", "Personal": "👤", "Fitness": "💪", 
                "Fun": "🎉", "School": "📚"
            }.get(task.get('category', ''), "📋")
            
            output += f"{i:2d}. {priority_emoji} {status_emoji} {category_emoji} {task.get('task_name', 'Untitled')}\n"
            output += f"    📅 Due: {due_date_str}\n"
            output += f"    🏷️  Priority: {task.get('priority', 'N/A')} | Category: {task.get('category', 'N/A')} | Status: {task.get('status', 'N/A')}\n"
            
            if task.get('notes'):
                output += f"    📝 Notes: {task['notes']}\n"
            
            if task.get('id'):
                output += f"    🆔 ID: {task['id'][:8]}...\n"
            
            output += "\n"
        
        return output

def handle_task_query(user_input):
    """
    Task Query Handler
    This function orchestrates the task query process:
    1. Calls parse_query_parameters to extract filters and sorting
    2. Calls get_tasks_from_notion to retrieve tasks
    3. Uses LLM to generate natural language summary of results
    """
    
    print(f"\n🔍 Processing task query: '{user_input}'")
    
    params = parse_query_parameters(user_input)
    print(f"📊 Query parameters: {params}")
    
    result = get_tasks_from_notion(
        filters=params.get('filters'),
        sort_by=params.get('sort_by'),
        limit=params.get('limit', 50)
    )
    
    if "error" in result:
        print(f"❌ Error retrieving tasks: {result['error']}")
        return False
    
    tasks = result.get('tasks', [])
    if not tasks:
        print(f"📭 No tasks found matching your query: '{user_input}'")
        print("💡 Try a broader search like 'all tasks' or 'tasks for this month'")
        return True
    
    print(format_task_display(tasks, f"Tasks for '{user_input}'"))
    return True
    

def get_task_input():
    """
    Get User Input
    This function handles getting input from the user (speech or text)
    """
    while True:
        print("\n" + "="*60)
        print("🤖 NOTION TASK MANAGER")
        print("="*60)
        print("Choose input method:")
        print("1. 🎤 Speech input (Push-to-Talk)")
        print("2. ⌨️  Text input")
        print("3. ❌ Exit")
        print("-"*60)
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🎤 Switching to speech mode...")
            print("💡 Tip: Press ENTER to start recording, speak clearly and pause when done")
            speech_text = listen_for_speech_push_to_talk()
            
            if speech_text:
                if speech_text == "quit":
                    print("👋 Goodbye!")
                    return None
                else:
                    return speech_text
            elif speech_text is None:
                print("🔄 Returning to menu...")
                continue
            else:
                print("❌ Speech input failed. Please try again or choose text input.")
                continue
                
        elif choice == "2":
            print("\nText input mode:")
            text_input = input("Enter your request: ").strip()
            
            if text_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                return None
            elif text_input:
                return text_input
            else:
                print("❌ Please enter a valid request.")
                continue
                
        elif choice == "3":
            print("👋 Goodbye!")
            return None
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")



"""
TASK UPDATING
"""

def parse_update_request(user_input):
    """
    Parse Update Request
    This function extracts what needs to be updated from natural language
    """
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
            
            You are an assistant that helps update tasks in a Notion schedule.

            The user wants to update an existing task. You need to extract:
            1. What task they want to update (task identifier)
            2. What changes they want to make to the task

            Respond in JSON format with this structure:

            {
                "task_identifier": {
                    "type": "name/id/description",
                    "value": "the identifier value"
                },
                "updates": {
                    "task_name": "new name (if changing)",
                    "due_date": "YYYY-MM-DD HH:MM (if changing)",
                    "priority": "Low/Medium/High (if changing)",
                    "category": "General/Personal/Fitness/Fun/School (if changing)",
                    "status": "To-Do/In Progress/Done (if changing)",
                    "notes": "new notes (if changing)"
                }
            }

            IMPORTANT RULES:
            1. Only include fields in "updates" that are actually being changed
            2. For task_identifier:
               - "type": "name" if they mention the task name
               - "type": "id" if they mention a specific ID
               - "type": "description" if they describe the task
            3. For dates: Use "YYYY-MM-DD HH:MM" format (24-hour)
            4. For priority: Must be "Low", "Medium", or "High"
            5. For category: Must be "General", "Personal", "Fitness", "Fun", or "School"
            6. For status: Must be "To-Do", "In Progress", or "Done"
            7. If no specific changes mentioned, return empty "updates" object
            8. Today's date is """ + str(datetime.now().strftime("%Y-%m-%d")) + """

            EXAMPLES:

            User: "Mark the workout task as Done"
            Response: {
                "task_identifier": {
                    "type": "name",
                    "value": "workout"
                },
                "updates": {
                    "status": "Done"
                }
            }

            User: "Change the meeting with John to tomorrow at 3pm"
            Response: {
                "task_identifier": {
                    "type": "description",
                    "value": "meeting with John"
                },
                "updates": {
                    "due_date": "2025-06-17 15:00"
                }
            }

            User: "Update the project planning task to high priority and add notes about the deadline"
            Response: {
                "task_identifier": {
                    "type": "name",
                    "value": "project planning"
                },
                "updates": {
                    "priority": "High",
                    "notes": "Deadline approaching"
                }
            }

            User: "Change the grocery shopping task category to Personal"
            Response: {
                "task_identifier": {
                    "type": "name",
                    "value": "grocery shopping"
                },
                "updates": {
                    "category": "Personal"
                }
            }

            User Input: """ + user_input + """
            """
            
            }
        ]
        }
    ],
    
    "max_tokens": 500
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            result_text = response_data['choices'][0]['message']['content'].strip()
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing update request: {e}")
                return None
        else:
            return None
    except Exception as e:
        print(f"❌ Error parsing update request: {e}")
        return None

def identify_task_to_update(task_identifier, available_tasks):
    """
    Identify Task to Update
    This function finds the specific task to update based on the identifier
    """
    if not available_tasks:
        return None
    
    identifier_type = task_identifier.get('type', 'name')
    identifier_value = task_identifier.get('value', '').lower()
    
    if identifier_type == 'id':
        for task in available_tasks:
            if task.get('id', '').startswith(identifier_value):
                return task
        return None
    
    elif identifier_type == 'name':
        best_match = None
        best_score = 0
        
        for task in available_tasks:
            task_name = task.get('task_name', '').lower()
            
            if task_name == identifier_value:
                return task
            
            if identifier_value in task_name or task_name in identifier_value:
                score = len(set(identifier_value.split()) & set(task_name.split()))
                if score > best_score:
                    best_score = score
                    best_match = task
        
        return best_match
    
    elif identifier_type == 'description':
        best_match = None
        best_score = 0
        
        for task in available_tasks:
            task_name = task.get('task_name', '').lower()
            task_notes = task.get('notes', '').lower()
            task_text = f"{task_name} {task_notes}"
            
            identifier_words = set(identifier_value.split())
            task_words = set(task_text.split())
            score = len(identifier_words & task_words)
            
            if score > best_score:
                best_score = score
                best_match = task
        
        return best_match
    
    return None

def handle_task_update(user_input):
    """
    Task Update Handler
    This function orchestrates the task update process:
    1. Parses the update request to understand what needs to be changed
    2. Retrieves available tasks to find the target task
    3. Identifies the specific task to update
    4. Calls the update function
    5. Provides feedback to the user
    """
    
    print(f"\n🔄 Processing task update: '{user_input}'")
    
    update_info = parse_update_request(user_input)
    if not update_info:
        print("❌ Could not understand what you want to update. Please be more specific.")
        print("💡 Examples:")
        print("   • 'Mark the workout task as Done'")
        print("   • 'Change the meeting time to 3pm'")
        print("   • 'Update the project task to high priority'")
        return False
    
    task_identifier = update_info.get('task_identifier', {})
    updates = update_info.get('updates', {})
    
    if not updates:
        print("❌ No changes specified. Please tell me what you want to update.")
        return False
    
    print(f"📝 Identified updates: {list(updates.keys())}")
    
    print("🔍 Retrieving available tasks to find the target task...")
    result = get_tasks_from_notion(limit=100)  # Get more tasks for better matching
    
    if "error" in result:
        print(f"❌ Error retrieving tasks: {result['error']}")
        return False
    
    available_tasks = result.get('tasks', [])
    if not available_tasks:
        print("❌ No tasks found in your Notion database.")
        return False
    
    target_task = identify_task_to_update(task_identifier, available_tasks)
    
    if not target_task:
        print(f"❌ Could not find a task matching '{task_identifier.get('value', '')}'")
        print("💡 Available tasks:")
        for i, task in enumerate(available_tasks[:10], 1):
            print(f"   {i}. {task.get('task_name', 'Untitled')}")
        if len(available_tasks) > 10:
            print(f"   ... and {len(available_tasks) - 10} more tasks")
        return False
    
    print(f"✅ Found target task: {target_task.get('task_name', 'Untitled')}")
    
    print(f"🔄 Updating task...")
    update_result = update_task_in_notion(target_task['id'], updates)
    
    if "error" in update_result:
        print(f"❌ Error updating task: {update_result['error']}")
        return False
    
    print(f"✅ Task updated successfully!")
    print(f"📝 Updated fields: {', '.join(update_result.get('updated_fields', []))}")
    
    print(f"\n📋 Updated Task Details:")
    print(f"   📝 Name: {target_task.get('task_name', 'Untitled')}")
    
    if 'due_date' in updates:
        print(f"   📅 Due Date: {updates['due_date']}")
    else:
        due_date = target_task.get('due_date')
        if due_date:
            print(f"   📅 Due Date: {due_date}")
    
    if 'priority' in updates:
        print(f"   🏷️  Priority: {updates['priority']}")
    else:
        print(f"   🏷️  Priority: {target_task.get('priority', 'N/A')}")
    
    if 'category' in updates:
        print(f"   📂 Category: {updates['category']}")
    else:
        print(f"   📂 Category: {target_task.get('category', 'N/A')}")
    
    if 'status' in updates:
        print(f"   📊 Status: {updates['status']}")
    else:
        print(f"   📊 Status: {target_task.get('status', 'N/A')}")
    
    if 'notes' in updates:
        print(f"   📝 Notes: {updates['notes']}")
    elif target_task.get('notes'):
        print(f"   📝 Notes: {target_task.get('notes')}")
    
    return True


"""
TASK DELETION
"""

def parse_delete_request(user_input):
    """
    Parse Delete Request
    This function extracts what task needs to be deleted from natural language
    """
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
            
            You are an assistant that helps delete tasks from a Notion schedule.

            The user wants to delete an existing task. You need to extract:
            1. What task they want to delete (task identifier)

            Respond in JSON format with this structure:

            {
                "task_identifier": {
                    "type": "name/id/description",
                    "value": "the identifier value"
                }
            }

            IMPORTANT RULES:
            1. For task_identifier:
               - "type": "name" if they mention the task name
               - "type": "id" if they mention a specific ID
               - "type": "description" if they describe the task
            2. Extract the most specific identifier possible
            3. If multiple tasks could match, prefer the most specific one

            EXAMPLES:

            User: "Delete the workout task"
            Response: {
                "task_identifier": {
                    "type": "name",
                    "value": "workout"
                }
            }

            User: "Remove the meeting with John"
            Response: {
                "task_identifier": {
                    "type": "description",
                    "value": "meeting with John"
                }
            }

            User: "Delete task abc123"
            Response: {
                "task_identifier": {
                    "type": "id",
                    "value": "abc123"
                }
            }

            User: "Remove the grocery shopping task"
            Response: {
                "task_identifier": {
                    "type": "name",
                    "value": "grocery shopping"
                }
            }

            User Input: """ + user_input + """
            """
            
            }
        ]
        }
    ],
    
    "max_tokens": 300
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            result_text = response_data['choices'][0]['message']['content'].strip()
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing delete request: {e}")
                return None
        else:
            return None
    except Exception as e:
        print(f"❌ Error parsing delete request: {e}")
        return None

def identify_task_to_delete(task_identifier, available_tasks):
    """
    Identify Task to Delete
    This function finds the specific task to delete based on the identifier
    """
    if not available_tasks:
        return None
    
    identifier_type = task_identifier.get('type', 'name')
    identifier_value = task_identifier.get('value', '').lower()
    
    if identifier_type == 'id':
        for task in available_tasks:
            if task.get('id', '').startswith(identifier_value):
                return task
        return None
    
    elif identifier_type == 'name':
        best_match = None
        best_score = 0
        
        for task in available_tasks:
            task_name = task.get('task_name', '').lower()
            
            if task_name == identifier_value:
                return task
            
            if identifier_value in task_name or task_name in identifier_value:
                score = len(set(identifier_value.split()) & set(task_name.split()))
                if score > best_score:
                    best_score = score
                    best_match = task
        
        return best_match
    
    elif identifier_type == 'description':
        best_match = None
        best_score = 0
        
        for task in available_tasks:
            task_name = task.get('task_name', '').lower()
            task_notes = task.get('notes', '').lower()
            task_text = f"{task_name} {task_notes}"
            
            identifier_words = set(identifier_value.split())
            task_words = set(task_text.split())
            score = len(identifier_words & task_words)
            
            if score > best_score:
                best_score = score
                best_match = task
        
        return best_match
    
    return None

def handle_task_deletion(user_input):
    """
    Task Deletion Handler
    This function orchestrates the task deletion process:
    1. Parses the delete request to understand what task to delete
    2. Retrieves available tasks to find the target task
    3. Identifies the specific task to delete
    4. Confirms deletion with user
    5. Calls the delete function
    6. Provides feedback to the user
    """
    
    print(f"\n🗑️  Processing task deletion: '{user_input}'")
    
    delete_info = parse_delete_request(user_input)
    if not delete_info:
        print("❌ Could not understand what task you want to delete. Please be more specific.")
        print("💡 Examples:")
        print("   • 'Delete the workout task'")
        print("   • 'Remove the meeting with John'")
        print("   • 'Delete task abc123'")
        return False
    
    task_identifier = delete_info.get('task_identifier', {})
    
    print("🔍 Retrieving available tasks to find the target task...")
    result = get_tasks_from_notion(limit=100)
    
    if "error" in result:
        print(f"❌ Error retrieving tasks: {result['error']}")
        return False
    
    available_tasks = result.get('tasks', [])
    if not available_tasks:
        print("❌ No tasks found in your Notion database.")
        return False
    
    target_task = identify_task_to_delete(task_identifier, available_tasks)
    
    if not target_task:
        print(f"❌ Could not find a task matching '{task_identifier.get('value', '')}'")
        print("💡 Available tasks:")
        for i, task in enumerate(available_tasks[:10], 1):
            print(f"   {i}. {task.get('task_name', 'Untitled')}")
        if len(available_tasks) > 10:
            print(f"   ... and {len(available_tasks) - 10} more tasks")
        return False
    
    print(f"✅ Found target task: {target_task.get('task_name', 'Untitled')}")
    
    # Confirmation
    print(f"\n📋 Task Details:")
    print(f"   📝 Name: {target_task.get('task_name', 'Untitled')}")
    
    due_date = target_task.get('due_date')
    if due_date:
        print(f"   📅 Due Date: {due_date}")
    
    print(f"   🏷️  Priority: {target_task.get('priority', 'N/A')}")
    print(f"   📂 Category: {target_task.get('category', 'N/A')}")
    print(f"   📊 Status: {target_task.get('status', 'N/A')}")
    
    if target_task.get('notes'):
        print(f"   📝 Notes: {target_task.get('notes')}")
    
    print(f"\n⚠️  Are you sure you want to delete this task?")
    print("💡 Note: Tasks are archived in Notion (not permanently deleted)")
    confirm = input("Type 'yes' to confirm deletion: ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Deletion cancelled.")
        return False
    
    print(f"🗑️  Deleting task...")
    delete_result = delete_task_from_notion(target_task['id'])
    
    if "error" in delete_result:
        print(f"❌ Error deleting task: {delete_result['error']}")
        return False
    
    print(f"✅ Task deleted successfully!")
    print(f"📝 Deleted task: {target_task.get('task_name', 'Untitled')}")
    print(f"💡 The task has been archived in Notion")
    
    return True


def main():
    print("🚀 Starting Notion Task Manager...")
    print("💡 This agent can:")
    print("   • Create new tasks")
    print("   • View and query existing tasks")
    print("   • Update task details")
    print("   • Search for specific tasks")
    print("   • Delete tasks")
    print("\n💡 Tips:")
    print("   - Be specific about dates, times, and details")
    print("   - For speech: Press ENTER to start, speak clearly and pause when done")
    print("   - Examples:")
    print("     • 'Add a meeting tomorrow at 2pm'")
    print("     • 'Show me tasks for this week'")
    print("     • 'Mark the workout task as Done'")
    print("     • 'Delete the grocery shopping task'")
    print("     • 'Find tasks about project planning'")
    
    while True:
        user_input = get_task_input()
        
        if user_input is None:
            break
        
        intent = determine_user_intent(user_input)
        print(f"\n🎯 Detected intent: {intent}")
        
        # Route intent to appropriate handler
        if intent == "CREATE_TASK":
            handle_task_creation(user_input)
        elif intent == "QUERY_TASKS":
            handle_task_query(user_input)
        elif intent == "UPDATE_TASK":
            handle_task_update(user_input)
        elif intent == "DELETE_TASK":
            handle_task_deletion(user_input)
        elif intent == "SEARCH_TASKS":
            print("🔎 Task searching not yet implemented")
        else:
            print("❓ I'm not sure what you want to do. Try being more specific.")
            print("💡 Examples:")
            print("   • 'Add a task' - to create new tasks")
            print("   • 'Show my tasks' - to view existing tasks")
            print("   • 'Update task' - to modify existing tasks")
            print("   • 'Delete task' - to remove existing tasks")


if __name__ == "__main__":
    main()
