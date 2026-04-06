# USAGE — Prayer Times App Operating Guide

This guide covers everything needed to manage the live prayer-times display for both mosques.

---

## 1. Admin Pages Overview

Each mosque has three management pages:

| Page | Tralee URL | Dublin URL | Purpose |
|------|-----------|-----------|---------|
| Prayer Times | `/manage/` | `/dublin/manage/` | View, add, edit, and delete prayer time rows |
| Announcements | `/manage/announcements/` | `/dublin/manage/announcements/` | Manage all announcement types |
| Settings | `/manage/settings/` | `/dublin/manage/settings/` | Theme, labels, Jumuah, Adhkar, refresh times |

---

## 2. GitHub Token Setup

All saves go through the GitHub API so changes are versioned and automatically deployed to the live site.

**Create a token:**
1. Go to GitHub → Settings → Developer settings → Fine-grained personal access tokens → Generate new token
2. Set **Repository access** to this repo only
3. Under **Permissions → Repository permissions → Contents**, select **Read and write**
4. Generate and copy the token

**Save the token in the browser:**
- Open any management page
- Paste the token into the "GitHub Token" field and click **Save**
- It's stored in `localStorage` — never sent to the server, never leaves your browser
- You only need to do this once per browser

**On localhost without a token:** see [Local Development Mode](#6-local-development-mode).

---

## 3. Managing Prayer Times

Open `/manage/` (Tralee) or `/dublin/manage/` (Dublin).

### Viewing times
Prayer times are displayed grouped by month. Each row shows Month, Date, and all prayer columns (Fajr Beginning, Fajr Jamaah, etc.).

### Adding a new month
1. Click **+ Add Month**
2. Paste data from the spreadsheet (tab-separated) into the text area
3. Click **Parse & Preview** — rows are shown for review
4. Click **Save to GitHub** — the new rows are appended to the CSV and committed

**Tralee format:** paste including the month header row and column headers  
**Dublin format:** paste tab-separated data; month is selected from a dropdown

### Editing a row
Click the **✏️** button on any row. Change the time values inline and click **Save**.

### Deleting a month
Expand the month, then click **Delete Month**. Confirm the prompt.

---

## 4. Managing Announcements

Open `/manage/announcements/` or `/dublin/manage/announcements/`.

The page lists all announcements with their type, ID, status badges, and action buttons (Edit / Show-Hide / Delete).

### 4.1 Text Announcements

Scroll text shown in the announcement bar.

**Fields:**
| Field | Description |
|-------|-------------|
| ID | Unique identifier, e.g. `ramadan_2027` |
| Message | The text to display |
| Schedule Windows | Date+time ranges when this announcement is active |
| Special | If ticked, text is highlighted in the warning colour |

**Schedule windows:** An announcement is active during *any* of its windows. Add up to 5 windows with **+ Add Window**. Each window has a start date/time and end date/time.

### 4.2 Image Announcements

A poster/image shown full-screen on the display.

**Fields:**
| Field | Description |
|-------|-------------|
| ID | Unique identifier |
| Image file | JPG/PNG — uploaded to the repo under `static/images/` |
| Schedule Windows | Date+time ranges when active |
| Frequency (min) | How many minutes between each showing in the rotation |
| Duration (sec) | How long the image stays on screen |
| Special | Bypasses normal rotation order |
| Avoid Jamaah times | Hides the image within a few minutes of each Jamaah |

### 4.3 Recurring Weekly Announcements

A poster that repeats every week on a specific day, controlled by seasonal timing rules.

**Fields:**
| Field | Description |
|-------|-------------|
| Day of week | Which day it triggers (Sunday–Saturday) |
| Frequency / Duration | Same as image announcements |
| Image | The poster image |
| Special / Avoid Jamaah | Same as image announcements |
| Date Range Windows | Optional — restrict to specific date ranges (in addition to seasonal timing) |
| Seasonal timing | Advanced JSON — defines `startReference`/`endReference` by prayer time for summer and winter |

**Date Range Windows on recurring_weekly:** If one or more windows are set, the announcement only shows when the current date falls inside a window *and* the seasonal timing matches. If no windows are set, seasonal timing alone controls it.

**Seasonal timing JSON structure:**
```json
{
  "summer": {
    "startReference": "fajrJamaah",
    "startOffset": 0,
    "endReference": "magribJamaah",
    "endOffset": 10
  },
  "winter": {
    "startReference": "fajrJamaah",
    "startOffset": 0,
    "endReference": "ishaJamaah",
    "endOffset": 10
  }
}
```
Valid references: `fajrBeginning`, `fajrJamaah`, `zohrBeginning`, `zohrJamaah`, `asarBeginning`, `asarJamaah`, `magribBeginning`, `magribJamaah`, `ishaBeginning`, `ishaJamaah`, `sunriseBeginning`.

### 4.4 Control Entries

Control entries are toggles that enable or disable a specific feature (e.g. `friday_tafseer_control` enables the Thursday/Friday Tafseer callout).

**Fields when editing:**
| Field | Description |
|-------|-------------|
| ID | Read-only |
| Description | Internal note about what this control toggles |
| Permanently hidden | If checked, the associated feature is always disabled, regardless of windows |
| Schedule Windows | Optional — auto-activate the feature only during these date ranges |

**Window behaviour:**
- `hide: true` + any windows → **always disabled** (hide wins)
- `hide: false` + no windows → **always active**
- `hide: false` + windows → **active only when current date is inside a window**

### 4.5 Common Operations

| Button | What it does |
|--------|-------------|
| Edit | Opens the edit modal for that announcement |
| Hide / Show | Toggles `hide: true/false` — hides immediately from the live display |
| Delete | Removes the entry permanently (asks for confirmation) |

---

## 5. Settings Page

Open `/manage/settings/` or `/dublin/manage/settings/`.

### 5.1 Theme Selection

Twenty colour swatches are displayed. Click any swatch to select it. The selected theme name is shown below the grid. Click **Save to GitHub** (or **Save Locally** on localhost) to apply it.

### 5.2 Display Labels

Column headings shown on the live prayer display:  
- **Column 1** — Tralee uses `BEGINNING`, Dublin uses `ADHAN`  
- **Column 2** — Tralee uses `JAMA'AH`, Dublin uses `IQAMAH`

### 5.3 Jumuah Time

Two separate time pickers for the Jumu'ah column:
- **Summer BST** — used when Irish Summer Time is active
- **Winter GMT** — used otherwise

### 5.4 Adhkar Display Timing

**Friday Dhuhr (Jumu'ah):**  
The Adhkar poster is triggered at a fixed clock time after Jumu'ah. Fields:
- Summer BST trigger time
- Winter GMT trigger time
- Window (min) — total duration of the Adhkar sequence
- Poster 1 (sec) — duration of Adhkar poster 1; Poster 2 fills the remaining time

**Per-Prayer Settings (Fajr / Dhuhr / Asr / Maghrib / Isha):**  
For all other prayers, the Adhkar poster is triggered relative to the Jamaah time. Each row:
- **Delay after Jamaah (min)** — how long after Jamaah the poster appears
- **Display window (min)** — total window duration
- **Poster 1 (sec)** — Poster 1 duration; Poster 2 fills the remainder

Poster 2 time is shown automatically and turns red if Poster 1 is too long.

### 5.5 Scheduled Refresh Times

A list of times (Irish time) at which the display page performs a hard reload. This forces it to pick up fresh prayer times and settings. Click **+ Add Time** to add more, click ✕ to remove.

---

## 6. Local Development Mode

When running Flask locally (`python app.py` or `flask run`), the management pages detect that you are on `localhost` or `127.0.0.1`.

If **no GitHub token is set**, a blue "Local Mode" banner appears and a **Save Locally** button is shown. Clicking it:
- POSTs the JSON directly to the Flask server (endpoint: `POST /api/settings` or `POST /api/announcements`)
- Flask writes the file directly to disk (inside the repo folder)
- The change is visible immediately on the next page load — no git commit needed

**Image uploads still require a GitHub token** even in Local Mode (images are stored in the GitHub repo, not locally).

To use Local Mode:
1. Start Flask: `python app.py`
2. Open `http://localhost:5000/manage/settings/`
3. Make changes, click **Save Locally**
4. Open `http://localhost:5000` — the live display reflects the changes immediately

---

## 7. Deploying Changes to Production

The app is hosted on Render. All data files (`*.json`, `*.csv`) live in this GitHub repository.

**Normal workflow (via GitHub):**
1. Make changes on the management page using the **Save to GitHub** button
2. Changes are committed to the `main` branch automatically
3. The live display page reloads itself at the next scheduled refresh time and picks up the new data

**Forcing an immediate refresh:**
- On the live display page, press **F5** or add a scheduled refresh time of the current time + 1 min (then remove it)
- Alternatively, the display refreshes automatically at midnight, 06:30, 12:30, and several other times configured in Settings → Scheduled Refresh Times

**Local changes to production:**
1. Edit JSON files locally using "Save Locally"
2. Commit and push the changed files: `git add static/data/ ; git commit -m "Update settings" ; git push`
3. Render auto-deploys from the `main` branch
