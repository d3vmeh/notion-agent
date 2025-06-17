from notion_client import Client
import datetime
import os


def extract_database_id_from_url(url):
    """Extract database ID from a Notion database URL."""
    if not url:
        return None

    parts = url.split('/')
    if len(parts) >= 4:
        database_id = parts[-1].split('?')[0]  
        if len(database_id) == 32:
            return database_id
    
    raise ValueError("Could not extract database ID from URL. Please check the URL format.")



notion_token = os.getenv("NOTION_TOKEN")
database_url = os.getenv("NOTION_DATABASE_URL")

if database_url:
    try:
        database_id = extract_database_id_from_url(database_url)
        print(f"✅ Database ID extracted: {database_id}")
    except ValueError as e:
        print(f"❌ Error extracting database ID: {e}")
        database_id = None
else:
    database_id = None

if notion_token and database_id:
    notion = Client(auth=notion_token)
else:
    notion = None
    print("❌ Notion client not initialized. Please set NOTION_TOKEN and NOTION_DATABASE_URL environment variables.")

def add_tasks_to_notion(tasks):
    if not notion:
        return [{"task": "Notion client not initialized", "status": "error", "error": "Please check your Notion credentials"}]
    
    results = []
    for task in tasks:
        try:
            due_date = task['due_date']
            if isinstance(due_date, str):
                due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d %H:%M")
                local_tz = datetime.datetime.now().astimezone().tzinfo
                due_date = due_date.replace(tzinfo=local_tz)
            
            notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Task": {"title": [{"text": {"content": task['task_name']}}]},
                    "Due Date": {"date": {"start": due_date.isoformat()}},
                    "Priority": {"select": {"name": task.get('priority', 'Medium')}},
                    "Category": {"select": {"name": task.get('category', 'General')}},
                    "Status": {"select": {"name": task.get('status', 'To-Do')}},
                    "Notes Page": {"rich_text": [{"text": {"content": task.get('notes', '')}}]}
                }
            )
            results.append({"task": task['task_name'], "status": "success"})
        except Exception as e:
            results.append({"task": task['task_name'], "status": "error", "error": str(e)})
    
    return results


#add_tasks_to_notion([
#    {
#        "task_name": "Test Task",
#        "due_date": "2025-06-14 15:00",
#        "priority": "High",
#        "category": "Personal",
#        "status": "In Progress",
#        "notes": "This is a test note"
#    }
#])

#print("Task added to Notion")