from notion_client import Client
import datetime
import os


#notion = Client(auth=os.getenv("notion_token"))
#database_id = os.getenv("notion_database_id")

#Only for debugging purposes, use environment variables later.
f = open("ids.txt", "r")
notion_token = f.readline().strip()
database_id = f.readline().strip()
f.close()


notion = Client(auth=notion_token)

def add_tasks_to_notion(tasks):
    results = []
    for task in tasks:
        try:
            due_date = task['due_date']
            if isinstance(due_date, str):
                due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d %H:%M")
            
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