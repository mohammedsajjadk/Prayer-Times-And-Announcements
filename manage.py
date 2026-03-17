"""
MOSQUE DISPLAY SYSTEM - MANAGEMENT CONSOLE
==========================================

Central management tool for the Prayer Times Display System.
Provides easy access to all management functions.

FEATURES:
---------
- Manage announcements (add, edit, delete, toggle visibility)
- Manage prayer times (add months, validate, backup)
- View system status
- Quick access to all management tools

HOW TO USE:
-----------
Run: python manage.py

Then select from the menu options.
"""

import subprocess
import os
import sys

def run_script(script_name):
    """Run a Python script."""
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError running {script_name}: {e}")
    except FileNotFoundError:
        print(f"\nError: {script_name} not found!")

def view_system_status():
    """Display system status."""
    print("\n" + "="*60)
    print("SYSTEM STATUS")
    print("="*60)
    
    # Check announcements file
    ann_file = 'static/data/announcements.json'
    if os.path.exists(ann_file):
        import json
        with open(ann_file, 'r') as f:
            announcements = json.load(f)
        active_count = sum(1 for a in announcements if not a.get('hide', False))
        total_count = len(announcements)
        print(f"\n📢 Announcements: {active_count} active out of {total_count} total")
    else:
        print(f"\n❌ Announcements file not found: {ann_file}")
    
    # Check prayer times file
    prayer_file = 'data/prayer_times.csv'
    if os.path.exists(prayer_file):
        with open(prayer_file, 'r') as f:
            lines = f.readlines()
        print(f"📿 Prayer Times: {len(lines) - 1} days configured")
    else:
        print(f"❌ Prayer times file not found: {prayer_file}")
    
    # Check images directory
    images_dir = 'static/images'
    if os.path.exists(images_dir):
        images = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"🖼️  Images: {len(images)} files in {images_dir}")
    else:
        print(f"❌ Images directory not found: {images_dir}")
    
    # Check if Adhkar poster exists
    adhkar_poster = 'static/images/Adhkar.jpg'
    if os.path.exists(adhkar_poster):
        print(f"✓ Adhkar poster found: {adhkar_poster}")
    else:
        print(f"⚠️  Adhkar poster not found: {adhkar_poster}")
    
    print("\n" + "="*60)

def show_help():
    """Display help information."""
    print("\n" + "="*60)
    print("HELP & DOCUMENTATION")
    print("="*60)
    print("""
MANAGEMENT TOOLS:
1. Announcement Manager (manage_announcements.py)
   - Add, edit, delete announcements
   - Toggle visibility
   - Supports text and image announcements

2. Prayer Time Manager (manage_prayer_times.py)
   - Add prayer times from Excel spreadsheet
   - Validate existing times
   - Create backups

3. Mosque Configuration (configure_mosque.py)
   - Configure mosque name and location
   - Set timezone and DST rules
   - Customize Jumuah times
   - Adjust Adhkar settings

FILE LOCATIONS:
- Configuration: mosque_config.json
- Announcements: static/data/announcements.json
- Prayer Times: data/prayer_times.csv
- Images: static/images/
- Main App: app.py

TO RUN THE APP:
python app.py
(Then open browser to http://localhost:5000)

FOR MORE INFO:
See SETUP_GUIDE.md for complete documentation
    """)
    print("="*60)

def main_menu():
    """Display main menu and handle user choice."""
    while True:
        print("\n" + "="*70)
        print(" " * 15 + "🕌 MOSQUE DISPLAY SYSTEM - MANAGEMENT CONSOLE 🕌")
        print("="*70)
        print()
        print("  📢  ANNOUNCEMENT MANAGEMENT")
        print("      1. Manage Announcements (add, edit, delete)")
        print()
        print("  📿  PRAYER TIME MANAGEMENT")  
        print("      2. Manage Prayer Times (add months, validate)")
        print()
        print("  ⚙️   CONFIGURATION")
        print("      3. Configure Mosque Settings (name, timezone, Jumuah)")
        print()
        print("  📊  SYSTEM")
        print("      4. View System Status")
        print("      5. Help & Documentation")
        print("      6. Exit")
        print()
        print("="*70)
        
        choice = input("\n  Enter your choice (1-6): ").strip()
        
        if choice == '1':
            run_script('manage_announcements.py')
        elif choice == '2':
            run_script('manage_prayer_times.py')
        elif choice == '3':
            run_script('configure_mosque.py')
        elif choice == '4':
            view_system_status()
        elif choice == '5':
            show_help()
        elif choice == '6':
            print("\n  ✨ May Allah accept your efforts! Goodbye! ✨\n")
            break
        else:
            print("\n  ❌ Invalid choice! Please try again.")

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║              MOSQUE DISPLAY SYSTEM - MANAGEMENT CONSOLE            ║
║                                                                    ║
║                        بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ                   ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    main_menu()
