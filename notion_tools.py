from notion_client import Client
import datetime
import os


def verify_database_url(url):
    """Verify that the URL points to a database and not a page."""
    if not url:
        return False, "No URL provided"
    
    # Check if it's a database URL
    if "notion.so" not in url:
        return False, "Not a valid Notion URL"
    
    # Database URLs typically have this pattern:
    # https://www.notion.so/workspace/database-name-database-id?v=...
    # or
    # https://workspace.notion.so/database-name-database-id?v=...
    
    if "database" in url.lower():
        return True, "URL appears to be a database URL"
    
    # Extract the ID and check if it's 32 characters
    parts = url.split('/')
    if len(parts) >= 4:
        potential_id = parts[-1].split('?')[0]
        if len(potential_id) == 32:
            return True, f"URL contains a 32-character ID: {potential_id}"
    
    return False, "URL format doesn't match expected database URL pattern"


def extract_database_id_from_url(url):
    """Extract database ID from a Notion database URL."""
    if not url:
        return None

    # First verify the URL
    is_valid, message = verify_database_url(url)
    if not is_valid:
        print(f"⚠️  Warning: {message}")
        print("💡 Make sure you're using the database URL, not a page URL")
        print("   Database URL should look like: https://www.notion.so/workspace/database-name-database-id")

    parts = url.split('/')
    if len(parts) >= 4:
        database_id = parts[-1].split('?')[0]  
        if len(database_id) == 32:
            return database_id
    
    raise ValueError("Could not extract database ID from URL. Please check the URL format.")


def validate_database_id(database_id):
    """Validate that we have a proper database ID and not a page ID."""
    if not database_id:
        return False, "No database ID provided"
    
    if len(database_id) != 32:
        return False, f"Database ID should be 32 characters, got {len(database_id)}"

    return True, "Database ID appears valid"


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
    database_id = None
    print("❌ Notion client not initialized. Please set NOTION_TOKEN and NOTION_DATABASE_URL environment variables.")


def add_tasks_to_notion(tasks):
    if not notion:
        return [{"task": "Notion client not initialized", "status": "error", "error": "Please check your Notion credentials"}]
    
    is_valid, message = validate_database_id(database_id)
    if not is_valid:
        return [{"task": "Database ID validation failed", "status": "error", "error": message}]
    
    print(f"🔍 Using database ID: {database_id}")
    
    results = []
    for task in tasks:
        try:
            if not task.get('task_name'):
                raise ValueError("Task name is required")
            
            due_date = task['due_date']
            if isinstance(due_date, str):
                due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d %H:%M")
            
            if due_date.tzinfo is None:
                local_tz = datetime.datetime.now().astimezone().tzinfo
                due_date = due_date.replace(tzinfo=local_tz)
            
            page_data = {
                "parent": {"database_id": database_id},
                "properties": {
                    "Task": {"title": [{"text": {"content": task['task_name']}}]},
                    "Due Date": {"date": {"start": due_date.isoformat()}},
                    "Priority": {"select": {"name": task.get('priority', 'Medium')}},
                    "Category": {"select": {"name": task.get('category', 'General')}},
                    "Status": {"select": {"name": task.get('status', 'To-Do')}},
                    "Notes Page": {"rich_text": [{"text": {"content": task.get('notes', '')}}]}
                }
            }
            
            print(f"📝 Creating task: {task['task_name']}")
            print(f"   📅 Due: {due_date.isoformat()}")
            print(f"   🏷️  Priority: {task.get('priority', 'Medium')}")
            print(f"   📂 Category: {task.get('category', 'General')}")
            print(f"   📊 Status: {task.get('status', 'To-Do')}")
            
            created_page = notion.pages.create(**page_data)
            
            page_id = created_page['id']
            print(f"✅ Task created with ID: {page_id}")
            
            try:
                retrieved_page = notion.pages.retrieve(page_id)
                print(f"✅ Page verified in database")
            except Exception as verify_error:
                print(f"⚠️  Warning: Could not verify page: {verify_error}")
            
            results.append({"task": task['task_name'], "status": "success", "page_id": page_id})
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error creating task '{task['task_name']}': {error_msg}")
            
            if "database_id" in error_msg.lower():
                print("💡 This might be a database access issue")
            elif "properties" in error_msg.lower():
                print("💡 This might be a property name/type mismatch")
            elif "date" in error_msg.lower():
                print("💡 This might be a date format issue")
            
            results.append({"task": task['task_name'], "status": "error", "error": error_msg})
    
    successful_tasks = [r for r in results if r['status'] == 'success']
    if successful_tasks:
        print("\n" + "=" * 50)
        print("🎉 TASKS ADDED SUCCESSFULLY!")
        print("=" * 50)
        print("💡 IMPORTANT: You may need to refresh your Notion page")
        print("   to see the new tasks in your calendar view.")
        print()
        print("🔧 How to refresh:")
        print("   • Press Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)")
        print("   • Or click the refresh button in your browser")
        print("   • Or wait 30-60 seconds for Notion to auto-sync")
        print()
        print("📊 Tasks added:")
        for result in successful_tasks:
            print(f"   ✅ {result['task']}")
        print("=" * 50)
    
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