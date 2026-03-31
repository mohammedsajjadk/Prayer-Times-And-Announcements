"""
PRAYER TIME MANAGER
===================

Interactive tool for managing prayer times in prayer_times.csv.
Makes it easy to add new months of prayer times from Imam Sahab's spreadsheet.

HOW TO USE:
-----------
Run: python manage_prayer_times.py

The tool will guide you through:
1. Viewing current prayer times
2. Adding a new month from spreadsheet data
3. Validating prayer times
4. Backup and restore

REQUIREMENTS:
-------------
- Copy the prayer time table from "Salah Template.xlsx" including headers
- Include the month name at the top
- The script will handle all conversions automatically
"""

import csv
import os
import re
from datetime import datetime
import shutil

CSV_FILE = 'data/prayer_times.csv'
BACKUP_DIR = 'data/backups'

MONTH_MAPPING = {
    'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4,
    'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
    'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
}

def ensure_backup_dir():
    """Create backup directory if it doesn't exist."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def backup_prayer_times():
    """Create a backup of the current prayer times."""
    ensure_backup_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'prayer_times_backup_{timestamp}.csv')
    shutil.copy2(CSV_FILE, backup_file)
    print(f"✓ Backup created: {backup_file}")
    return backup_file

def view_prayer_times():
    """Display prayer times from CSV."""
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found!")
        return
    
    with open(CSV_FILE, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        print("\n" + "="*120)
        print("CURRENT PRAYER TIMES")
        print("="*120)
        print(f"{'Month':<6} {'Date':<5} {'Fajr Beg':<10} {'Sunrise':<10} {'Zohr Beg':<10} {'Asr Beg':<10} {'Mag Beg':<10} {'Isha Beg':<10}")
        print("-"*120)
        
        for row in reader:
            if len(row) >= 8:
                print(f"{row[0]:<6} {row[1]:<5} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]:<10} {row[6]:<10} {row[7]:<10}")
        
        print("="*120 + "\n")

def convert_time_format(time_str):
    """Convert various time formats to HH:MM 24-hour format."""
    time_str = time_str.strip()
    
    # Handle empty or placeholder times
    if not time_str or time_str == '"':
        return None
    
    # Already in 24-hour format (HH:MM)
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        hours, mins = map(int, time_str.split(':'))
        return f"{hours:02d}:{mins:02d}"
    
    # Format like "5.15" or "2.00"  (means 5:15 PM or 2:00 PM in 24-hour)
    if re.match(r'^\d{1,2}\.\d{2}$', time_str):
        hours, mins = map(int, time_str.split('.'))
        # These are typically afternoon times, so add 12 if less than 12
        if hours < 12:
            hours += 12
        return f"{hours:02d}:{mins:02d}"
    
    return time_str

def add_month_from_spreadsheet():
    """Add prayer times for a month from spreadsheet data."""
    print("\n" + "="*60)
    print("ADD MONTH FROM SPREADSHEET")
    print("="*60)
    print("""
