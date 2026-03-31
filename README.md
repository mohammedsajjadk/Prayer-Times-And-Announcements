# Prayer Times Display System

A comprehensive digital display system for mosques to show prayer times, announcements, and Adhkar.

## Features

✨ **Dynamic Prayer Times Display**
- Automatic daily prayer time updates
- Supports both Beginning and Jamaah times
- Islamic and Gregorian date display
- Multiple theme options

📢 **Announcement Management**
- Text and image announcements
- Date-based and recurring weekly schedules
- Seasonal timing support
- Priority and visibility controls

🕌 **Adhkar Display**
- Automatic display after each Jamaah
- Customizable timing and duration
- Special Friday Zohr scheduling
- Image poster support

⚙️ **Mosque Configurable**
- Easy configuration for any mosque
- Timezone and DST support
- Customizable Jumuah times
- Theme customization

🛠️ **Management Tools**
- Interactive announcement manager
- Prayer time import tool
- Configuration manager
- Backup and restore utilities

## Quick Start

### 1. Install Dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Your Mosque

```powershell
python configure_mosque.py
```

Follow the prompts to set:
- Mosque name and location
- Timezone
- Jumuah times (summer/winter)
- Adhkar settings

### 3. Add Prayer Times

```powershell
python manage_prayer_times.py
```

- Copy prayer times from your Excel spreadsheet
- Paste when prompted
- System automatically converts and validates times

### 4. Add Announcements

```powershell
python manage_announcements.py
```

- Add text or image announcements
- Set start/end dates and times
- Configure display frequency

### 5. Run the Application

```powershell
python app.py
```

Open browser to: `http://localhost:5000`

## File Structure

```
prayer-times/
├── app.py                      # Main Flask application
├── mosque_config.json          # Mosque configuration
├── manage.py                   # Master management console
├── manage_announcements.py     # Announcement manager
├── manage_prayer_times.py      # Prayer time manager
├── configure_mosque.py         # Mosque configuration tool
│
├── data/
│   └── prayer_times.csv        # Prayer times database
│
├── static/
│   ├── css/
│   │   └── styles.css         # Styling
│   ├── js/
│   │   ├── main.js            # Main application logic
│   │   ├── announcements.js   # Announcement handling
│   │   ├── prayers.js         # Prayer time logic
│   │   └── themes.js          # Theme management
│   ├── images/
│   │   └── Adhkar.jpg         # Adhkar poster (REQUIRED)
│   └── data/
│       └── announcements.json # Announcements database
│
└── templates/
    └── index.html             # Main display template
```

## Management Tools

### Master Console (`manage.py`)

Central hub for all management tasks:
```powershell
python manage.py
```

**Features:**
- Access all management tools
- View system status
- Quick help and documentation

### Announcement Manager (`manage_announcements.py`)

Manage announcements interactively:
```powershell
python manage_announcements.py
```

**Options:**
1. View all announcements
2. Add new text announcement
3. Add new image announcement
4. Delete announcement
5. Toggle visibility (hide/show)

### Prayer Time Manager (`manage_prayer_times.py`)

Import and manage prayer times:
```powershell
python manage_prayer_times.py
```

**Options:**
1. View current times
2. Add new month from spreadsheet
3. Validate prayer times
4. Create backup

### Mosque Configuration (`configure_mosque.py`)

Configure mosque-specific settings:
```powershell
python configure_mosque.py
```

**Settings:**
- Mosque name and location
- Timezone and DST rules
- Jumuah times (summer/winter)
- Adhkar display settings
- Display customization

## Configuration Guide

### Mosque Settings (`mosque_config.json`)

