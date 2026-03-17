"""
MOSQUE CONFIGURATION MANAGER
=============================

Interactive tool for configuring mosque-specific settings.
Allows customization of timezone, Jumuah times, display options, and more.

HOW TO USE:
-----------
Run: python configure_mosque.py

The tool will guide you through updating:
- Mosque name and location
- Timezone and DST rules
- Jumuah prayer times (summer/winter)
- Adhkar display settings
- Display customization
"""

import json
import os

CONFIG_FILE = 'mosque_config.json'

def load_config():
    """Load current configuration."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found!")
        return None
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Configuration saved to {CONFIG_FILE}")

def view_config(config):
    """Display current configuration."""
    print("\n" + "="*60)
    print("CURRENT CONFIGURATION")
    print("="*60)
    print(f"\nMosque Name: {config['mosque']['name']}")
    print(f"Location: {config['mosque']['location']}")
    print(f"Display Name: {config['mosque']['displayName']}")
    print(f"\nTimezone: {config['timezone']['name']}")
    print(f"Has DST: {config['timezone']['hasDST']}")
    print(f"\nJumuah Time (Summer): {config['jumuah']['summer']['time']}")
    print(f"Jumuah Time (Winter): {config['jumuah']['winter']['time']}")
    print(f"\nAdhkar Enabled: {config['adhkar']['enabled']}")
    print(f"Adhkar Delay After Jamaah: {config['adhkar']['delayMinutes']} minutes")
    print("="*60)

def configure_mosque_details(config):
    """Configure mosque name and location."""
    print("\n" + "="*60)
    print("CONFIGURE MOSQUE DETAILS")
    print("="*60)
    
    print(f"\nCurrent mosque name: {config['mosque']['name']}")
    new_name = input("Enter new mosque name (or press Enter to keep current): ").strip()
    if new_name:
        config['mosque']['name'] = new_name
        config['mosque']['displayName'] = new_name
    
    print(f"\nCurrent location: {config['mosque']['location']}")
    new_location = input("Enter new location (or press Enter to keep current): ").strip()
    if new_location:
        config['mosque']['location'] = new_location
    
    save_config(config)

def configure_jumuah_times(config):
    """Configure Jumuah prayer times."""
    print("\n" + "="*60)
    print("CONFIGURE JUMUAH TIMES")
    print("="*60)
    
    print(f"\nCurrent Summer Jumuah time: {config['jumuah']['summer']['time']}")
    summer_time = input("Enter new summer Jumuah time (HH:MM format, or press Enter to keep): ").strip()
    if summer_time:
        config['jumuah']['summer']['time'] = summer_time
    
    print(f"\nCurrent Winter Jumuah time: {config['jumuah']['winter']['time']}")
    winter_time = input("Enter new winter Jumuah time (HH:MM format, or press Enter to keep): ").strip()
    if winter_time:
        config['jumuah']['winter']['time'] = winter_time
    
    save_config(config)

def configure_adhkar_settings(config):
    """Configure Adhkar display settings."""
    print("\n" + "="*60)
    print("CONFIGURE ADHKAR SETTINGS")
    print("="*60)
    
    print(f"\nAdhkar currently: {'ENABLED' if config['adhkar']['enabled'] else 'DISABLED'}")
    enable = input("Enable Adhkar display? (y/n): ").strip().lower()
    if enable in ['y', 'n']:
        config['adhkar']['enabled'] = (enable == 'y')
    
    print(f"\nCurrent delay after Jamaah: {config['adhkar']['delayMinutes']} minutes")
    delay = input("Enter new delay in minutes (or press Enter to keep): ").strip()
    if delay.isdigit():
        config['adhkar']['delayMinutes'] = int(delay)
    
    print(f"\nCurrent display duration: {config['adhkar']['durationMinutes']} minutes")
    duration = input("Enter new duration in minutes (or press Enter to keep): ").strip()
    if duration.isdigit():
        config['adhkar']['durationMinutes'] = int(duration)
    
    print(f"\nCurrent Friday Zohr summer time: {config['adhkar']['fridayZohrSpecialTimes']['summer']}")
    friday_summer = input("Enter new time (HH:MM) or press Enter to keep: ").strip()
    if friday_summer:
        config['adhkar']['fridayZohrSpecialTimes']['summer'] = friday_summer
    
    print(f"\nCurrent Friday Zohr winter time: {config['adhkar']['fridayZohrSpecialTimes']['winter']}")
    friday_winter = input("Enter new time (HH:MM) or press Enter to keep: ").strip()
    if friday_winter:
        config['adhkar']['fridayZohrSpecialTimes']['winter'] = friday_winter
    
    save_config(config)

def configure_timezone(config):
    """Configure timezone settings."""
    print("\n" + "="*60)
    print("CONFIGURE TIMEZONE")
    print("="*60)
    print("""
