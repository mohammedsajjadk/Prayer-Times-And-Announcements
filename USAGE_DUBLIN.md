# Dublin Mosque — Management Guide

This guide covers every day-to-day task for managing the prayer-times display screen.

**Management URL:** `/dublin/manage/`

---

## Contents

1. [Update Prayer Times for a New Month](#1-update-prayer-times-for-a-new-month)
2. [Fix a Wrong Prayer Time](#2-fix-a-wrong-prayer-time)
3. [Add a Text Announcement](#3-add-a-text-announcement)
4. [Add an Image Poster](#4-add-an-image-poster)
5. [Cancel a Recurring Class Temporarily (Suppress Periods)](#5-cancel-a-recurring-class-temporarily)
6. [Hide an Announcement Immediately](#6-hide-an-announcement-immediately)
7. [Change the Display Theme](#7-change-the-display-theme)
8. [Adjust Adhkar Poster Timings](#8-adjust-adhkar-poster-timings)
9. [Understanding Status Badges](#9-understanding-status-badges)
10. [GitHub Token Setup](#10-github-token-setup)

---

## 1. Update Prayer Times for a New Month

Prayer times come as a tab-separated table (from the mosque's own timetable source). Each upload covers one calendar month.

### Step 1 — Understand the expected format

The parser expects a **tab-separated** table with these columns:

```
Date    Day     Fajr    Sunrise Dhuhr   Asr     Maghrib Isha
1       Mon     03:45   05:42   13:12   17:04   21:20   22:45
2       Tue     03:46   05:43   13:12   17:04   21:19   22:44
...
```

**Important details:**
- **No month name row required** — the month is selected from a **dropdown** on the management page before parsing
- **Column headings** should be present as the first row
- **ADHAN times** (beginning times) are in these columns — the parser treats them as the Adhan column
- **IQAMAH times** are auto-calculated as **Adhan + 10 minutes** for every prayer
- Times use `HH:MM` 24-hour format — unlike Tralee, there are no decimal afternoon times

### Step 2 — Get the data

Copy the relevant month's data from the Excel spreadsheet or timetable source:
1. Select from the column headers row down to the last day of the month
2. Copy (**Ctrl+C**)

### Step 3 — Paste and save

1. Go to `/dublin/manage/prayer-times/`
2. Click **+ Add Month** to open the upload panel
3. Select the **month** from the dropdown (e.g. “June”)
4. Paste the copied data into the text area (**Ctrl+V**)
5. Click **Parse & Save to GitHub** — this parses the data and commits it to GitHub in one step
6. A green toast confirms success; the live display picks up the new times within a few minutes

---

## 2. Update Prayer Time for Specific Day or Fix a Wrong Prayer Time

1. Go to `/dublin/manage/prayer-times/`
2. Find the row for the day you want to edit
3. Click the **✎ (pencil) button** on that row — this opens the **Edit Prayer Times** modal
4. Update the time(s) as needed (format: `HH:MM`, e.g. `19:45`)
5. Click **Save & Commit** in the modal footer — saves and commits to GitHub in one step

---

## 3. Add a Text Announcement

Use text announcements for notices like: *"Sisters' Quran circle: Every Saturday after Fajr"* or *"Eid prayer: Saturday 7:00am — arrive early."*

1. Go to `/dublin/manage/announcements/`
2. Click **+ Text** to expand the Add Text panel
3. Fill in the form:

| Field | Notes |
|-------|-------|
| **ID** | A unique identifier with no spaces, e.g. `eid_dinner_2027` |
| **Message** | The text shown on the display screen |
| **Schedule Windows** | *Required.* Set Start date/time → End date/time for when the announcement is active. Click **+ Add Window** to add more (max 5). |
| **Special announcement** | Check for high-priority notices |

4. Click **Save to GitHub**

---

## 4. Add an Image Poster

Use image posters for event flyers, holiday greetings, or lecture posters.

### Step 1 — Generate the image with ChatGPT

Use this prompt template to ask ChatGPT to generate the announcement image:

---

**Generic template:**

```
- Create a professional Islamic event poster in image format

- Event:
  [EVENT NAME]

- Title:
  [TITLE / THEME]

- Details:
  Date: [DAY, DATE]
  Womens Time: [TIME]
  Mens Time: [TIME]
  Venue: [MASJID / LOCATION NAME]
  [ADDITIONAL LOCATION LINE IF NEEDED]

- Style:
  - Mature, elegant, and modern (NOT childish)
  - No bright playful colors
  - No cartoon style
  - No human or living creature figures
  - Clean and minimal design

- Theme:
  - Subtle theme of [THEME IDEA – e.g. growth, knowledge, unity, family, spirituality]
  - Use refined elements like [e.g. books, calligraphy, abstract learning symbols]
  - Avoid toys or childish graphics
  - Optional: soft Islamic geometric patterns or mosque silhouette in background

- Colors:
  - Sophisticated palette (e.g. navy blue, beige, gold, charcoal, off-white)
  - Soft gradients or lightly textured background
  - High contrast for readability

- Typography:
  - Title "[TITLE]" should be the BIGGEST
  - Event name "[EVENT NAME]" should be bold and prominent at top
  - Date should be very large (second biggest)
  - Time details also large and clear
  - Venue slightly smaller but readable
  - Use elegant, modern fonts (no playful fonts)

- Layout:
  - Structured sections with good spacing
  - Centered composition
  - Clean dividers or subtle lines between sections

- Output:
  - High-resolution, print-ready poster
  - All text sharp and clearly readable
```

---

### Step 2 — Download the image

Save the generated image to your computer (right-click → Save image).

### Step 3 — Upload in the management page

1. Go to `/dublin/manage/announcements/`
2. Click **+ Image** to expand the Add Image panel
3. Fill in the form:

| Field | Notes |
|-------|-------|
| **ID** | A unique identifier, e.g. `ramadan_poster_2027` |
| **Image file** | Choose the saved JPG or PNG — it will be uploaded to GitHub |
| **Schedule Windows** | *Required.* Set Start date/time → End date/time for when the poster shows. Click **+ Add Window** to add more (max 5). |
| **Frequency (minutes)** | How often the poster appears in the rotation |
| **Duration (seconds)** | How long it stays on screen each time |
| **Special** | Check for high-priority posters |
| **Avoid Jamaah times** | Check to skip showing near prayer times |

4. Click **Upload & Save to GitHub** — the image is uploaded to GitHub first, then the announcement is saved. A green toast confirms success.

---

## 5. Cancel a Recurring Class Temporarily

If a regular class or event is cancelled for specific dates without removing the whole announcement:

> Suppress periods are only available on **recurring** and **control** type announcements.

1. Go to `/dublin/manage/announcements/`
2. Find the recurring announcement in the list
3. Click **Edit** on that announcement
4. In the edit modal, scroll to **Suppress periods**
5. Click **+ Add Suppress Period**
6. Set the Start date/time and End date/time for the cancelled period
7. Click **Save to GitHub** in the modal footer

---

## 6. Hide an Announcement Immediately

To immediately remove an announcement from the display without deleting it:

1. Go to `/dublin/manage/announcements/`
2. Find the announcement in the list
3. Click the **Hide** button — the change saves to GitHub immediately

The announcement stays in your list with a **Hidden** badge. To restore it: click the **Show** button (same button, label changes to “Show” when hidden) — also saves immediately.

---

## 7. Change the Display Theme

1. Go to `/dublin/manage/settings/`
2. Scroll to **Theme Selection**
3. Click a theme **swatch** from the visual grid to select it
4. Click **Save to GitHub**

---

## 8. Adjust Adhkar Poster Timings

Adhkar slides automatically appear between prayers. To tune when they show:

1. Go to `/dublin/manage/settings/`
2. Scroll to **Adhkar Display Timing**
3. In the **Per-Prayer Settings** table, edit any prayer row:
   - **Delay after Jamaah (min)** — pause before Adhkar starts
   - **Display window (min)** — total minutes the Adhkar cycle is active
   - **Poster 1 (sec)** — duration of the first Adhkar poster; Poster 2 fills remaining window time automatically
4. To adjust Friday Jumu'ah Adhkar, edit the **Friday Dhuhr** table above the per-prayer table:
   - **Summer BST trigger** — clock time Adhkar starts on Fridays in summer
   - **Winter GMT trigger** — clock time Adhkar starts on Fridays in winter
   - **Window (min)** and **Poster 1 (sec)**
5. Click **Save to GitHub**

---

## 9. Understanding Status Badges

Each announcement in the list shows a coloured badge:

| Badge | Colour | Meaning |
|-------|--------|---------|
| **Active** | Green | Showing on screen right now |
| **Active soon** | Grey | In date range but not within any active schedule window |
| **Inactive** | Light grey | Outside its start/end date range |
| **Suppressed now** | Orange | Inside a suppress period — temporarily hidden |
| **Hidden** | Red | Manually hidden via the Hide button |

---

## 10. GitHub Token Setup

All saves go through the GitHub API so changes are versioned and automatically deployed to the live site.

**Create a token (one-time):**
1. Go to GitHub → Settings → Developer settings → Fine-grained personal access tokens → **Generate new token**
2. Set **Repository access** to this repo only
3. Under **Permissions → Repository permissions → Contents**, select **Read and write**
4. Click Generate, then **copy the token immediately** (you can only see it once)

**Save the token in your browser:**
1. Open `/dublin/manage/`
2. Paste the token into the **GitHub Token** field and click **Save**
3. The token is stored only in your browser's `localStorage` — it is never sent to the server
4. You only need to do this once per browser (and again in incognito/private mode)
