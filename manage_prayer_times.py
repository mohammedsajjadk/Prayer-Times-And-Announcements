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
from datetime import datetime, timedelta
import shutil

MOSQUE_CONFIGS = {
    '1': {
        'name': 'Tralee Mosque',
        'csvFile': 'data/tralee/prayer_times.csv',
        'backupDir': 'data/tralee/backups',
        'parserFormat': 'tralee',
    },
    '2': {
        'name': 'Dublin Mosque',
        'csvFile': 'data/dublin/prayer_times.csv',
        'backupDir': 'data/dublin/backups',
        'parserFormat': 'dublin',
    },
}

MONTH_MAPPING = {
    'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4,
    'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
    'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
}

MONTH_NAMES = ["","January","February","March","April","May","June",
               "July","August","September","October","November","December"]


def select_mosque():
    """Ask the user to select a mosque and return their config."""
    print("\n" + "="*60)
    print("SELECT MOSQUE")
    print("="*60)
    for key, cfg in MOSQUE_CONFIGS.items():
        print(f"{key}. {cfg['name']}")
    print("="*60)
    while True:
        choice = input("Enter choice: ").strip()
        if choice in MOSQUE_CONFIGS:
            return MOSQUE_CONFIGS[choice]
        print("Invalid choice, try again.")


def ensure_backup_dir(backup_dir):
    os.makedirs(backup_dir, exist_ok=True)


def backup_prayer_times(csv_file, backup_dir):
    ensure_backup_dir(backup_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'prayer_times_backup_{timestamp}.csv')
    shutil.copy2(csv_file, backup_file)
    print(f"✓ Backup created: {backup_file}")
    return backup_file

def view_prayer_times(csv_file):
    """Display prayer times from CSV."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return
    
    with open(csv_file, 'r') as f:
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

def add_month_from_spreadsheet(mosque_cfg):
    """Add prayer times for a month from spreadsheet data."""
    csv_file = mosque_cfg['csvFile']
    parser_format = mosque_cfg['parserFormat']

    print("\n" + "="*60)
    print(f"ADD MONTH FROM SPREADSHEET — {mosque_cfg['name']}")
    print("="*60)

    if parser_format == 'dublin':
        return _add_month_dublin(csv_file, mosque_cfg['backupDir'])

    # ── Tralee format ──
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
    
    month_name = None
    data_rows = []
    
    for line in lines:
        if not line.strip():
            continue
        upper_line = line.upper()
        for month_key in MONTH_MAPPING:
            if month_key in upper_line:
                month_name = month_key
                break
        if any(word in line.upper() for word in ['DATE', 'FAJR', 'SUNRISE', 'ZOHR']):
            continue
        parts = re.split(r'\t+|\s{2,}', line.strip())
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

    backup_prayer_times(csv_file, mosque_cfg['backupDir'])

    converted_rows = []
    previous_row = None
    
    for parts in data_rows:
        if len(parts) < 13:
            print(f"Warning: Skipping incomplete row: {parts}")
            continue
        date = parts[0]
        fajr_beg  = parts[3]; sunrise   = parts[4]; zohr_beg  = parts[5]
        asr_beg   = parts[6]; magrib_beg = parts[7]; isha_beg  = parts[8]
        fajr_j    = parts[9]; zohr_j    = parts[10]; asr_j     = parts[11]
        magrib_j  = parts[12]; isha_j   = parts[13] if len(parts) > 13 else parts[11]
        
        def r(v, pidx):
            return convert_time_format(v) if v != '"' else (previous_row[pidx] if previous_row else None)
        
        fajr_beg  = r(fajr_beg,  2); sunrise   = r(sunrise,   3); zohr_beg  = r(zohr_beg,  4)
        asr_beg   = r(asr_beg,   5); magrib_beg = r(magrib_beg,6); isha_beg  = r(isha_beg,  7)
        fajr_j    = r(fajr_j,    8); zohr_j    = r(zohr_j,    9); asr_j     = r(asr_j,    10)
        magrib_j  = r(magrib_j, 11); isha_j    = r(isha_j,   12)
        
        row = [month_num, date, fajr_beg, sunrise, zohr_beg, asr_beg, magrib_beg, isha_beg,
               fajr_j, zohr_j, asr_j, magrib_j, isha_j]
        converted_rows.append(row)
        previous_row = row

    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        for row in converted_rows:
            writer.writerow(row)

    print(f"\n✓ Successfully added {len(converted_rows)} days for {month_name}!")
    print(f"✓ Prayer times have been appended to {csv_file}")


def _add_month_dublin(csv_file, backup_dir):
    """Add a month for Dublin mosque (Beginning times only; Jamaat = Beginning + 10 min)."""
    print("""