Common timezones:
- Europe/London (UK)
- Europe/Dublin (Ireland)
- America/New_York (US Eastern)
- America/Chicago (US Central)
- America/Los_Angeles (US Pacific)
- Asia/Dubai (UAE)
- Asia/Karachi (Pakistan)
- Asia/Kolkata (India)
    """)
    
    print(f"\nCurrent timezone: {config['timezone']['name']}")
    new_tz = input("Enter new timezone (or press Enter to keep current): ").strip()
    if new_tz:
        config['timezone']['name'] = new_tz
    
    print(f"\nDoes this timezone use DST? Currently: {config['timezone']['hasDST']}")
    has_dst = input("Use DST? (y/n): ").strip().lower()
    if has_dst in ['y', 'n']:
        config['timezone']['hasDST'] = (has_dst == 'y')
    
    save_config(config)

def reset_to_defaults():
    """Reset configuration to default Tralee Masjid settings."""
    print("\n" + "="*60)
    print("RESET TO DEFAULTS")
    print("="*60)
    print("\nWARNING: This will reset all settings to default Tralee Masjid configuration!")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        default_config = {
            "mosque": {
                "name": "Tralee Masjid",
                "location": "Tralee, Ireland",
                "displayName": "Tralee Masjid"
            },
            "timezone": {
                "name": "Europe/Dublin",
                "hasDST": True,
                "dstRules": {
                    "description": "Ireland DST: Last Sunday in March to last Sunday in October",
                    "startMonth": 3,
                    "startRule": "lastSunday",
                    "endMonth": 10,
                    "endRule": "lastSunday"
                },
                "standardOffset": 0,
                "dstOffset": 1
            },
            "jumuah": {
                "summer": {"time": "13:45", "description": "Jumuah time during Irish Summer Time"},
                "winter": {"time": "13:20", "description": "Jumuah time during Irish Winter Time"}
            },
            "adhkar": {
                "enabled": True,
                "posterPath": "/static/images/Adhkar.jpg",
                "displayAfterJamaah": True,
                "delayMinutes": 8,
                "durationMinutes": 4,
                "fridayZohrSpecialTimes": {"summer": "14:10", "winter": "13:42"},
                "excludeFridayZohr": False
            },
            "display": {
                "title": "Prayer Times",
                "showIslamicDate": True,
                "showGregorianDate": True,
                "defaultTheme": "theme1",
                "availableThemes": ["theme1", "theme2", "theme3", "theme4", "theme5"]
            },
            "defaults": {
                "announcementDuration": 60,
                "imageDuration": 60,
                "avoidJamaahTime": True
            }
        }
        save_config(default_config)
        print("\n✓ Configuration reset to defaults!")
    else:
        print("\nReset cancelled.")

def main_menu():
    """Display main menu and handle user choice."""
    config = load_config()
    if config is None:
        return
    
    while True:
        print("\n" + "="*60)
        print("MOSQUE CONFIGURATION MANAGER")
        print("="*60)
        print("1. View current configuration")
        print("2. Configure mosque details (name, location)")
        print("3. Configure Jumuah times (summer/winter)")
        print("4. Configure Adhkar settings")
        print("5. Configure timezone")
        print("6. Reset to defaults (Tralee Masjid)")
        print("7. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            view_config(config)
        elif choice == '2':
            configure_mosque_details(config)
            config = load_config()  # Reload after save
        elif choice == '3':
            configure_jumuah_times(config)
            config = load_config()
        elif choice == '4':
            configure_adhkar_settings(config)
            config = load_config()
        elif choice == '5':
            configure_timezone(config)
            config = load_config()
        elif choice == '6':
            reset_to_defaults()
            config = load_config()
        elif choice == '7':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice! Please try again.")

if __name__ == "__main__":
    main_menu()
