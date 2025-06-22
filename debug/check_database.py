#!/usr/bin/env python3
"""
Database URL Verification Script
Run this to check if your database URL is correct
"""

import os
from notion_tools import extract_database_id_from_url, verify_database_url, validate_database_id

def main():
    print("🔍 Database URL Verification Tool")
    print("=" * 40)
    
    # Get the database URL from environment
    database_url = os.getenv("NOTION_DATABASE_URL")
    
    if not database_url:
        print("❌ NOTION_DATABASE_URL environment variable not found!")
        print("💡 Please set it with: export NOTION_DATABASE_URL='your-database-url'")
        return
    
    print(f"📋 Database URL: {database_url}")
    print()
    
    # Verify the URL format
    is_valid_url, url_message = verify_database_url(database_url)
    print(f"🔗 URL Verification: {'✅' if is_valid_url else '❌'} {url_message}")
    
    try:
        # Extract and validate the database ID
        database_id = extract_database_id_from_url(database_url)
        print(f"🆔 Extracted Database ID: {database_id}")
        
        is_valid_id, id_message = validate_database_id(database_id)
        print(f"🆔 ID Validation: {'✅' if is_valid_id else '❌'} {id_message}")
        
        if is_valid_id:
            print("\n✅ Your database URL appears to be correct!")
            print("💡 If tasks are still disappearing, try the troubleshooting steps below.")
        else:
            print("\n❌ There's an issue with your database ID.")
            print("💡 Make sure you're using the database URL, not a page URL.")
            
    except ValueError as e:
        print(f"❌ Error extracting database ID: {e}")
    
    print("\n" + "=" * 40)
    print("🔧 TROUBLESHOOTING STEPS:")
    print("1. Make sure you're using the DATABASE URL, not a page URL")
    print("2. The URL should contain 'database' or end with a 32-character ID")
    print("3. Try accessing the database directly in Notion to verify it exists")
    print("4. Check that your Notion integration has access to this database")
    print("5. Try creating a test task manually in Notion first")

if __name__ == "__main__":
    main() 