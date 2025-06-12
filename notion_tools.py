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

def add_task_to_notion(title, due_date, priority = "Medium", category = "General", status = "To-Do"):
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Task": {"title": [{"text": {"content": title}}]},
            "Due Date": {"date": {"start": due_date.isoformat()}},
            "Priority": {"select": {"name": priority}},
            "Category": {"select": {"name": category}},
            "Status": {"select": {"name": status}}
        }
    )


#add_task_to_notion(
#    "Test Task",
#    due_date = datetime.datetime(2025, 6, 12, 15, 0),
#    priority = "High",
#    category = "Personal",
#    status = "In Progress"
#)

#print("Task added to Notion")