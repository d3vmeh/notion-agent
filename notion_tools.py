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

def get_tasks_from_notion(filters=None, sort_by=None, limit=50):
    """
    Retrieve tasks from Notion database with optional filtering and sorting.
    
    Args:
        filters (dict): Filter criteria (e.g., {"category": "Fitness", "status": "To-Do"})
        sort_by (dict): Sort criteria (e.g., {"property": "Due Date", "direction": "ascending"})
        limit (int): Maximum number of tasks to return
    
    Returns:
        dict: Dictionary with tasks list and metadata
    """
    if not notion:
        return {"error": "Notion client not initialized"}
    
    try:
        filter_conditions = []
        if filters:
            for property_name, value in filters.items():
                if property_name == "category":
                    filter_conditions.append({
                        "property": "Category",
                        "select": {"equals": value}
                    })
                elif property_name == "priority":
                    filter_conditions.append({
                        "property": "Priority", 
                        "select": {"equals": value}
                    })
                elif property_name == "status":
                    filter_conditions.append({
                        "property": "Status",
                        "select": {"equals": value}
                    })
                elif property_name == "date_range":
                    start_date, end_date = value
                    filter_conditions.append({
                        "property": "Due Date",
                        "date": {
                            "on_or_after": start_date,
                            "on_or_before": end_date
                        }
                    })
        
        sorts = []
        if sort_by:
            if sort_by.get("property") == "due_date":
                sorts.append({
                    "property": "Due Date",
                    "direction": sort_by.get("direction", "ascending")
                })
            elif sort_by.get("property") == "priority":
                sorts.append({
                    "property": "Priority",
                    "direction": sort_by.get("direction", "descending")
                })
        
        if not sorts:
            sorts.append({
                "property": "Due Date",
                "direction": "ascending"
            })
        
        print(f"🔍 Querying Notion database: {database_id}")
        print(f"📊 Filters: {filter_conditions}")
        print(f"📈 Sort: {sorts}")
        print(f"📏 Limit: {limit}")
        
        response = notion.databases.query(
            database_id=database_id,
            filter={"and": filter_conditions} if filter_conditions else None,
            sorts=sorts,
            page_size=limit
        )
        
        tasks = []
        for page in response["results"]:
            properties = page["properties"]
            
            task_name = ""
            if properties.get("Task", {}).get("title"):
                task_name = properties["Task"]["title"][0]["text"]["content"]
            
            due_date = None
            if properties.get("Due Date", {}).get("date", {}).get("start"):
                due_date = properties["Due Date"]["date"]["start"]
            
            priority = ""
            if properties.get("Priority", {}).get("select"):
                priority = properties["Priority"]["select"]["name"]
            
            category = ""
            if properties.get("Category", {}).get("select"):
                category = properties["Category"]["select"]["name"]
            
            status = ""
            if properties.get("Status", {}).get("select"):
                status = properties["Status"]["select"]["name"]
            
            notes = ""
            if properties.get("Notes Page", {}).get("rich_text"):
                notes = properties["Notes Page"]["rich_text"][0]["text"]["content"]
            
            tasks.append({
                "id": page["id"],
                "task_name": task_name,
                "due_date": due_date,
                "priority": priority,
                "category": category,
                "status": status,
                "notes": notes,
                "created_time": page["created_time"],
                "last_edited_time": page["last_edited_time"]
            })
        
        print(f"✅ Retrieved {len(tasks)} tasks from Notion")
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "has_more": response.get("has_more", False)
        }
        
    except Exception as e:
        error_msg = f"Failed to retrieve tasks: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}

def update_task_in_notion(task_id, updates):
    if not notion:
        return {"error": "Notion client not initialized"}
    
    try:
        properties = {}
        
        if "task_name" in updates:
            properties["Task"] = {"title": [{"text": {"content": updates["task_name"]}}]}
        
        if "due_date" in updates:
            due_date = updates["due_date"]
            if isinstance(due_date, str):
                due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d %H:%M")
            
            if due_date.tzinfo is None:
                local_tz = datetime.datetime.now().astimezone().tzinfo
                due_date = due_date.replace(tzinfo=local_tz)
            
            properties["Due Date"] = {"date": {"start": due_date.isoformat()}}
        
        if "priority" in updates:
            properties["Priority"] = {"select": {"name": updates["priority"]}}
        
        if "category" in updates:
            properties["Category"] = {"select": {"name": updates["category"]}}
        
        if "status" in updates:
            properties["Status"] = {"select": {"name": updates["status"]}}
        
        if "notes" in updates:
            properties["Notes Page"] = {"rich_text": [{"text": {"content": updates["notes"]}}]}
        
        if not properties:
            return {"error": "No valid updates provided"}
        
        print(f"🔄 Updating task {task_id} with: {list(properties.keys())}")
        
        updated_page = notion.pages.update(page_id=task_id, properties=properties)
        
        print(f"✅ Task updated successfully")
        
        return {
            "status": "success",
            "task_id": task_id,
            "updated_fields": list(properties.keys())
        }
        
    except Exception as e:
        error_msg = f"Failed to update task: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}


def delete_task_from_notion(task_id):
    if not notion:
        return {"error": "Notion client not initialized"}
    
    try:
        print(f"🗑️  Archiving task {task_id}")
        
        archived_page = notion.pages.update(page_id=task_id, archived=True)
        
        print(f"✅ Task archived successfully")
        
        return {
            "status": "success",
            "task_id": task_id,
            "message": "Task archived successfully"
        }
        
    except Exception as e:
        error_msg = f"Failed to archive task: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}


def search_tasks_in_notion(query, limit=20):
    if not notion:
        return {"error": "Notion client not initialized"}
    
    try:
        print(f"🔍 Searching for tasks containing: '{query}'")
        
        response = notion.search(
            query=query,
            filter={"property": "object", "value": "page"},
            page_size=limit
        )
        
        tasks = []
        for page in response["results"]:
            if page.get("parent", {}).get("database_id") == database_id:
                properties = page["properties"]
                
                task_name = ""
                if properties.get("Task", {}).get("title"):
                    task_name = properties["Task"]["title"][0]["text"]["content"]
                
                due_date = None
                if properties.get("Due Date", {}).get("date", {}).get("start"):
                    due_date = properties["Due Date"]["date"]["start"]
                
                priority = ""
                if properties.get("Priority", {}).get("select"):
                    priority = properties["Priority"]["select"]["name"]
                
                category = ""
                if properties.get("Category", {}).get("select"):
                    category = properties["Category"]["select"]["name"]
                
                status = ""
                if properties.get("Status", {}).get("select"):
                    status = properties["Status"]["select"]["name"]
                
                tasks.append({
                    "id": page["id"],
                    "task_name": task_name,
                    "due_date": due_date,
                    "priority": priority,
                    "category": category,
                    "status": status
                })
        
        print(f"✅ Search found {len(tasks)} tasks")
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "query": query
        }
        
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}

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