import csv
import json
import os
from datetime import datetime, timezone, timedelta

from flask import Flask, render_template, jsonify, Response, request
from hijri_converter import convert

app = Flask(__name__)

# ─── Mosque configurations ────────────────────────────────────────────────────
MOSQUE_CONFIGS = {
    'tralee': {
        'slug': 'tralee',
        'displayName': 'Tralee Islamic Centre',
        'csvPath': 'data/tralee/prayer_times.csv',
        'announcementsPath': 'static/data/tralee/announcements.json',
        'settingsPath': 'static/data/tralee/settings.json',
        'sehriOffset': -10,
        'parserFormat': 'tralee',
        'manageBase': '/manage/',
        'announcementsManage': '/manage/announcements/',
        'settingsManage': '/manage/settings/',
        'prayerTimesManage': '/manage/prayer-times/',
        'apiBase': '/',
        'liveSite': '/',
    },
    'dublin': {
        'slug': 'dublin',
        'displayName': 'Dublin Mosque',
        'csvPath': 'data/dublin/prayer_times.csv',
        'announcementsPath': 'static/data/dublin/announcements.json',
        'settingsPath': 'static/data/dublin/settings.json',
        'sehriOffset': 0,
        'parserFormat': 'dublin',
        'manageBase': '/dublin/manage/',
        'announcementsManage': '/dublin/manage/announcements/',
        'settingsManage': '/dublin/manage/settings/',
        'prayerTimesManage': '/dublin/manage/prayer-times/',
        'apiBase': '/dublin/',
        'liveSite': '/dublin',
    },
}


def load_prayer_times(csv_path='data/tralee/prayer_times.csv'):
    prayer_times = []
    with open(csv_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header
        for row in csvreader:
            prayer_times.append(row)
    return prayer_times


def get_islamic_date(date=None):
    if date is None:
        today = datetime.today().date()  # Get today's date
    else:
        today = date
        
    hijri_date = convert.Gregorian(today.year, today.month, today.day).to_hijri()

    # Format Islamic date like "14 J-Ul-Awwal 1436"
    islamic_months = [
        "Muharram", "Safar", "Rabi-Ul-Awwal", "Rabi-Ul-Thani",
        "J-Ul-Awwal", "J-Ul-Thani", "Rajab", "Sha'ban",
        "Ramadan", "Shawwal", "Dhul-Qadah", "Dhul-Hijjah"
    ]

    formatted_hijri_date = f"{hijri_date.day} {islamic_months[hijri_date.month - 1]} {hijri_date.year}"
    return formatted_hijri_date


def calculate_important_times(prayer_times, sehri_offset=-10):
    # [0]=MONTH, [1]=DATE, [2]=FAJR BEGINNING, [3]=SUNRISE, [4]=ZOHR BEGINNING ...
    try:
        sehri_time = datetime.strptime(prayer_times[2], '%H:%M')
        zohr_time  = datetime.strptime(prayer_times[4], '%H:%M')
        sehri_ends = (sehri_time + timedelta(minutes=sehri_offset)).strftime('%H:%M')
        noon_time  = (zohr_time - timedelta(minutes=10)).strftime('%H:%M')
    except (ValueError, TypeError):
        sehri_ends = '--:--'
        noon_time  = '--:--'
    return {
        'sehri_ends': sehri_ends,
        'sunrise': prayer_times[3],
        'noon': noon_time
    }


# To determine if a given date is in Irish Summer Time
def is_ireland_dst(dt):
    year = dt.year
    march_last_day = 31 - (datetime(year, 3, 31).weekday() + 1) % 7
    dst_start = datetime(year, 3, march_last_day, 1, 0, tzinfo=timezone.utc)
    oct_last_day = 31 - (datetime(year, 10, 31).weekday() + 1) % 7
    dst_end = datetime(year, 10, oct_last_day, 1, 0, tzinfo=timezone.utc)
    return dst_start <= dt < dst_end


# ─── Shared view helpers ──────────────────────────────────────────────────────
def _index_view(mosque_slug):
    mosque = MOSQUE_CONFIGS[mosque_slug]
    prayer_times = load_prayer_times(mosque['csvPath'])
    now = datetime.now(timezone.utc)
    is_summer_time = is_ireland_dst(now)
    irish_time = now + timedelta(hours=(1 if is_summer_time else 0))
    current_month = irish_time.month
    current_day = irish_time.day
    today_prayer_times = next(
        (row for row in prayer_times if int(row[0]) == current_month and int(row[1]) == current_day), None)
    tomorrow = irish_time + timedelta(days=1)
    tomorrow_prayer_times = next(
        (row for row in prayer_times if int(row[0]) == tomorrow.month and int(row[1]) == tomorrow.day), None)

    # Fallback placeholder row when no data exists yet (e.g. mosque just set up)
    _empty_row = ['0', '0', '--:--', '--:--', '--:--', '--:--', '--:--', '--:--',
                  '--:--', '--:--', '--:--', '--:--', '--:--']
    if today_prayer_times is None:
        today_prayer_times = _empty_row
    if tomorrow_prayer_times is None:
        tomorrow_prayer_times = _empty_row

    important_times = calculate_important_times(today_prayer_times, mosque['sehriOffset'])
    tomorrow_important_times = calculate_important_times(tomorrow_prayer_times, mosque['sehriOffset'])
    return render_template('index.html',
                           current_time=irish_time.strftime('%H:%M:%S'),
                           current_date=irish_time.strftime('%a %d %b %Y'),
                           islamic_date=get_islamic_date(irish_time.date()),
                           today_prayer_times=today_prayer_times,
                           tomorrow_prayer_times=tomorrow_prayer_times,
                           important_times=important_times,
                           tomorrow_important_times=tomorrow_important_times,
                           mosque_slug=mosque_slug)


def _api_csv_view(mosque_slug):
    mosque = MOSQUE_CONFIGS[mosque_slug]
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), mosque['csvPath'])
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content, mimetype='text/plain')
    except FileNotFoundError:
        return Response('', mimetype='text/plain', status=404)


