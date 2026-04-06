"""Tests for manage_prayer_times.py"""

import csv
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock, call
from io import StringIO

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manage_prayer_times as mpt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_CSV = (
    "MONTH,DATE,FAJR BEGINNING,SUNRISE BEGINNING,ZOHR BEGINNING,"
    "ASAR BEGINNING,MAGRIB BEGINNING,ISHA BEGINNING,"
    "FAJR JAMAAH,ZOHR JAMAAH,ASAR JAMAAH,MAGRIB JAMAAH,ISHA JAMAAH\n"
    "3,1,05:31,07:24,12:52,16:26,18:21,19:41,05:40,13:15,17:15,18:31,20:15\n"
    "3,2,05:28,07:22,12:51,16:28,18:23,19:43,05:40,13:15,17:15,18:33,20:15\n"
)


# ---------------------------------------------------------------------------
# ensure_backup_dir
# ---------------------------------------------------------------------------

class TestEnsureBackupDir:
    def test_creates_directory_when_missing(self, tmp_path):
        backup_dir = str(tmp_path / "backups")
        mpt.ensure_backup_dir(backup_dir)
        assert os.path.isdir(backup_dir)

    def test_does_nothing_when_directory_exists(self, tmp_path):
        backup_dir = str(tmp_path / "backups")
        os.makedirs(backup_dir)
        mpt.ensure_backup_dir(backup_dir)  # should not raise
        assert os.path.isdir(backup_dir)


# ---------------------------------------------------------------------------
# backup_prayer_times
# ---------------------------------------------------------------------------

class TestBackupPrayerTimes:
    def test_creates_backup_file(self, tmp_path):
        csv_file = tmp_path / "prayer_times.csv"
        csv_file.write_text(SAMPLE_CSV)
        backup_dir = str(tmp_path / "backups")

        result = mpt.backup_prayer_times(str(csv_file), backup_dir)

        assert os.path.exists(result)
        assert "prayer_times_backup_" in result

    def test_returns_backup_path(self, tmp_path):
        csv_file = tmp_path / "prayer_times.csv"
        csv_file.write_text(SAMPLE_CSV)
        backup_dir = str(tmp_path / "backups")

        result = mpt.backup_prayer_times(str(csv_file), backup_dir)

        assert result.endswith(".csv")


# ---------------------------------------------------------------------------
# view_prayer_times
# ---------------------------------------------------------------------------

class TestViewPrayerTimes:
    def test_shows_error_when_file_missing(self, capsys):
        mpt.view_prayer_times('nonexistent.csv')
        assert "not found" in capsys.readouterr().out

    def test_prints_prayer_times(self, tmp_path, capsys):
        csv_file = tmp_path / "prayer_times.csv"
        csv_file.write_text(SAMPLE_CSV)

        mpt.view_prayer_times(str(csv_file))

        out = capsys.readouterr().out
        assert "CURRENT PRAYER TIMES" in out
        assert "05:31" in out


# ---------------------------------------------------------------------------
# convert_time_format
# ---------------------------------------------------------------------------

class TestConvertTimeFormat:
    def test_already_24hr_format(self):
        assert mpt.convert_time_format("05:30") == "05:30"
        assert mpt.convert_time_format("14:00") == "14:00"

    def test_decimal_format_afternoon(self):
        assert mpt.convert_time_format("2.00") == "14:00"
        assert mpt.convert_time_format("5.15") == "17:15"

    def test_empty_string_returns_none(self):
        assert mpt.convert_time_format("") is None

    def test_quote_placeholder_returns_none(self):
        assert mpt.convert_time_format('"') is None

    def test_single_digit_hour(self):
        assert mpt.convert_time_format("9:05") == "09:05"

    def test_strips_whitespace(self):
        assert mpt.convert_time_format("  05:30  ") == "05:30"


# ---------------------------------------------------------------------------
# validate_prayer_times (now delegates to PrayerTimeValidator)
# ---------------------------------------------------------------------------

