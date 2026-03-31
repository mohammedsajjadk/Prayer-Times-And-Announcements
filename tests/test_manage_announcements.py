"""Tests for manage_announcements.py"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manage_announcements as ma


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_ANNOUNCEMENTS = [
    {
        "id": "test_event",
        "startDate": "2027-03-15T09:00:00+01:00",
        "endDate": "2027-03-15T18:00:00+01:00",
        "message": "Test announcement",
        "isSpecial": False,
        "hide": False
    },
    {
        "id": "hidden_event",
        "startDate": "2027-04-01T09:00:00+01:00",
        "endDate": "2027-04-01T18:00:00+01:00",
        "message": "Hidden announcement",
        "isSpecial": False,
        "hide": True
    },
    {
        "id": "weekly_program",
        "type": "recurring_weekly",
        "dayOfWeek": 5,
        "images": ["/static/images/Program.jpg"],
        "hide": False
    }
]


# ---------------------------------------------------------------------------
# load_announcements
# ---------------------------------------------------------------------------

class TestLoadAnnouncements:
    def test_loads_valid_file(self, tmp_path):
        ann_file = tmp_path / "announcements.json"
        ann_file.write_text(json.dumps(SAMPLE_ANNOUNCEMENTS))

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)):
            result = ma.load_announcements()

        assert len(result) == 3
        assert result[0]['id'] == 'test_event'

    def test_returns_none_when_file_missing(self, capsys):
        with patch.object(ma, 'ANNOUNCEMENTS_FILE', 'nonexistent.json'):
            result = ma.load_announcements()

        assert result is None
        assert "not found" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# save_announcements
# ---------------------------------------------------------------------------

class TestSaveAnnouncements:
    def test_writes_json_to_file(self, tmp_path):
        ann_file = tmp_path / "announcements.json"

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)):
            ma.save_announcements(SAMPLE_ANNOUNCEMENTS)

        saved = json.loads(ann_file.read_text())
        assert len(saved) == 3

    def test_prints_success_message(self, tmp_path, capsys):
        ann_file = tmp_path / "announcements.json"

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)):
            ma.save_announcements(SAMPLE_ANNOUNCEMENTS)

        assert "Successfully saved" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# list_announcements
# ---------------------------------------------------------------------------

class TestListAnnouncements:
    def test_shows_all_announcements(self, capsys):
        ma.list_announcements(SAMPLE_ANNOUNCEMENTS)
        out = capsys.readouterr().out
        assert "test_event" in out
        assert "hidden_event" in out
        assert "weekly_program" in out

    def test_shows_hidden_status(self, capsys):
        ma.list_announcements(SAMPLE_ANNOUNCEMENTS)
        out = capsys.readouterr().out
        assert "HIDDEN" in out
        assert "ACTIVE" in out

    def test_shows_day_for_recurring_weekly(self, capsys):
        ma.list_announcements(SAMPLE_ANNOUNCEMENTS)
        out = capsys.readouterr().out
        assert "Friday" in out


# ---------------------------------------------------------------------------
# add_text_announcement
# ---------------------------------------------------------------------------

class TestAddTextAnnouncement:
    def test_adds_new_announcement(self, tmp_path):
        ann_file = tmp_path / "announcements.json"
        announcements = []

        inputs = iter([
            'new_event',       # id
            'Test message',    # message
            '2027-05-01',      # start date
            '09:00',           # start time
            '2027-05-01',      # end date
            '18:00',           # end time
            'n',               # is special
        ])

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', side_effect=inputs):
            ma.add_text_announcement(announcements)

        assert len(announcements) == 1
        assert announcements[0]['id'] == 'new_event'
        assert announcements[0]['message'] == 'Test message'

    def test_rejects_duplicate_id(self, capsys):
        announcements = list(SAMPLE_ANNOUNCEMENTS)
        with patch('builtins.input', return_value='test_event'):
            ma.add_text_announcement(announcements)
        assert "already exists" in capsys.readouterr().out
        assert len(announcements) == len(SAMPLE_ANNOUNCEMENTS)


# ---------------------------------------------------------------------------
# add_image_announcement
# ---------------------------------------------------------------------------

class TestAddImageAnnouncement:
    def test_adds_new_image_announcement(self, tmp_path):
        ann_file = tmp_path / "announcements.json"
        announcements = []

        inputs = iter([
            'img_event',                    # id
            '/static/images/Test.jpg',      # image path
            '2027-06-01',                   # start date
            '09:00',                        # start time
            '2027-06-30',                   # end date
            '23:59',                        # end time
            '1',                            # frequency
            '60',                           # duration
            'n',                            # is special
            'n',                            # avoid jamaah
        ])

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', side_effect=inputs):
            ma.add_image_announcement(announcements)

        assert len(announcements) == 1
        ann = announcements[0]
        assert ann['id'] == 'img_event'
        assert ann['type'] == 'image'
        assert '/static/images/Test.jpg' in ann['images']

    def test_rejects_duplicate_id(self, capsys):
        announcements = list(SAMPLE_ANNOUNCEMENTS)
        with patch('builtins.input', return_value='test_event'):
            ma.add_image_announcement(announcements)
        assert "already exists" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# delete_announcement
# ---------------------------------------------------------------------------

class TestDeleteAnnouncement:
    def test_deletes_with_confirmation(self, tmp_path, capsys):
        ann_file = tmp_path / "announcements.json"
        announcements = [dict(a) for a in SAMPLE_ANNOUNCEMENTS]

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', side_effect=['1', 'y']):
            ma.delete_announcement(announcements)

        assert len(announcements) == 2
        assert "deleted" in capsys.readouterr().out

    def test_does_not_delete_on_no_confirmation(self, tmp_path):
        ann_file = tmp_path / "announcements.json"
        announcements = [dict(a) for a in SAMPLE_ANNOUNCEMENTS]

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', side_effect=['1', 'n']):
            ma.delete_announcement(announcements)

        assert len(announcements) == 3

    def test_invalid_index(self, tmp_path, capsys):
        ann_file = tmp_path / "announcements.json"
        announcements = [dict(a) for a in SAMPLE_ANNOUNCEMENTS]

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', side_effect=['99', 'y']):
            ma.delete_announcement(announcements)

        assert len(announcements) == 3
        assert "Invalid" in capsys.readouterr().out

    def test_non_numeric_input(self, tmp_path, capsys):
        ann_file = tmp_path / "announcements.json"
        announcements = [dict(a) for a in SAMPLE_ANNOUNCEMENTS]

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', return_value='abc'):
            ma.delete_announcement(announcements)

        assert len(announcements) == 3


# ---------------------------------------------------------------------------
# toggle_visibility
# ---------------------------------------------------------------------------

class TestToggleVisibility:
    def test_hides_active_announcement(self, tmp_path):
        ann_file = tmp_path / "announcements.json"
        announcements = [dict(a) for a in SAMPLE_ANNOUNCEMENTS]

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', return_value='1'):
            ma.toggle_visibility(announcements)

        assert announcements[0]['hide'] is True

    def test_shows_hidden_announcement(self, tmp_path):
        ann_file = tmp_path / "announcements.json"
        announcements = [dict(a) for a in SAMPLE_ANNOUNCEMENTS]

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', return_value='2'):
            ma.toggle_visibility(announcements)

        assert announcements[1]['hide'] is False

    def test_invalid_index(self, tmp_path, capsys):
        ann_file = tmp_path / "announcements.json"
        announcements = [dict(a) for a in SAMPLE_ANNOUNCEMENTS]

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', return_value='99'):
            ma.toggle_visibility(announcements)

        assert "Invalid" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# main_menu
# ---------------------------------------------------------------------------

class TestMainMenu:
    def test_exits_on_choice_6(self, tmp_path, capsys):
        ann_file = tmp_path / "announcements.json"
        ann_file.write_text(json.dumps(SAMPLE_ANNOUNCEMENTS))

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', return_value='6'):
            ma.main_menu()

        assert "Goodbye" in capsys.readouterr().out

    def test_returns_when_file_missing(self, capsys):
        with patch.object(ma, 'ANNOUNCEMENTS_FILE', 'nonexistent.json'):
            ma.main_menu()

        assert "not found" in capsys.readouterr().out

    def test_invalid_choice_then_exit(self, tmp_path, capsys):
        ann_file = tmp_path / "announcements.json"
        ann_file.write_text(json.dumps(SAMPLE_ANNOUNCEMENTS))

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', side_effect=['9', '6']):
            ma.main_menu()

        assert "Invalid" in capsys.readouterr().out

    def test_view_called_on_choice_1(self, tmp_path):
        ann_file = tmp_path / "announcements.json"
        ann_file.write_text(json.dumps(SAMPLE_ANNOUNCEMENTS))

        with patch.object(ma, 'ANNOUNCEMENTS_FILE', str(ann_file)), \
             patch('builtins.input', side_effect=['1', '6']), \
             patch.object(ma, 'list_announcements') as mock_list:
            ma.main_menu()

        mock_list.assert_called()