Instructions:
1. Open 'Salah Template.xlsx'
2. Select the ENTIRE table including month name and headers
3. Copy it (Ctrl+C)
4. Paste it below when prompted
5. Press Enter, then type 'END' and press Enter again
    """)
    
    print("Paste the table data (type 'END' on a new line when done):")
    print("-" * 60)
    
    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        lines.append(line)
    
    if not lines:
        print("No data entered!")
        return
    
    # Parse the data
    month_name = None
    data_rows = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        
        # Check if this is the month line
        upper_line = line.upper()
        for month_key in MONTH_MAPPING:
            if month_key in upper_line:
                month_name = month_key
                break
        
        # Skip header line
        if any(word in line.upper() for word in ['DATE', 'FAJR', 'SUNRISE', 'ZOHR']):
            continue
        
        # Split by tabs (from Excel) or multiple spaces
        parts = re.split(r'\t+|\s{2,}', line.strip())
        
        # This should be a data row if it starts with a number
        if parts and parts[0].isdigit():
            data_rows.append(parts)
    
    if not month_name:
        print("ERROR: Could not find month name in the pasted data!")
        return
    
    if not data_rows:
        print("ERROR: No data rows found!")
        return
    
    month_num = MONTH_MAPPING[month_name]
    print(f"\nParsing {month_name} (Month {month_num})...")
    print(f"Found {len(data_rows)} days of data")
    
    # Create backup before adding new data
    backup_prayer_times()
    
    # Process and add the data
    converted_rows = []
    previous_row = None
    
    for parts in data_rows:
        if len(parts) < 13:
            print(f"Warning: Skipping incomplete row: {parts}")
            continue
        
        date = parts[0]
        
        # Extract times (indices based on typical spreadsheet layout)
        fajr_beg = parts[3]
        sunrise = parts[4]
        zohr_beg = parts[5]
        asr_beg = parts[6]
        magrib_beg = parts[7]
        isha_beg = parts[8]
        fajr_j = parts[9]
        zohr_j = parts[10]
        asr_j = parts[11]
        magrib_j = parts[12]
        isha_j = parts[13] if len(parts) > 13 else parts[11]
        
        # Convert times, handling ditto marks
        fajr_beg = convert_time_format(fajr_beg) if fajr_beg != '"' else (previous_row[2] if previous_row else None)
        sunrise = convert_time_format(sunrise) if sunrise != '"' else (previous_row[3] if previous_row else None)
        zohr_beg = convert_time_format(zohr_beg) if zohr_beg != '"' else (previous_row[4] if previous_row else None)
        asr_beg = convert_time_format(asr_beg) if asr_beg != '"' else (previous_row[5] if previous_row else None)
        magrib_beg = convert_time_format(magrib_beg) if magrib_beg != '"' else (previous_row[6] if previous_row else None)
        isha_beg = convert_time_format(isha_beg) if isha_beg != '"' else (previous_row[7] if previous_row else None)
        fajr_j = convert_time_format(fajr_j) if fajr_j != '"' else (previous_row[8] if previous_row else None)
        zohr_j = convert_time_format(zohr_j) if zohr_j != '"' else (previous_row[9] if previous_row else None)
        asr_j = convert_time_format(asr_j) if asr_j != '"' else (previous_row[10] if previous_row else None)
        magrib_j = convert_time_format(magrib_j) if magrib_j != '"' else (previous_row[11] if previous_row else None)
        isha_j = convert_time_format(isha_j) if isha_j != '"' else (previous_row[12] if previous_row else None)
        
        row = [month_num, date, fajr_beg, sunrise, zohr_beg, asr_beg, magrib_beg, isha_beg, 
               fajr_j, zohr_j, asr_j, magrib_j, isha_j]
        
        converted_rows.append(row)
        previous_row = row
    
    # Append to CSV file
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        for row in converted_rows:
            writer.writerow(row)
    
    print(f"\n✓ Successfully added {len(converted_rows)} days for {month_name}!")
    print(f"✓ Prayer times have been appended to {CSV_FILE}")

def validate_prayer_times():
    """Validate prayer times using PrayerTimeValidator."""
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found!")
        return

    from prayer_time_validator import PrayerTimeValidator

    print("\n" + "="*60)
    print("VALIDATING PRAYER TIMES")
    print("="*60)

    # Find out which months are available in the CSV
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        available_months = sorted({int(row['MONTH']) for row in reader})

    if not available_months:
        print("\nNo data found in the CSV file.")
        return

    month_names = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    print(f"\nAvailable months: {', '.join(f'{m} ({month_names[m]})' for m in available_months)}")
    print("\nOptions:")
    print("  • Enter a month number (1-12) to validate a specific month")
    print("  • Enter 'all' to validate every available month")
    print("  • Enter 'back' to return to the menu")

    validator = PrayerTimeValidator(CSV_FILE)

    while True:
        choice = input("\nYour choice: ").strip().lower()

        if choice == 'back':
            break
        elif choice == 'all':
            for month in available_months:
                results = validator.validate_month(month)
                validator.print_validation_report(results)
            break
        else:
            try:
                month = int(choice)
                if month < 1 or month > 12:
                    print("Please enter a number between 1 and 12.")
                    continue
                results = validator.validate_month(month)
                if "error" in results:
                    print(f"\n  {results['error']}")
                    print(f"  Available months: {', '.join(str(m) for m in available_months)}")
                else:
                    validator.print_validation_report(results)
                break
            except ValueError:
                print("Invalid input. Enter a month number, 'all', or 'back'.")

def main_menu():
    """Display main menu and handle user choice."""
    while True:
        print("\n" + "="*60)
        print("PRAYER TIME MANAGER")
        print("="*60)
        print("1. View current prayer times")
        print("2. Add new month from spreadsheet")
        print("3. Validate prayer times")
        print("4. Create backup")
        print("5. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            view_prayer_times()
        elif choice == '2':
            add_month_from_spreadsheet()
        elif choice == '3':
            validate_prayer_times()
        elif choice == '4':
            backup_prayer_times()
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice! Please try again.")

if __name__ == "__main__":
    main_menu()