def _api_json_view(mosque_slug, file_key, empty_fallback='{}'):
    mosque = MOSQUE_CONFIGS[mosque_slug]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), mosque[file_key])
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content, mimetype='application/json')
    except FileNotFoundError:
        return Response(empty_fallback, mimetype='application/json', status=404)


def _api_json_write_view(mosque_slug, file_key):
    """Write a JSON file to disk. Only permitted from localhost."""
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return jsonify({'error': 'Local writes are only permitted from localhost.'}), 403
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Invalid or missing JSON body.'}), 400
    mosque = MOSQUE_CONFIGS[mosque_slug]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), mosque[file_key])
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return jsonify({'ok': True})


_DEBUG_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'debug.log')
_DEBUG_MAX_LINES = 5000  # Rotate after this many lines


def _debug_log_allowed():
    """Only localhost may access debug log endpoints."""
    return request.remote_addr in ('127.0.0.1', '::1')


@app.route('/api/debug-log', methods=['POST'])
def debug_log_write():
    if not _debug_log_allowed():
        return jsonify({'error': 'Forbidden'}), 403
    payload = request.get_json(silent=True) or {}
    lines = payload.get('lines', [])
    if not lines:
        return jsonify({'ok': True})
    os.makedirs(os.path.dirname(_DEBUG_LOG_PATH), exist_ok=True)
    with open(_DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    # Rotate: keep only the last _DEBUG_MAX_LINES lines
    try:
        with open(_DEBUG_LOG_PATH, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        if len(all_lines) > _DEBUG_MAX_LINES:
            with open(_DEBUG_LOG_PATH, 'w', encoding='utf-8') as f:
                f.writelines(all_lines[-_DEBUG_MAX_LINES:])
    except OSError:
        pass
    return jsonify({'ok': True})


@app.route('/api/debug-log', methods=['GET'])
def debug_log_read():
    if not _debug_log_allowed():
        return Response('Forbidden', status=403, mimetype='text/plain')
    try:
        with open(_DEBUG_LOG_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ''
    return Response(content, mimetype='text/plain')


@app.route('/api/debug-log', methods=['DELETE'])
def debug_log_clear():
    if not _debug_log_allowed():
        return jsonify({'error': 'Forbidden'}), 403
    try:
        open(_DEBUG_LOG_PATH, 'w').close()
    except OSError:
        pass
    return jsonify({'ok': True})


# Dublin shares the same single debug log file
@app.route('/dublin/api/debug-log', methods=['POST'])
def dublin_debug_log_write():
    return debug_log_write()


@app.route('/dublin/api/debug-log', methods=['GET'])
def dublin_debug_log_read():
    return debug_log_read()


@app.route('/dublin/api/debug-log', methods=['DELETE'])
def dublin_debug_log_clear():
    return debug_log_clear()


# ─── Tralee routes ────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return _index_view('tralee')


@app.route('/manage/')
def manage_index():
    return render_template('manage/index.html', mosque=MOSQUE_CONFIGS['tralee'])


@app.route('/manage/logs')
def manage_logs():
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return Response('Forbidden — debug logs are only accessible from localhost.', status=403, mimetype='text/plain')
    return render_template('manage/logs.html', mosque=MOSQUE_CONFIGS['tralee'])


@app.route('/manage/announcements/')
def manage_announcements():
    return render_template('manage/announcements.html', mosque=MOSQUE_CONFIGS['tralee'])


@app.route('/manage/prayer-times/')
def manage_prayer_times():
    return render_template('manage/prayer_times.html', mosque=MOSQUE_CONFIGS['tralee'])


@app.route('/manage/settings/')
def manage_settings():
    return render_template('manage/settings.html', mosque=MOSQUE_CONFIGS['tralee'])


@app.route('/api/csv')
def get_csv():
    return _api_csv_view('tralee')


@app.route('/api/announcements')
def get_announcements():
    return _api_json_view('tralee', 'announcementsPath', '[]')


@app.route('/api/announcements', methods=['POST'])
def save_announcements_local():
    return _api_json_write_view('tralee', 'announcementsPath')


@app.route('/api/settings')
def get_settings():
    return _api_json_view('tralee', 'settingsPath', '{}')


@app.route('/api/settings', methods=['POST'])
def save_settings_local():
    return _api_json_write_view('tralee', 'settingsPath')


# ─── Dublin routes ────────────────────────────────────────────────────────────
@app.route('/dublin')
def dublin_index():
    return _index_view('dublin')


@app.route('/dublin/manage/')
def dublin_manage_index():
    return render_template('manage/index.html', mosque=MOSQUE_CONFIGS['dublin'])


@app.route('/dublin/manage/logs')
def dublin_manage_logs():
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return Response('Forbidden — debug logs are only accessible from localhost.', status=403, mimetype='text/plain')
    return render_template('manage/logs.html', mosque=MOSQUE_CONFIGS['dublin'])


@app.route('/dublin/manage/announcements/')
def dublin_manage_announcements():
    return render_template('manage/announcements.html', mosque=MOSQUE_CONFIGS['dublin'])


@app.route('/dublin/manage/prayer-times/')
def dublin_manage_prayer_times():
    return render_template('manage/prayer_times.html', mosque=MOSQUE_CONFIGS['dublin'])


@app.route('/dublin/manage/settings/')
def dublin_manage_settings():
    return render_template('manage/settings.html', mosque=MOSQUE_CONFIGS['dublin'])


@app.route('/dublin/api/csv')
def dublin_get_csv():
    return _api_csv_view('dublin')


@app.route('/dublin/api/announcements')
def dublin_get_announcements():
    return _api_json_view('dublin', 'announcementsPath', '[]')


@app.route('/dublin/api/announcements', methods=['POST'])
def dublin_save_announcements_local():
    return _api_json_write_view('dublin', 'announcementsPath')


@app.route('/dublin/api/settings')
def dublin_get_settings():
    return _api_json_view('dublin', 'settingsPath', '{}')


@app.route('/dublin/api/settings', methods=['POST'])
def dublin_save_settings_local():
    return _api_json_write_view('dublin', 'settingsPath')


if __name__ == '__main__':
    app.run(debug=True)
