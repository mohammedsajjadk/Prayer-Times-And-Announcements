"""
ANNOUNCEMENT MANAGER
=====================

Interactive tool for managing announcement entries in announcements.json.
Simplifies the process of adding, editing, and removing announcements.

HOW TO USE:
-----------
Run: python manage_announcements.py

The tool will present you with options to:
1. View all announcements
2. Add a new announcement
3. Edit an existing announcement
4. Delete an announcement
5. Toggle announcement visibility (hide/show)
"""

import json
import os
from datetime import datetime, timedelta

ANNOUNCEMENTS_FILE = 'static/data/announcements.json'

def load_announcements():
    """Load announcements from JSON file."""
    if not os.path.exists(ANNOUNCEMENTS_FILE):
        print(f"Error: {ANNOUNCEMENTS_FILE} not found!")
        return None
    
    with open(ANNOUNCEMENTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_announcements(announcements):
    """Save announcements to JSON file."""
    with open(ANNOUNCEMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(announcements, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Successfully saved to {ANNOUNCEMENTS_FILE}")

def list_announcements(announcements):
    """Display all announcements."""
    print("\n" + "="*80)
    print("CURRENT ANNOUNCEMENTS")
    print("="*80)
    
    for i, ann in enumerate(announcements, 1):
        ann_type = ann.get('type', 'date-based')
        status = "HIDDEN" if ann.get('hide', False) else "ACTIVE"
        
        print(f"\n[{i}] ID: {ann.get('id', 'N/A')} - Type: {ann_type} - Status: {status}")
        
        if ann_type == 'control':
            print(f"    Description: {ann.get('description', 'N/A')}")
        elif ann_type == 'recurring_weekly':
            days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            day = days[ann.get('dayOfWeek', 0)]
            print(f"    Day: {day}")
            if 'images' in ann:
                print(f"    Images: {', '.join(ann['images'])}")
        elif ann_type == 'image':
            print(f"    Start: {ann.get('startDate', 'N/A')}")
            print(f"    End: {ann.get('endDate', 'N/A')}")
            if 'images' in ann:
                print(f"    Images: {', '.join(ann['images'])}")
        else:
            print(f"    Start: {ann.get('startDate', 'N/A')}")
            print(f"    End: {ann.get('endDate', 'N/A')}")
            if 'message' in ann:
                print(f"    Message: {ann.get('message', 'N/A')[:60]}...")
    print("\n" + "="*80)

def add_text_announcement(announcements):
    """Add a new text announcement."""
    print("\n" + "="*60)
    print("ADD NEW TEXT ANNOUNCEMENT")
    print("="*60)
    
    ann_id = input("\nEnter announcement ID (e.g., 'ramadan_2027'): ").strip()
    
    # Check if ID already exists
    if any(a.get('id') == ann_id for a in announcements):
        print(f"ERROR: Announcement with ID '{ann_id}' already exists!")
        return
    
    message = input("Enter announcement message: ").strip()
    
    print("\nEnter start date and time (format: YYYY-MM-DD HH:MM)")
    start_date = input("Start date: ").strip()
    start_time = input("Start time (e.g., 09:00): ").strip()
    
    print("\nEnter end date and time")
    end_date = input("End date: ").strip()
    end_time = input("End time (e.g., 18:00): ").strip()
    
    is_special = input("\nIs this a special announcement? (y/n): ").strip().lower() == 'y'
    
    # Create announcement object
    new_announcement = {
        "id": ann_id,
        "startDate": f"{start_date}T{start_time}:00+01:00",
        "endDate": f"{end_date}T{end_time}:00+01:00",
        "message": message,
        "isSpecial": is_special
    }
    
    announcements.append(new_announcement)
    save_announcements(announcements)
    print(f"\n✓ Text announcement '{ann_id}' added successfully!")

def add_image_announcement(announcements):
    """Add a new image announcement."""
    print("\n" + "="*60)
    print("ADD NEW IMAGE ANNOUNCEMENT")
    print("="*60)
    
    ann_id = input("\nEnter announcement ID (e.g., 'youth_event_2027'): ").strip()
    
    # Check if ID already exists
    if any(a.get('id') == ann_id for a in announcements):
        print(f"ERROR: Announcement with ID '{ann_id}' already exists!")
        return
    
    image_path = input("Enter image path (e.g., '/static/images/MyPoster.jpg'): ").strip()
    
    print("\nEnter start date and time (format: YYYY-MM-DD HH:MM)")
    start_date = input("Start date: ").strip()
    start_time = input("Start time (e.g., 09:00): ").strip()
    
    print("\nEnter end date and time")
    end_date = input("End date: ").strip()
    end_time = input("End time (e.g., 18:00): ").strip()
    
    frequency = int(input("\nDisplay frequency in minutes (default 1): ").strip() or "1")
    duration = int(input("Display duration in seconds (default 60): ").strip() or "60")
    
    is_special = input("Is this a special announcement? (y/n): ").strip().lower() == 'y'
    avoid_jamaah = input("Avoid Jamaah times? (y/n): ").strip().lower() == 'y'
    
    # Create announcement object
    new_announcement = {
        "id": ann_id,
        "startDate": f"{start_date}T{start_time}:00+01:00",
        "endDate": f"{end_date}T{end_time}:00+01:00",
        "type": "image",
        "displayCondition": {
            "frequency": frequency,
            "duration": duration,
            "gapBetweenImages": 60,
            "avoidJamaahTime": avoid_jamaah,
            "rotateImages": True
        },
        "images": [image_path],
        "isSpecial": is_special
    }
    
    announcements.append(new_announcement)
    save_announcements(announcements)
    print(f"\n✓ Image announcement '{ann_id}' added successfully!")

def delete_announcement(announcements):
    """Delete an announcement."""
    list_announcements(announcements)
    
    try:
        index = int(input("\nEnter the number of the announcement to delete: ")) - 1
        if 0 <= index < len(announcements):
            ann = announcements[index]
            confirm = input(f"Are you sure you want to delete '{ann.get('id')}'? (y/n): ")
            if confirm.lower() == 'y':
                announcements.pop(index)
                save_announcements(announcements)
                print(f"\n✓ Announcement deleted successfully!")
        else:
            print("Invalid selection!")
    except ValueError:
        print("Invalid input!")

def toggle_visibility(announcements):
    """Toggle hide/show status of an announcement."""
    list_announcements(announcements)
    
    try:
        index = int(input("\nEnter the number of the announcement to toggle: ")) - 1
        if 0 <= index < len(announcements):
            ann = announcements[index]
            current_status = ann.get('hide', False)
            ann['hide'] = not current_status
            new_status = "HIDDEN" if ann['hide'] else "VISIBLE"
            save_announcements(announcements)
            print(f"\n✓ Announcement '{ann.get('id')}' is now {new_status}!")
        else:
            print("Invalid selection!")
    except ValueError:
        print("Invalid input!")

def main_menu():
    """Display main menu and handle user choice."""
    announcements = load_announcements()
    if announcements is None:
        return
    
    while True:
        print("\n" + "="*60)
        print("ANNOUNCEMENT MANAGER")
        print("="*60)
        print("1. View all announcements")
        print("2. Add new text announcement")
        print("3. Add new image announcement")
        print("4. Delete an announcement")
        print("5. Toggle announcement visibility (hide/show)")
        print("6. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            list_announcements(announcements)
        elif choice == '2':
            add_text_announcement(announcements)
        elif choice == '3':
            add_image_announcement(announcements)
        elif choice == '4':
            delete_announcement(announcements)
        elif choice == '5':
            toggle_visibility(announcements)
        elif choice == '6':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice! Please try again.")

if __name__ == "__main__":
    main_menu()
