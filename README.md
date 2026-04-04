# Prayer Times Display System

A multi-mosque digital display system for showing prayer times, announcements, and Adhkar. Each mosque gets its own live display URL and management portal.

## Live URLs

| Mosque | Live Display | Management Portal |
|--------|-------------|-------------------|
| Tralee | `/` | `/manage/` |
| Dublin | `/dublin` | `/dublin/manage/` |

## Features

- Real-time prayer times display (Beginning + Jamaah)
- Islamic and Gregorian date
- Multiple theme options
- Automatic Adhkar poster after each Jamaah
- Text and image announcements
- Web-based prayer time management (add, edit, delete months)
- GitHub-backed CSV storage (all changes auto-committed)

## Quick Start

### 1. Install Dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Add Prayer Times

```powershell
python manage_prayer_times.py
```

Select mosque (1 = Tralee, 2 = Dublin), then paste from your spreadsheet. Times are automatically converted, ditto marks expanded, and appended to the CSV.

### 3. Run the Application

```powershell
python app.py
```

Open browser to `http://localhost:5000` (Tralee) or `http://localhost:5000/dublin` (Dublin).

## File Structure

```
prayer-times/
├── app.py                          # Flask application (all routes)
├── prayer_time_parser.py           # Tralee + Dublin parsers
├── prayer_time_validator.py        # CSV validation utilities
├── manage_prayer_times.py          # CLI prayer time importer
├── manage_announcements.py         # CLI announcement manager
├── configure_mosque.py             # Interactive settings editor
│
├── data/
│   ├── tralee/
│   │   └── prayer_times.csv        # Tralee prayer times
│   └── dublin/
│       └── prayer_times.csv        # Dublin prayer times
│
├── static/
│   ├── styles.css
│   ├── fonts/
│   ├── images/                     # Announcement & Adhkar posters
│   ├── js/
│   │   ├── main.js                 # App bootstrap, settings fetch
│   │   ├── prayers.js              # Prayer time display logic
│   │   ├── announcements.js        # Announcement + Adhkar engine
│   │   ├── time.js                 # Clock and date helpers
│   │   ├── themes.js               # Theme switcher
│   │   └── utils.js                # Shared utilities
│   └── data/
│       ├── tralee/
│       │   ├── settings.json       # Tralee settings (Jumuah, Adhkar, …)
│       │   └── announcements.json  # Tralee announcements
│       └── dublin/
│           ├── settings.json       # Dublin settings
│           └── announcements.json  # Dublin announcements
│
└── templates/
    ├── index.html                  # Live display (shared, mosque-aware)
    └── manage/
        └── index.html              # Web management portal
```

## Web Management Portal

Visit `/manage/` (Tralee) or `/dublin/manage/` (Dublin) in a browser.

**What you can do:**
- View prayer times grouped by month
- Add a new month by pasting from Excel
- Edit any row in-place (click the ✏️ button)
- Delete an entire month
- All changes are committed to GitHub automatically

## CLI Tools

### Prayer Time Importer

```powershell
python manage_prayer_times.py
```

Prompts for mosque selection at startup. Options:
1. View current prayer times
2. Add new month (paste from spreadsheet)
3. Validate CSV data
4. Create backup
5. Switch mosque

**Tralee format** — Paste including the month header row and column headers:
```
April 2025
Date    Fajr Begin  ...
1       04:32       ...
```

**Dublin format** — Paste tab-separated data without a month header (month is selected separately). Jamaah times are computed automatically as Beginning + 10 min.

### Announcement Manager

```powershell
python manage_announcements.py
```

Options: view, add text, add image, delete, toggle visibility.

### Mosque Configuration

```powershell
python configure_mosque.py
```

Interactive editor for Jumuah times, Adhkar settings, and timezone.

## Settings Files

Each mosque has its own `static/data/{slug}/settings.json`. Key fields:

```json
{
  "jumuah": {
    "summer": "13:45",
    "winter": "13:20"
  },
  "adhkar": {
    "delayAfterJamaah": 8,
    "displayWindowMinutes": 4,
    "poster1Seconds": 120
  },
  "scheduledRefreshTimes": ["00:01", "06:00"]
}
```

## Adhkar System

Adhkar posters are displayed automatically after each Jamaah prayer:

- **Delay**: configurable (default 8 min after Jamaah)
- **Window**: configurable (default 4 min total)
- **Two posters**: poster 1 shown for `poster1Seconds`, poster 2 for the remainder
- **Friday Zohr**: uses special times (`fridayZohrSummer` / `fridayZohrWinter`)

Poster images are loaded from `/static/images/` — update the paths in `settings.json`.

## Adding a New Mosque

1. Create `data/{slug}/prayer_times.csv` (copy headers from an existing one)
2. Create `static/data/{slug}/settings.json` and `announcements.json`
3. Add an entry to `MOSQUE_CONFIGS` in `app.py`
4. Add routes: `@app.route('/{slug}')` and `@app.route('/{slug}/manage/')` following the existing pattern

## Troubleshooting

**Prayer times not showing?**  
Check `data/{slug}/prayer_times.csv` has a row for today's month and date.

**Adhkar not appearing?**  
Verify the poster image paths in `static/data/{slug}/settings.json` exist under `static/images/`.

**Announcements not showing?**  
Check dates and that `hide` is not `true` in `static/data/{slug}/announcements.json`.

**Edit button not working on /manage?**  
Ensure JavaScript is enabled. The edit modal uses vanilla JS — no Bootstrap JS dependency.

## License

Designed and created by [Mohammed Sajjad Khatib](https://www.linkedin.com/in/mohammedsajjadk/), free for use by any mosque.

---

**May Allah accept this work and make it a means of benefit for the Muslim community. Aameen.**
