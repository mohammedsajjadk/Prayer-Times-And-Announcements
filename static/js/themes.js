/**
 * Prayer Times Application - Theme Module
 * Handles the theme selection and application functionality.
 * Active theme is stored in settings.json (selectedTheme) and applied on load.
 */

// Theme configurations — 20 themes total
var themes = {
  // 1. Dark Navy (default) — original deep-blue look
  theme1: {
    name: 'Dark Navy',
    '--bg-color': '#001529',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#00F0FF',
    '--border-color': '#0088FF',
    '--announcement-bg-color': '#000C17',
    '--announcement-text-color': '#FFFFFF',
    '--announcement-warning': '#ff0000',
    '--next-prayer-border-color': 'rgba(0, 240, 255, 0.8)'
  },
  // 2. Clean White-Blue — light/daytime look
  theme2: {
    name: 'Clean White',
    '--bg-color': '#FFFFFF',
    '--text-color': '#003366',
    '--highlight-color': '#0055CC',
    '--border-color': '#4499FF',
    '--announcement-bg-color': '#EEF4FF',
    '--announcement-text-color': '#003366',
    '--announcement-warning': '#CC0000',
    '--next-prayer-border-color': 'rgba(0, 85, 204, 0.8)'
  },
  // 3. Navy Teal
  theme3: {
    name: 'Navy Teal',
    '--bg-color': '#0A192F',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#64FFDA',
    '--border-color': '#226e69',
    '--announcement-bg-color': '#000C17',
    '--announcement-text-color': '#FFFFFF',
    '--announcement-warning': '#ff0000',
    '--next-prayer-border-color': 'rgba(100, 255, 218, 0.8)'
  },
  // 4. White Cyan
  theme4: {
    name: 'White Cyan',
    '--bg-color': '#FFFFFF',
    '--text-color': '#00C0CC',
    '--highlight-color': '#FF0000',
    '--border-color': '#00B4D8',
    '--announcement-bg-color': '#F8F9FA',
    '--announcement-text-color': '#00C0CC',
    '--announcement-warning': '#FF4444',
    '--next-prayer-border-color': 'rgba(255, 0, 0, 0.8)'
  },
  // 5. White Teal
  theme5: {
    name: 'White Teal',
    '--bg-color': '#FFFFFF',
    '--text-color': '#13686e',
    '--highlight-color': '#FF0000',
    '--border-color': '#00B4D8',
    '--announcement-bg-color': '#F8F9FA',
    '--announcement-text-color': '#13686e',
    '--announcement-warning': '#FF4444',
    '--next-prayer-border-color': 'rgba(255, 0, 0, 0.8)'
  },
  // 6. Classic Blue — original bright-blue look
  theme6: {
    name: 'Classic Blue',
    '--bg-color': '#0099ff',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#000000',
    '--border-color': '#76B5C5',
    '--announcement-bg-color': '#000C17',
    '--announcement-text-color': '#FFFFFF',
    '--announcement-warning': '#ff0000',
    '--next-prayer-border-color': 'rgba(0, 0, 0, 0.8)'
  },
  // 7. Midnight Gold
  theme7: {
    name: 'Midnight Gold',
    '--bg-color': '#0D0D0D',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#FFD700',
    '--border-color': '#B8860B',
    '--announcement-bg-color': '#1A1A00',
    '--announcement-text-color': '#FFD700',
    '--announcement-warning': '#FF4500',
    '--next-prayer-border-color': 'rgba(255, 215, 0, 0.8)'
  },
  // 8. Deep Purple
  theme8: {
    name: 'Deep Purple',
    '--bg-color': '#1A0033',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#DA70D6',
    '--border-color': '#8A2BE2',
    '--announcement-bg-color': '#0D001A',
    '--announcement-text-color': '#DA70D6',
    '--announcement-warning': '#ff0000',
    '--next-prayer-border-color': 'rgba(218, 112, 214, 0.8)'
  },
  // 9. Forest Green
  theme9: {
    name: 'Forest Green',
    '--bg-color': '#0D1F0D',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#39FF14',
    '--border-color': '#228B22',
    '--announcement-bg-color': '#071407',
    '--announcement-text-color': '#39FF14',
    '--announcement-warning': '#FF4500',
    '--next-prayer-border-color': 'rgba(57, 255, 20, 0.8)'
  },
  // 10. Maroon Amber
  theme10: {
    name: 'Maroon Amber',
    '--bg-color': '#1C0000',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#FFBF00',
    '--border-color': '#800000',
    '--announcement-bg-color': '#0E0000',
    '--announcement-text-color': '#FFBF00',
    '--announcement-warning': '#ff0000',
    '--next-prayer-border-color': 'rgba(255, 191, 0, 0.8)'
  },
  // 11. Slate Orange
  theme11: {
    name: 'Slate Orange',
    '--bg-color': '#2F3542',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#FF6B35',
    '--border-color': '#5E6472',
    '--announcement-bg-color': '#1E2330',
    '--announcement-text-color': '#FF6B35',
    '--announcement-warning': '#FF0000',
    '--next-prayer-border-color': 'rgba(255, 107, 53, 0.8)'
  },
  // 12. Dark Teal
  theme12: {
    name: 'Dark Teal',
    '--bg-color': '#003333',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#00FFCC',
    '--border-color': '#007777',
    '--announcement-bg-color': '#001A1A',
    '--announcement-text-color': '#00FFCC',
    '--announcement-warning': '#ff0000',
    '--next-prayer-border-color': 'rgba(0, 255, 204, 0.8)'
  },
  // 13. Midnight Blue
  theme13: {
    name: 'Midnight Blue',
    '--bg-color': '#00008B',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#87CEEB',
    '--border-color': '#4169E1',
    '--announcement-bg-color': '#000066',
    '--announcement-text-color': '#FFFFFF',
    '--announcement-warning': '#FFD700',
    '--next-prayer-border-color': 'rgba(135, 206, 235, 0.8)'
  },
  // 14. Warm Dark
  theme14: {
    name: 'Warm Dark',
    '--bg-color': '#1A1209',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#FFA500',
    '--border-color': '#8B4513',
    '--announcement-bg-color': '#0D0904',
    '--announcement-text-color': '#FFA500',
    '--announcement-warning': '#FF0000',
    '--next-prayer-border-color': 'rgba(255, 165, 0, 0.8)'
  },
  // 15. Dark Indigo
  theme15: {
    name: 'Dark Indigo',
    '--bg-color': '#1A1A2E',
    '--text-color': '#E0E0E0',
    '--highlight-color': '#E94560',
    '--border-color': '#16213E',
    '--announcement-bg-color': '#0F0F1A',
    '--announcement-text-color': '#E94560',
    '--announcement-warning': '#FF0000',
    '--next-prayer-border-color': 'rgba(233, 69, 96, 0.8)'
  },
  // 16. Desert Sand
  theme16: {
    name: 'Desert Sand',
    '--bg-color': '#2C1810',
    '--text-color': '#F5DEB3',
    '--highlight-color': '#FF8C00',
    '--border-color': '#8B4513',
    '--announcement-bg-color': '#1A0F09',
    '--announcement-text-color': '#FF8C00',
    '--announcement-warning': '#FF0000',
    '--next-prayer-border-color': 'rgba(255, 140, 0, 0.8)'
  },
  // 17. High Contrast
  theme17: {
    name: 'High Contrast',
    '--bg-color': '#000000',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#FFFF00',
    '--border-color': '#888888',
    '--announcement-bg-color': '#111111',
    '--announcement-text-color': '#FFFF00',
    '--announcement-warning': '#FF0000',
    '--next-prayer-border-color': 'rgba(255, 255, 0, 0.8)'
  },
  // 18. Blue Grey
  theme18: {
    name: 'Blue Grey',
    '--bg-color': '#37474F',
    '--text-color': '#ECEFF1',
    '--highlight-color': '#80CBC4',
    '--border-color': '#546E7A',
    '--announcement-bg-color': '#263238',
    '--announcement-text-color': '#80CBC4',
    '--announcement-warning': '#FF5252',
    '--next-prayer-border-color': 'rgba(128, 203, 196, 0.8)'
  },
  // 19. Charcoal Green
  theme19: {
    name: 'Charcoal Green',
    '--bg-color': '#1C1C1C',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#00FF7F',
    '--border-color': '#2E7D32',
    '--announcement-bg-color': '#111111',
    '--announcement-text-color': '#00FF7F',
    '--announcement-warning': '#FF4500',
    '--next-prayer-border-color': 'rgba(0, 255, 127, 0.8)'
  },
  // 20. Crimson Dark
  theme20: {
    name: 'Crimson Dark',
    '--bg-color': '#14000A',
    '--text-color': '#FFFFFF',
    '--highlight-color': '#FF1493',
    '--border-color': '#8B0045',
    '--announcement-bg-color': '#0A0006',
    '--announcement-text-color': '#FF1493',
    '--announcement-warning': '#FFD700',
    '--next-prayer-border-color': 'rgba(255, 20, 147, 0.8)'
  }
};

