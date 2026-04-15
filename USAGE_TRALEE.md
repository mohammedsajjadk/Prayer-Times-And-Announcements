# Tralee Islamic Centre — Management Guide

This guide covers every day-to-day task for managing the prayer-times display screen.

**Management URL:** `/manage/`

---

## Contents

1. [Update Prayer Times for a New Month](#1-update-prayer-times-for-a-new-month)
2. [Fix a Wrong Prayer Time](#2-fix-a-wrong-prayer-time)
3. [Add a Text Announcement](#3-add-a-text-announcement)
4. [Add an Image Poster](#4-add-an-image-poster)
5. [Cancel a Recurring Class Temporarily (Suppress Periods)](#5-cancel-a-recurring-class-temporarily)
6. [Hide an Announcement Immediately](#6-hide-an-announcement-immediately)
7. [Change the Jumu'ah Time](#7-change-the-jumuah-time)
8. [Change the Display Theme](#8-change-the-display-theme)
9. [Adjust Adhkar Poster Timings](#9-adjust-adhkar-poster-timings)
10. [Understanding Status Badges](#10-understanding-status-badges)
11. [GitHub Token Setup](#11-github-token-setup)

---

## 1. Update Prayer Times for a New Month

Prayer times come from the Imam as an Excel spreadsheet. Each month appears on its own sheet (e.g. "June", "July").

### Step 1 — Open the spreadsheet and locate the month

Open the Excel file. Click the tab for the month you want to upload (e.g. **JUNE**).

### Step 2 — Understand the expected format

The parser expects **exactly this layout** (example shown for June):

```
JUNE		ISLAMIC 	BEGINNING TIMES...
DATE	DAY	HIJRI	FAJR	SUNRISE	ZOHR	ASAR	MAGRIB	ISHA		FAJR	ZOHR	ASAR	MAGRIB	ISHA
1	Mon	15 D.Hijjah	03:04	05:23	13:37	19:12	21:53	23:13		4.45	2.00	8.15	9.58	11.25
2	Tue	16	03:04	05:22	13:37	19:12	21:54	23:14		"	"	"	9.59	"
3	Wed	17	03:04	05:22	13:37	19:13	21:55	23:14		"	"	"	10.00	"
...
30	Sun	15 Muharram	03:46	05:54	13:34	19:02	22:18	23:43		"	"	"	10.00	"
```

**Important details:**
- **Row 1:** The month name (e.g. `JUNE`) must be present in the first cell — the parser uses it to identify the month
- **Row 2:** Column headers — must be present as shown above
- **`"` symbol:** Means "same Jamaah time as the previous row" — the parser fills these in automatically
- **Decimal times (e.g. `4.45`):** Afternoon Jamaah times are written in H.MM decimal format:
  - `4.45` → **16:45**
  - `2.00` → **14:00**
  - `8.15` → **20:15**
  - `9.58` → **21:58**
  - `11.25` → **23:25**
- **Early morning times** (Fajr Jamaah, e.g. `4.45` at 04:45 before sunrise) are kept as-is; afternoon times are converted by adding 12 hours

### Step 3 — Select and copy the data

In Excel:
1. Click on the cell containing **JUNE** (the month name, top-left)
2. Select down to the **last day of the month**, across to the **last column** (ISHA Jamaah)
3. Copy (**Ctrl+C**)

> Include the month name row and the headers row — these are required for the parser.

### Step 4 — Paste and save

1. Go to `/manage/prayer-times/`
2. Click **+ Add Month** to open the upload panel
3. Paste the copied data into the text area (**Ctrl+V**)
4. Click **Parse & Save to GitHub** — this parses the data and commits it to GitHub in one step
5. A green toast confirms success; the live display picks up the new times within a few minutes

---

## 2. Update Prayer Time for Specific Day or Fix a Wrong Prayer Time

1. Go to `/manage/prayer-times/`
2. Find the row for the day you want to edit
3. Click the **✎ (pencil) button** on that row — this opens the **Edit Prayer Times** modal
4. Update the time(s) as needed (format: `HH:MM`, e.g. `19:45`)
5. Click **Save & Commit** in the modal footer — saves and commits to GitHub in one step

---

## 3. Add a Text Announcement

Use text announcements for notices like: *"Eid ul-Adha: Saturday Night Prayers — Masjid opens at 8pm"* or *"Weekly lecture: Every Tuesday after Isha."*

1. Go to `/manage/announcements/`
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
Create a **high-resolution, print-ready event poster** with a **mature, elegant, modern design** and a **tight, space-efficient layout**.

---

### ⚠️ **STRICT LAYOUT RULES**

* Fully utilize the canvas (no large empty space at top or bottom)
* Minimize margins while keeping clean edges
* All content must scale to fill the poster naturally
* Avoid excessive spacing between sections
* Ensure strong vertical balance (top → middle → bottom flow)
* Text should occupy most of the design (approximately 70–85% of space)

---

### 🧾 **CONTENT STRUCTURE (REPLACE AS NEEDED)**

**TITLE (Top – Most Important):**
[INSERT MAIN EVENT TITLE HERE]
→ Largest text on poster
→ Bold and visually dominant

---

**SUBTITLE / DESCRIPTION:**
[INSERT EVENT DESCRIPTION HERE]
→ IMPORTANT: Make this **large and clearly readable (not small or faint)**
→ Second most prominent text block

---

**DATE / TIME DETAILS:**
[INSERT DATE & TIME INFO HERE]
→ Large and bold
→ Clear hierarchy, easy to scan
→ Can be split into multiple lines if needed

---

**VENUE (Bottom Center – Least Prominent):**
[INSERT VENUE HERE]
→ Smallest text section
→ Center aligned at bottom

---

### 🖼️ **IMAGE / BACKGROUND REQUIREMENTS**

* Include subtle, relevant thematic imagery (optional but recommended)
* Images must NOT dominate text
* If using images:

  * Max 20–30% visual weight each
  * Soft blend into background
  * Must remain clear (not overly dark or blurred)
* Can include abstract or symbolic visuals depending on theme
* Ensure text remains the primary focus

---

### 🎨 **STYLE DIRECTION**

* Elegant, minimal, and professional
* No childish or playful design elements
* No human or living creature illustrations
* Use structured layout with clear hierarchy
* Subtle decorative elements only (e.g. geometric patterns, soft gradients)

---

### 🎨 **COLOR PALETTE**

* Use sophisticated tones such as:
  navy blue, charcoal, deep green, beige, off-white, gold accents
* Ensure high contrast for readability
* Avoid overly bright or neon colors

---

### 🔤 **TYPOGRAPHY RULES**

* Strong hierarchy:

  1. Title – largest
  2. Date/Time – second largest
  3. Subtitle – medium-large (must be readable, not small)
  4. Venue – smallest
* Use clean, modern, professional fonts
* Avoid decorative or cartoon-style fonts

---

### 📐 **COMPOSITION RULES**

* Centered or balanced structured layout
* Content should fill the entire vertical space evenly
* No large blank gaps anywhere
* Use subtle dividers or spacing for clarity
* Ensure visual weight is evenly distributed

---

### 🖨️ **OUTPUT REQUIREMENTS**

* Portrait orientation
* High resolution (300 DPI or higher)
* Print-ready quality
* Sharp, readable text
* Clean margins and professional finish

---

## 💡 Optional add-on line (if AI leaves empty space):

> “Ensure all available space is efficiently used by scaling text and balancing layout; avoid empty areas.”```

---

**Example — Ramadan Farewell:**

```
Create a professional Islamic event poster in image format.

Event:
Monthly Bayaan Programme

Title:
Together We Thrive: Parents and Children

Details:
Date: Sunday 26 April 2026
Womens Time: After Zohr 2:45 PM
Mens Time: After Asar 7:45 PM
Venue: Tralee Masjid
Kerry Islamic Cultural Centre

Style:
- Mature, elegant, and modern (NOT childish)
- No bright playful colors, no cartoon style
- No human or living creature figures
- Clean and minimal design

Theme:
- Subtle “growth, learning, and family development” theme
- Use refined elements like books, subtle school items, or abstract learning symbols
- Avoid toys or childish graphics
- Optional: soft Islamic geometric patterns or mosque silhouette in background

Colors:
- Sophisticated palette (navy blue, beige, gold, charcoal, off-white)
- Soft gradients or textured background
- High contrast for readability

Typography:
- Title "Together We Thrive: Parents and Children" should be the BIGGEST
- Event name "Monthly Bayaan Programme" should be bold and prominent at top
- Date should be very large (second biggest)
- Time details also large and clear
- Venue slightly smaller but readable
- Use elegant, modern fonts (no playful fonts)

Layout:
- Structured sections with spacing
- Centered composition
- Clean dividers or subtle lines between sections

Output:
- High-resolution, print-ready poster
- All text sharp and clearly readable
```

---

### Step 2 — Download the image

Save the generated image to your computer (right-click → Save image).

### Step 3 — Upload in the management page

1. Go to `/manage/announcements/`
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

If a regular class or event (e.g. *Quran class every Tuesday*) is cancelled for specific dates without removing the whole announcement:

> Suppress periods are only available on **recurring** and **control** type announcements.

1. Go to `/manage/announcements/`
2. Find the recurring announcement in the list
3. Click **Edit** on that announcement
4. In the edit modal, scroll to **Suppress periods**
5. Click **+ Add Suppress Period**
6. Set the Start date/time and End date/time for the cancelled period
7. Click **Save to GitHub** in the modal footer

The announcement will not appear during that suppressed window, then resume automatically when the period ends. The status badge will show **Suppressed now** during those dates.

---

## 6. Hide an Announcement Immediately

To immediately remove an announcement from the display without deleting it (so you can restore it later):

1. Go to `/manage/announcements/`
2. Find the announcement in the list
3. Click the **Hide** button — the change saves to GitHub immediately

The announcement stays in your list with a **Hidden** badge. To restore it: click the **Show** button (same button, label changes to “Show” when hidden) — also saves immediately.

---

## 7. Change the Jumu'ah Time

1. Go to `/manage/settings/`
2. Scroll to **Jumu'ah Time**
3. Update **Summer time (BST)** (late March → late October) and/or **Winter time (GMT)** (late October → late March)
4. Click **Save to GitHub**

The new times appear on the live display immediately after the next data refresh.

---

## 8. Change the Display Theme

1. Go to `/manage/settings/`
2. Scroll to **Theme Selection**
3. Click a theme **swatch** from the visual grid to select it
4. Click **Save to GitHub**

---

## 9. Adjust Adhkar Poster Timings

Adhkar (remembrance) slides automatically appear between prayers. To tune when they show:

1. Go to `/manage/settings/`
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

## 10. Understanding Status Badges

Each announcement in the list shows a coloured badge:

| Badge | Colour | Meaning |
|-------|--------|---------|
| **Active** | Green | Showing on screen right now |
| **Active soon** | Grey | In date range but not within any active schedule window |
| **Inactive** | Light grey | Outside its start/end date range |
| **Suppressed now** | Orange | Inside a suppress period — temporarily hidden |
| **Hidden** | Red | Manually hidden via the Hide button |

---

## 11. GitHub Token Setup

All saves go through the GitHub API so changes are versioned and automatically deployed to the live site.

**Create a token (one-time):**
1. Go to GitHub → Settings → Developer settings → Fine-grained personal access tokens → **Generate new token**
2. Set **Repository access** to this repo only
3. Under **Permissions → Repository permissions → Contents**, select **Read and write**
4. Click Generate, then **copy the token immediately** (you can only see it once)

**Save the token in your browser:**
1. Open `/manage/`
2. Paste the token into the **GitHub Token** field and click **Save**
3. The token is stored only in your browser's `localStorage` — it is never sent to the server
4. You only need to do this once per browser (and again in incognito/private mode)
