# Prayer Times & Announcements Display App

Full-screen digital prayer times board for a mosque with live announcements, an automated post-Jamaah Adhkar poster, 20 colour themes, and a browser-based management console.

## Live URLs

| Mosque | Display | Management |
|--------|---------|------------|
| Tralee Islamic Centre | `/` | `/manage/` |
| Dublin Mosque | `/dublin` | `/dublin/manage/` |

## What It Does

- Rotated full-screen display: Fajr / Dhuhr / Asr / Maghrib / Isha with Beginning + Jamaah columns
- Islamic and Gregorian date, live clock, scheduled page refreshes
- Scrolling announcements: text, images, recurring weekly posters, automated post-Jamaah Adhkar
- 20 selectable colour themes stored in `settings.json`
- Management pages for prayer times, announcements, and all settings — no server access needed
- Local development mode: saves JSON files directly to disk with a single button click

## Tech Stack

Python 3 / Flask · Vanilla JS · Bootstrap 5 (admin) · CSV prayer data · JSON settings + announcements

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` (Tralee) or `http://localhost:5000/dublin` (Dublin).

## Repository Layout

```
app.py                            Flask routes + local write endpoints
static/
  js/
    main.js                       App bootstrap, settings fetch, DEFAULT_SETTINGS
    prayers.js                    Prayer time display logic
    announcements.js              Announcement + Adhkar engine
    themes.js                     Theme switcher
    time.js / utils.js            Clock helpers
  data/
    tralee/
      settings.json               Jumuah, theme, labels, Adhkar config
      announcements.json          Active announcements
    dublin/                       Same structure for Dublin
data/
  tralee/prayer_times.csv
  dublin/prayer_times.csv
templates/
  index.html                      Live display
  manage/
    index.html                    Prayer times admin
    announcements.html            Announcements admin
    settings.html                 Settings admin
```

## Deployment

Hosted on Render. Data files (`*.json`, `*.csv`) are committed to this repository and served as Flask static files. The live display reloads itself at configurable times each day to pick up updated data.

See [USAGE.md](USAGE.md) for full operating instructions.
