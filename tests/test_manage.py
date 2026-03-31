"""Tests for manage.py"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manage


# ---------------------------------------------------------------------------
# view_system_status
# ---------------------------------------------------------------------------

class TestViewSystemStatus:
    def test_shows_announcement_count(self, tmp_path, capsys):
        ann_data = [{"id": "a", "hide": False}, {"id": "b", "hide": True}]
        prayer_content = "HEADER\nrow1\nrow2\n"

        def fake_exists(path):
            if 'Adhkar' in str(path):
                return False
            return True

        real_open = open
        def fake_open(path, *args, **kwargs):
            import io
            if 'announcements' in str(path):
                return io.StringIO(json.dumps(ann_data))
            if 'prayer_times' in str(path):
                return io.StringIO(prayer_content)
            return real_open(path, *args, **kwargs)

        with patch('manage.os.path.exists', side_effect=fake_exists), \
             patch('builtins.open', side_effect=fake_open), \
             patch('manage.os.listdir', return_value=['a.jpg', 'b.png', 'text.txt']):
            manage.view_system_status()

        out = capsys.readouterr().out
        assert "Announcements" in out
        assert "1 active" in out

    def test_shows_missing_files(self, capsys):
        with patch('manage.os.path.exists', return_value=False):
            manage.view_system_status()
        out = capsys.readouterr().out
        assert "not found" in out


# ---------------------------------------------------------------------------
# show_help
# ---------------------------------------------------------------------------

class TestShowHelp:
    def test_prints_help_content(self, capsys):
        manage.show_help()
        out = capsys.readouterr().out
        assert "manage_announcements.py" in out
        assert "manage_prayer_times.py" in out
        assert "configure_mosque.py" in out
        assert "app.py" in out


# ---------------------------------------------------------------------------
# main_menu
# ---------------------------------------------------------------------------

class TestMainMenu:
    def test_exits_on_choice_6(self, capsys):
        with patch('builtins.input', return_value='6'):
            manage.main_menu()
        out = capsys.readouterr().out
        assert "Goodbye" in out or "May Allah" in out

    def test_invalid_choice_then_exit(self, capsys):
        with patch('builtins.input', side_effect=['9', '6']):
            manage.main_menu()
        assert "Invalid" in capsys.readouterr().out

    def test_view_system_status_on_choice_4(self):
        with patch('builtins.input', side_effect=['4', '6']), \
             patch.object(manage, 'view_system_status') as mock_status:
            manage.main_menu()
        mock_status.assert_called_once()

    def test_show_help_on_choice_5(self):
        with patch('builtins.input', side_effect=['5', '6']), \
             patch.object(manage, 'show_help') as mock_help:
            manage.main_menu()
        mock_help.assert_called_once()

    def test_run_script_called_for_announcements(self):
        with patch('builtins.input', side_effect=['1', '6']), \
             patch.object(manage, 'run_script') as mock_run:
            manage.main_menu()
        mock_run.assert_called_once_with('manage_announcements.py')

    def test_run_script_called_for_prayer_times(self):
        with patch('builtins.input', side_effect=['2', '6']), \
             patch.object(manage, 'run_script') as mock_run:
            manage.main_menu()
        mock_run.assert_called_once_with('manage_prayer_times.py')

    def test_run_script_called_for_configure(self):
        with patch('builtins.input', side_effect=['3', '6']), \
             patch.object(manage, 'run_script') as mock_run:
            manage.main_menu()
        mock_run.assert_called_once_with('configure_mosque.py')


# ---------------------------------------------------------------------------
# run_script
# ---------------------------------------------------------------------------

class TestRunScript:
    def test_calls_subprocess(self):
        with patch('manage.subprocess.run') as mock_run:
            manage.run_script('some_script.py')
        mock_run.assert_called_once()

    def test_handles_file_not_found(self, capsys):
        import subprocess
        with patch('manage.subprocess.run', side_effect=FileNotFoundError):
            manage.run_script('missing.py')
        assert "not found" in capsys.readouterr().out

    def test_handles_called_process_error(self, capsys):
        import subprocess
        with patch('manage.subprocess.run',
                   side_effect=subprocess.CalledProcessError(1, 'cmd')):
            manage.run_script('failing.py')
        assert "Error" in capsys.readouterr().out