MOCK_VALIDATOR_RESULT = {
    "month": 3, "total_rows": 2,
    "date_validation": {"is_valid": True, "missing_dates": [], "extra_dates": [], "expected_range": "1-2", "actual_dates": [1, 2]},
    "fajr_beginning_validation": {"is_valid": True, "expected_pattern": "decrement", "violations": [], "total_violations": 0},
    "sunrise_beginning_validation": {"is_valid": True, "expected_pattern": "decrement", "violations": [], "total_violations": 0},
    "zohr_beginning_validation": {"is_valid": True, "expected_pattern": "increment", "violations": [], "total_violations": 0},
    "asar_beginning_validation": {"is_valid": True, "expected_pattern": "increment", "violations": [], "total_violations": 0},
    "magrib_beginning_validation": {"is_valid": True, "expected_pattern": "increment", "violations": [], "total_violations": 0},
    "isha_beginning_validation": {"is_valid": True, "expected_pattern": "increment", "violations": [], "total_violations": 0},
    "zohr_jamaah_validation": {"is_valid": True, "violations": [], "total_violations": 0},
    "magrib_jamaah_validation": {"is_valid": True, "violations": [], "total_violations": 0},
}


class TestValidatePrayerTimes:
    def test_error_when_csv_missing(self, capsys):
        mpt.validate_prayer_times('nonexistent.csv')
        assert "not found" in capsys.readouterr().out

    def test_calls_validator_for_specific_month(self, tmp_path, capsys):
        csv_file = tmp_path / "prayer_times.csv"
        csv_file.write_text(SAMPLE_CSV)

        mock_validator = MagicMock()
        mock_validator.validate_month.return_value = MOCK_VALIDATOR_RESULT

        with patch('prayer_time_validator.PrayerTimeValidator', return_value=mock_validator), \
             patch('builtins.input', return_value='3'):
            mpt.validate_prayer_times(str(csv_file))

        mock_validator.validate_month.assert_called_once_with(3)

    def test_validate_all_months(self, tmp_path):
        csv_file = tmp_path / "prayer_times.csv"
        csv_file.write_text(SAMPLE_CSV)

        mock_validator = MagicMock()
        mock_validator.validate_month.return_value = MOCK_VALIDATOR_RESULT

        with patch('prayer_time_validator.PrayerTimeValidator', return_value=mock_validator), \
             patch('builtins.input', return_value='all'):
            mpt.validate_prayer_times(str(csv_file))

        mock_validator.validate_month.assert_called_once_with(3)

    def test_back_exits_without_validating(self, tmp_path):
        csv_file = tmp_path / "prayer_times.csv"
        csv_file.write_text(SAMPLE_CSV)

        mock_validator = MagicMock()

        with patch('prayer_time_validator.PrayerTimeValidator', return_value=mock_validator), \
             patch('builtins.input', return_value='back'):
            mpt.validate_prayer_times(str(csv_file))

        mock_validator.validate_month.assert_not_called()

    def test_invalid_month_number_reprompts(self, tmp_path):
        csv_file = tmp_path / "prayer_times.csv"
        csv_file.write_text(SAMPLE_CSV)

        mock_validator = MagicMock()
        mock_validator.validate_month.return_value = MOCK_VALIDATOR_RESULT

        with patch('prayer_time_validator.PrayerTimeValidator', return_value=mock_validator), \
             patch('builtins.input', side_effect=['99', '3']):
            mpt.validate_prayer_times(str(csv_file))

        mock_validator.validate_month.assert_called_once_with(3)


# ---------------------------------------------------------------------------
# main_menu
# ---------------------------------------------------------------------------

class TestMainMenu:
    def test_exit_on_choice_6(self, tmp_path, capsys):
        # input('1') selects mosque 1, input('6') exits
        with patch('builtins.input', side_effect=['1', '6']):
            mpt.main_menu()
        assert "Goodbye" in capsys.readouterr().out

    def test_invalid_choice_then_exit(self, capsys):
        # input('1') selects mosque 1, input('9') invalid, input('6') exits
        with patch('builtins.input', side_effect=['1', '9', '6']):
            mpt.main_menu()
        out = capsys.readouterr().out
        assert "Invalid" in out

    def test_view_prayer_times_called_on_choice_1(self, tmp_path):
        # input('1') selects mosque, input('1') = view, input('6') = exit
        with patch('builtins.input', side_effect=['1', '1', '6']), \
             patch.object(mpt, 'view_prayer_times') as mock_view:
            mpt.main_menu()
        mock_view.assert_called_once()

    def test_backup_called_on_choice_4(self, tmp_path):
        # input('1') selects mosque, input('4') = backup, input('6') = exit
        with patch('builtins.input', side_effect=['1', '4', '6']), \
             patch.object(mpt, 'backup_prayer_times') as mock_backup:
            mpt.main_menu()
        mock_backup.assert_called_once()