```json
{
  "mosque": {
    "name": "Your Masjid Name",
    "location": "Your City, Country",
    "displayName": "Display Name"
  },
  "timezone": {
    "name": "Your/Timezone",
    "hasDST": true,
    "standardOffset": 0,
    "dstOffset": 1
  },
  "jumuah": {
    "summer": {"time": "13:45"},
    "winter": {"time": "13:20"}
  },
  "adhkar": {
    "enabled": true,
    "delayMinutes": 8,
    "durationMinutes": 4,
    "fridayZohrSpecialTimes": {
      "summer": "14:10",
      "winter": "13:42"
    }
  }
}
```

### Adding Prayer Times

1. Open your Excel spreadsheet with prayer times
2. Select the entire table (including month name and headers)
3. Copy (Ctrl+C)
4. Run `python manage_prayer_times.py`
5. Select option 2 (Add new month from spreadsheet)
6. Paste the data
7. Type `END` and press Enter
8. System automatically:
   - Extracts month
   - Converts time formats
   - Handles ditto marks (")
   - Validates data
   - Appends to CSV

### Adding Announcements

**Text Announcement:**
```json
{
  "id": "event_2027",
  "startDate": "2027-03-15T09:00:00+01:00",
  "endDate": "2027-03-15T18:00:00+01:00",
  "message": "Your announcement message",
  "isSpecial": true
}
```

**Image Announcement:**
```json
{
  "id": "poster_2027",
  "startDate": "2027-03-15T09:00:00+01:00",
  "endDate": "2027-03-15T18:00:00+01:00",
  "type": "image",
  "images": ["/static/images/YourPoster.jpg"],
  "displayCondition": {
    "frequency": 1,
    "duration": 60,
    "avoidJamaahTime": true
  },
  "isSpecial": true
}
```

**Recurring Weekly:**
```json
{
  "id": "weekly_program",
  "type": "recurring_weekly",
  "dayOfWeek": 5,
  "seasonalTiming": {
    "summer": {
      "startReference": "fajrBeginning",
      "endReference": "ishaJamaah",
      "endOffset": 15
    },
    "winter": {
      "startReference": "fajrBeginning",
      "endReference": "ishaJamaah",
      "endOffset": 15
    }
  },
  "images": ["/static/images/Program.jpg"]
}
```

## Adhkar System

The system automatically displays the Adhkar poster (`/static/images/Adhkar.jpg`):

**Post-Jamaah Display:**
- Displays 8 minutes after each Jamaah prayer
- Duration: 4 minutes
- Applies to: Fajr, Zohr, Asr, Maghrib, Isha
- Excludes: Friday Zohr (has special timing)

**Friday Zohr Special Times:**
- Summer (DST): 14:10
- Winter: 13:42

**Note:** Make sure `static/images/Adhkar.jpg` exists!

## Common Timezones

| Region | Timezone |
|--------|----------|
| UK | Europe/London |
| Ireland | Europe/Dublin |
| UAE | Asia/Dubai |
| Pakistan | Asia/Karachi |
| India | Asia/Kolkata |
| US Eastern | America/New_York |
| US Central | America/Chicago |
| US Pacific | America/Los_Angeles |

## Troubleshooting

### Adhkar not displaying?
1. Check `static/images/Adhkar.jpg` exists
2. Verify `adhkar.enabled` is `true` in `mosque_config.json`
3. Confirm timing settings

### Prayer times not updating?
1. Run `python manage_prayer_times.py` → option 3 to validate
2. Check `data/prayer_times.csv` format
3. Ensure times are in HH:MM format

### Announcements not showing?
1. Check announcement dates are correct
2. Verify `hide` is not set to `true`
3. Confirm timezone settings

## Support and Customization

For mosque-specific customizations or support, you can:
1. Use `configure_mosque.py` for basic settings
2. Edit `mosque_config.json` directly for advanced options
3. Modify theme colors in `static/styles.css`

## License

This project was designed and created by [Mohammed Sajjad Khatib](https://www.linkedin.com/in/mohammedsajjadk/), and is free for use by any mosque.
---

**May Allah accept this work and make it a means of benefit for the Muslim community. Aameen.**
