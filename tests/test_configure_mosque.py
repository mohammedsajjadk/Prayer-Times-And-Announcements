"""Tests for configure_mosque.py"""

import json
import os
import pytest
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import configure_mosque as cm


# ---------------------------------------------------------------------------
# Sample config
# ---------------------------------------------------------------------------

SAMPLE_CONFIG = {
    "mosque": {
        "name": "Test Masjid",
        "location": "Test City, Ireland",
        "displayName": "Test Masjid"
    },
    "timezone": {
        "name": "Europe/Dublin",
        "hasDST": True,
        "standardOffset": 0,
        "dstOffset": 1
    },
    "jumuah": {
        "summer": {"time": "13:45", "description": "Summer Jumuah"},
        "winter": {"time": "13:20", "description": "Winter Jumuah"}
    },
    "adhkar": {
        "enabled": True,
        "posterPath": "/static/images/Adhkar.jpg",
        "displayAfterJamaah": True,
        "delayMinutes": 8,
        "durationMinutes": 4,
        "fridayZohrSpecialTimes": {"summer": "14:10", "winter": "13:42"},
        "excludeFridayZohr": False
    },
    "display": {
        "title": "Prayer Times",
        "showIslamicDate": True,
        "showGregorianDate": True,
        "defaultTheme": "theme1",
        "availableThemes": ["theme1", "theme2"]
    },
    "defaults": {
        "announcementDuration": 60,
        "imageDuration": 60,
        "avoidJamaahTime": True
    }
}


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

class TestLoadConfig:
    def test_loads_valid_file(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        cfg_file.write_text(json.dumps(SAMPLE_CONFIG))

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)):
            result = cm.load_config()

        assert result['mosque']['name'] == 'Test Masjid'

    def test_returns_none_when_missing(self, capsys):
        with patch.object(cm, 'CONFIG_FILE', 'nonexistent.json'):
            result = cm.load_config()

        assert result is None
        assert "not found" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# save_config
# ---------------------------------------------------------------------------

class TestSaveConfig:
    def test_writes_config(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)):
            cm.save_config(SAMPLE_CONFIG)

        saved = json.loads(cfg_file.read_text())
        assert saved['mosque']['name'] == 'Test Masjid'

    def test_prints_confirmation(self, tmp_path, capsys):
        cfg_file = tmp_path / "mosque_config.json"

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)):
            cm.save_config(SAMPLE_CONFIG)

        assert "saved" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# view_config
# ---------------------------------------------------------------------------

class TestViewConfig:
    def test_shows_mosque_details(self, capsys):
        cm.view_config(SAMPLE_CONFIG)
        out = capsys.readouterr().out
        assert "Test Masjid" in out
        assert "Europe/Dublin" in out
        assert "13:45" in out
        assert "13:20" in out


# ---------------------------------------------------------------------------
# configure_mosque_details
# ---------------------------------------------------------------------------

class TestConfigureMosqueDetails:
    def test_updates_name(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        config = {k: dict(v) if isinstance(v, dict) else v
                  for k, v in SAMPLE_CONFIG.items()}
        config['mosque'] = dict(SAMPLE_CONFIG['mosque'])

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['New Masjid', '']):
            cm.configure_mosque_details(config)

        assert config['mosque']['name'] == 'New Masjid'
        assert config['mosque']['displayName'] == 'New Masjid'

    def test_keeps_existing_when_empty_input(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        config = {k: dict(v) if isinstance(v, dict) else v
                  for k, v in SAMPLE_CONFIG.items()}
        config['mosque'] = dict(SAMPLE_CONFIG['mosque'])

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['', '']):
            cm.configure_mosque_details(config)

        assert config['mosque']['name'] == 'Test Masjid'


# ---------------------------------------------------------------------------
# configure_jumuah_times
# ---------------------------------------------------------------------------