var themeModule = {
  // Initialize theme system — reads selectedTheme from appSettings
  init: function() {
    this._applyFromSettings(0);
  },

  // Poll for appSettings availability (up to ~1000 ms) then apply
  _applyFromSettings: function(attempts) {
    var self = this;
    if (window.appSettings && window.appSettings.selectedTheme) {
      // Real settings have loaded — use them
      self.applyThemeByName(window.appSettings.selectedTheme);
    } else if (attempts < 20) {
      // Keep polling every 50 ms (max 20 × 50 ms = 1 s)
      setTimeout(function() { self._applyFromSettings(attempts + 1); }, 50);
    } else {
      // Settings never loaded — use the default fallback
      var fallbackTheme = (window._DEFAULT_SETTINGS_FALLBACK || {}).selectedTheme || 'theme1';
      self.applyThemeByName(fallbackTheme);
    }
  },

  // Apply a theme by its key name
  applyThemeByName: function(themeName) {
    var theme = themes[themeName];
    if (!theme) {
      theme = themes['theme1'];
    }
    this.applyTheme(theme);
  },

  // Apply a theme object to CSS custom properties on the document root
  applyTheme: function(theme) {
    var root = document.documentElement;
    for (var property in theme) {
      if (theme.hasOwnProperty(property) && property.indexOf('--') === 0) {
        root.style.setProperty(property, theme[property]);
      }
    }
  }
};
