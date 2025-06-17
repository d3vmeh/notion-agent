import requests
import os
import json
from datetime import datetime
from notion_tools import add_tasks_to_notion
from speech_tools import *
import ast

api_key = os.getenv("OPENAI_API_KEY")

def clean_json_response(response_text):
    """
    Clean the response text by removing any comments and ensuring it's valid JSON.
    """
    # Remove any lines that start with // or contain //
    lines = response_text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove any // comments from the line
        if '//' in line:
            line = line.split('//')[0]
        # Only keep non-empty lines that aren't just whitespace
        if line.strip():
            cleaned_lines.append(line)
    
    cleaned_response = '\n'.join(cleaned_lines)
    return cleaned_response.strip()


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
                    "status": "To-Do/In Progress/Completed",
                    "notes": "Additional details, description, or context about the task"
                }
            ]

            IMPORTANT RULES:
            1. The due_date must be in the format "YYYY-MM-DD HH:MM" (24-hour format)
            2. Priority must be exactly one of: "Low", "Medium", or "High" (case-sensitive)
            3. Category must be exactly one of: "General", "Personal", "Fitness", "Fun", or "School" (case-sensitive)
            4. Status must be exactly one of: "To-Do", "In Progress", or "Completed" (case-sensitive)
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
        #cleaned_response = clean_json_response(cleaned_response)
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


def get_task_input():
    while True:
        print("NOTION TASK AGENT")
        print("="*50)
        print("Choose input method:")
        print("1. 🎤 Speech input (standard)")
        print("2. 🎤 Speech input (continuous)")
        print("3. 🎤 Push-to-Talk (HOLD SPACE)")
        print("4. 🎤 Push-to-Talk (ENTER start/stop)")
        print("5. ⌨️  Text input")
        print("6. ❌ Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            print("\n🎤 Switching to speech mode (standard)...")
            print("💡 Tip: Speak clearly and pause briefly when done")
            speech_text = listen_for_speech()
            
            if speech_text:
                if speech_text == "quit":
                    print("👋 Goodbye!")
                    return None
                else:
                    return speech_text
            else:
                print("❌ Speech input failed. Please try again or choose text input.")
                continue
                
        elif choice == "2":
            print("\n🎤 Switching to speech mode (continuous)...")
            print("💡 Tip: Speak naturally and pause when finished")
            speech_text = listen_for_speech_continuous()
            
            if speech_text:
                if speech_text == "quit":
                    print("👋 Goodbye!")
                    return None
                else:
                    return speech_text
            else:
                print("❌ Speech input failed. Please try again or choose text input.")
                continue
                
        elif choice == "3":
            print("\n🎤 Switching to push-to-talk mode...")
            print("💡 Tip: HOLD DOWN SPACE while talking, RELEASE to stop")
            speech_text = listen_for_speech_true_push_to_talk()
            
            if speech_text:
                if speech_text == "quit":
                    print("👋 Goodbye!")
                    return None
                else:
                    return speech_text
            else:
                print("❌ Speech input failed. Please try again or choose text input.")
                continue
                
        elif choice == "4":
            print("\n🎤 Switching to push-to-talk mode...")
            print("💡 Tip: Press ENTER to start, press ENTER again to stop")
            speech_text = listen_for_speech_simple_push_to_talk()
            
            if speech_text:
                if speech_text == "quit":
                    print("👋 Goodbye!")
                    return None
                else:
                    return speech_text
            else:
                print("❌ Speech input failed. Please try again or choose text input.")
                continue
                
        elif choice == "5":
            print("\nText input mode:")
            text_input = input("Enter your task description: ").strip()
            
            if text_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                return None
            elif text_input:
                return text_input
            else:
                print("❌ Please enter a valid task description.")
                continue
                
        elif choice == "6":
            print("👋 Goodbye!")
            return None
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")


def main():
    print("Starting Notion Task Agent...")
    print("💡 Tips:")
    print("   - Say 'quit' to exit")
    print("   - Be specific about dates, times, and details")
    print("   - For speech: Speak clearly and pause when done")
    print("   - For push-to-talk: Use SPACE or ENTER to control recording")
    print("   - You can add multiple tasks at once by mentioning them together")
    
    while True:
        question = get_task_input()
        
        if question is None:
            break
            
        print(f"\n📝 Processing: '{question}'")
        response = request_task_addition(question)
        print(response)
        
        if "error" in response:
            print("❌ Error occurred:", response["error"])
            continue
        
        if not isinstance(response, list):
            print("❌ Unexpected response format - expected list of tasks")
            continue
        
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
                
        except Exception as e:
            print(f"❌ Error adding tasks to Notion: {e}")


if __name__ == "__main__":
    main()