Instructions (Dublin format):
1. Paste the timetable table (Day/Date/Fajr/Sunrise/Dhuhr/Asr/Maghrib/Isha columns)
2. Select the month when prompted
3. Press Enter, then type 'END' and press Enter again

Jamaat times will be calculated automatically as Beginning + 10 minutes.
    """)

    print("Select month:")
    for i, name in enumerate(MONTH_NAMES[1:], 1):
        print(f"  {i:>2}. {name}")
    while True:
        try:
            month_num = int(input("Month number (1-12): ").strip())
            if 1 <= month_num <= 12:
                break
            print("Enter a number between 1 and 12.")
        except ValueError:
            print("Invalid input.")

    print("\nPaste the table data (type 'END' on a new line when done):")
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

    from prayer_time_parser import DublinPrayerTimeParser
    parser = DublinPrayerTimeParser()
    csv_output = parser.parse_input('\n'.join(lines), month_num)

    # Parse the CSV output back to rows (skip header)
    out_lines = csv_output.strip().split('\n')
    new_rows = [line.split(',') for line in out_lines[1:] if line.strip()]

    if not new_rows:
        print("ERROR: No data rows could be parsed!")
        return

    print(f"\nParsed {len(new_rows)} days for {MONTH_NAMES[month_num]}")
    backup_prayer_times(csv_file, backup_dir)

    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        for row in new_rows:
            writer.writerow(row)

    print(f"\n✓ Successfully added {len(new_rows)} days for {MONTH_NAMES[month_num]}!")
    print(f"✓ Prayer times have been appended to {csv_file}")

def validate_prayer_times(csv_file):
    """Validate prayer times using PrayerTimeValidator."""
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return

    from prayer_time_validator import PrayerTimeValidator

    print("\n" + "="*60)
    print("VALIDATING PRAYER TIMES")
    print("="*60)

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        available_months = sorted({int(row['MONTH']) for row in reader})

    if not available_months:
        print("\nNo data found in the CSV file.")
        return

    print(f"\nAvailable months: {', '.join(f'{m} ({MONTH_NAMES[m]})' for m in available_months)}")
    print("\nOptions:")
    print("  • Enter a month number (1-12) to validate a specific month")
    print("  • Enter 'all' to validate every available month")
    print("  • Enter 'back' to return to the menu")

    validator = PrayerTimeValidator(csv_file)

    while True:
        choice = input("\nYour choice: ").strip().lower()
        if choice == 'back':
            break
        elif choice == 'all':
            for month in available_months:
                validator.print_validation_report(validator.validate_month(month))
            break
        else:
            try:
                month = int(choice)
                if not (1 <= month <= 12):
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
    mosque_cfg = select_mosque()
    csv_file = mosque_cfg['csvFile']
    backup_dir = mosque_cfg['backupDir']

    while True:
        print("\n" + "="*60)
        print(f"PRAYER TIME MANAGER — {mosque_cfg['name']}")
        print("="*60)
        print("1. View current prayer times")
        print("2. Add new month from spreadsheet")
        print("3. Validate prayer times")
        print("4. Create backup")
        print("5. Switch mosque")
        print("6. Exit")
        print("="*60)

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == '1':
            view_prayer_times(csv_file)
        elif choice == '2':
            add_month_from_spreadsheet(mosque_cfg)
        elif choice == '3':
            validate_prayer_times(csv_file)
        elif choice == '4':
            backup_prayer_times(csv_file, backup_dir)
        elif choice == '5':
            mosque_cfg = select_mosque()
            csv_file = mosque_cfg['csvFile']
            backup_dir = mosque_cfg['backupDir']
        elif choice == '6':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice! Please try again.")

if __name__ == "__main__":
    main_menu()