class TestConfigureJumuahTimes:
    def test_updates_summer_time(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        import copy
        config = copy.deepcopy(SAMPLE_CONFIG)

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['14:00', '']):
            cm.configure_jumuah_times(config)

        assert config['jumuah']['summer']['time'] == '14:00'

    def test_keeps_existing_when_empty(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        import copy
        config = copy.deepcopy(SAMPLE_CONFIG)

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['', '']):
            cm.configure_jumuah_times(config)

        assert config['jumuah']['summer']['time'] == '13:45'
        assert config['jumuah']['winter']['time'] == '13:20'


# ---------------------------------------------------------------------------
# configure_adhkar_settings
# ---------------------------------------------------------------------------

class TestConfigureAdhkarSettings:
    def test_disables_adhkar(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        import copy
        config = copy.deepcopy(SAMPLE_CONFIG)

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['n', '', '', '', '']):
            cm.configure_adhkar_settings(config)

        assert config['adhkar']['enabled'] is False

    def test_updates_delay_minutes(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        import copy
        config = copy.deepcopy(SAMPLE_CONFIG)

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['y', '10', '', '', '']):
            cm.configure_adhkar_settings(config)

        assert config['adhkar']['delayMinutes'] == 10


# ---------------------------------------------------------------------------
# configure_timezone
# ---------------------------------------------------------------------------

class TestConfigureTimezone:
    def test_updates_timezone(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        import copy
        config = copy.deepcopy(SAMPLE_CONFIG)

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['Europe/London', 'y']):
            cm.configure_timezone(config)

        assert config['timezone']['name'] == 'Europe/London'
        assert config['timezone']['hasDST'] is True

    def test_disables_dst(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        import copy
        config = copy.deepcopy(SAMPLE_CONFIG)

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['', 'n']):
            cm.configure_timezone(config)

        assert config['timezone']['hasDST'] is False


# ---------------------------------------------------------------------------
# reset_to_defaults
# ---------------------------------------------------------------------------

class TestResetToDefaults:
    def test_resets_on_confirmation(self, tmp_path, capsys):
        cfg_file = tmp_path / "mosque_config.json"

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', return_value='yes'):
            cm.reset_to_defaults()

        saved = json.loads(cfg_file.read_text())
        assert saved['mosque']['name'] == 'Tralee Masjid'
        assert "reset" in capsys.readouterr().out

    def test_cancels_without_confirmation(self, tmp_path, capsys):
        cfg_file = tmp_path / "mosque_config.json"
        cfg_file.write_text(json.dumps(SAMPLE_CONFIG))

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', return_value='no'):
            cm.reset_to_defaults()

        # File should be unchanged
        saved = json.loads(cfg_file.read_text())
        assert saved['mosque']['name'] == 'Test Masjid'
        assert "cancelled" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# main_menu
# ---------------------------------------------------------------------------

class TestMainMenu:
    def test_exits_on_choice_7(self, tmp_path, capsys):
        cfg_file = tmp_path / "mosque_config.json"
        cfg_file.write_text(json.dumps(SAMPLE_CONFIG))

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', return_value='7'):
            cm.main_menu()

        assert "Goodbye" in capsys.readouterr().out

    def test_returns_when_config_missing(self, capsys):
        with patch.object(cm, 'CONFIG_FILE', 'nonexistent.json'):
            cm.main_menu()

        assert "not found" in capsys.readouterr().out

    def test_view_config_called_on_choice_1(self, tmp_path):
        cfg_file = tmp_path / "mosque_config.json"
        cfg_file.write_text(json.dumps(SAMPLE_CONFIG))

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['1', '7']), \
             patch.object(cm, 'view_config') as mock_view:
            cm.main_menu()

        mock_view.assert_called()

    def test_invalid_choice_then_exit(self, tmp_path, capsys):
        cfg_file = tmp_path / "mosque_config.json"
        cfg_file.write_text(json.dumps(SAMPLE_CONFIG))

        with patch.object(cm, 'CONFIG_FILE', str(cfg_file)), \
             patch('builtins.input', side_effect=['9', '7']):
            cm.main_menu()

        assert "Invalid" in capsys.readouterr().out
