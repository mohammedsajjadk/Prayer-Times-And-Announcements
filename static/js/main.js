/**
 * Prayer Times Application - Main Module
 * Coordinates the initialization and updates of all other modules
 */

// Default settings — used when settings.json cannot be loaded
var DEFAULT_SETTINGS = {
  scheduledRefreshTimes: [
    {h:0,m:0},{h:3,m:30},{h:6,m:30},{h:10,m:30},{h:12,m:30},
    {h:14,m:12},{h:16,m:30},{h:17,m:30},{h:18,m:30},{h:19,m:45},{h:21,m:15}
  ],
  jumuah: { summer: '13:45', winter: '13:20' },
  selectedTheme: 'theme1',
  labels: { column1: 'BEGINNING', column2: "JAMA'AH" },
  adhkar: {
    fridayZohrSummer: '14:10',
    fridayZohrWinter: '13:42',
    fridayZohrWindowMinutes: 3,
    fridayZohrPoster1Seconds: 90,
    prayers: {
      fajr:   { delayAfterJamaah: 8, displayWindowMinutes: 3, poster1Seconds: 90 },
      zohr:   { delayAfterJamaah: 8, displayWindowMinutes: 3, poster1Seconds: 90 },
      asr:    { delayAfterJamaah: 8, displayWindowMinutes: 3, poster1Seconds: 90 },
      magrib: { delayAfterJamaah: 8, displayWindowMinutes: 3, poster1Seconds: 90 },
      isha:   { delayAfterJamaah: 8, displayWindowMinutes: 3, poster1Seconds: 90 }
    }
  }
};

// Expose DEFAULT_SETTINGS as fallback so themes.js can read it before appSettings is available
window._DEFAULT_SETTINGS_FALLBACK = DEFAULT_SETTINGS;

function applyColumnLabels(settings) {
  var lbl = (settings && settings.labels) || DEFAULT_SETTINGS.labels;
  var col1 = document.getElementById('col1-header');
  var col2 = document.getElementById('col2-header');
  if (col1) col1.textContent = lbl.column1 || 'BEGINNING';
  if (col2) col2.textContent = lbl.column2 || "JAMA'AH";
}

// Check if (h, m) matches the current Irish time within a 2-second window
function isScheduledRefreshTime(h, m, irishH, irishM, irishS) {
  return irishH === h && irishM === m && irishS <= 2;
}

// Load settings.json from GitHub/local; fall back to DEFAULT_SETTINGS silently
fetch('/static/data/' + (window.MOSQUE_SLUG || 'tralee') + '/settings.json')
  .then(function(r) { return r.json(); })
  .then(function(s) { window.appSettings = s; applyColumnLabels(s); })
  .catch(function() { applyColumnLabels(DEFAULT_SETTINGS); });

// Main application object
var app = {  // Initialize the application
  initialize: function() {
    // Initialize test mode if enabled
    if (testMode.enabled) {
      testMode.start();
    }
    
    // Initial updates
    timeModule.updateTime();
    prayerModule.updateNextPrayer();
    announcementModule.updateAnnouncement();
    timeModule.convertTo12Hour();

    // Set initial Jumuah time based on Summer/Winter time on page load
    var now = testMode.enabled ? testMode.getMockDate() : new Date();
    var isIrishSummerTime = dateUtils.isIrelandDST(now);
    var jumuahElement = document.querySelector(".jamaah .prayer-time-value:nth-child(7)");
    if (jumuahElement) {
      var _jCfg = (window.appSettings || DEFAULT_SETTINGS).jumuah;
      var jumuahTime = isIrishSummerTime ? (_jCfg.summer || '13:45') : (_jCfg.winter || '13:20');
      jumuahElement.setAttribute("data-time", jumuahTime);
      jumuahElement.textContent = timeUtils.formatTimeFor12Hour(jumuahTime);
    }
    prayerModule.updateJumuahTimes();
    prayerModule.updateToNextDayTimesIfNeeded();

    // Initialize theme system
    themeModule.init();

    // Store interval reference for cleanup
    window.mainInterval = setInterval(function() {
      // Handle regular UI updates
      prayerModule.updateNextPrayer();
      announcementModule.updateAnnouncement();
      timeModule.convertTo12Hour();
      prayerModule.updateJumuahTimes();
      prayerModule.updateToNextDayTimesIfNeeded();

      // Check for midnight refresh and 4:30 PM refresh
      var now = testMode.enabled ? testMode.getMockDate() : new Date();
      var isIrishSummerTime = dateUtils.isIrelandDST(now);
      var irishOffset = isIrishSummerTime ? 1 : 0;
      var irishHours = now.getUTCHours() + irishOffset;
      irishHours = irishHours >= 24 ? irishHours - 24 : irishHours;
      var irishMins = now.getUTCMinutes();
      var irishSecs = now.getUTCSeconds();

      // Check for fixed scheduled refreshes (times from settings.json)
      var refreshTimes = (window.appSettings || DEFAULT_SETTINGS).scheduledRefreshTimes;
      var shouldRefresh = refreshTimes.some(function(t) {
        return isScheduledRefreshTime(t.h, t.m, irishHours, irishMins, irishSecs);
      });

      // Check for Friday 5-minute refresh between 13:48 and 15:45
      var currentDay = testMode.enabled ? testMode.dayOfWeek : now.getUTCDay();
      if (!testMode.enabled && irishHours < now.getUTCHours()) {
        currentDay = (currentDay + 1) % 7;
      }
      
      if (currentDay === 5 && irishSecs <= 2) { // Friday
        var currentTimeMinutes = irishHours * 60 + irishMins;
        var startTime = 13 * 60 + 48; // 13:48
        var endTime = 15 * 60 + 45;   // 15:45
        
        if (currentTimeMinutes >= startTime && currentTimeMinutes <= endTime) {
          // Check if current minute is a multiple of 5 from start time
          var minutesFromStart = currentTimeMinutes - startTime;
          if (minutesFromStart % 5 === 0) {
            shouldRefresh = true;
          }
        }
      }

      // Check for dynamic refreshes 30 minutes before each Jamaah time
      if (!shouldRefresh && irishSecs <= 2) {
        // Get current Jamaah times
        var jamaahTimes = [
          document.querySelector(".jamaah .prayer-time-value:nth-child(2)"), // Fajr
          document.querySelector(".jamaah .prayer-time-value:nth-child(3)"), // Zohr
          document.querySelector(".jamaah .prayer-time-value:nth-child(4)"), // Asr
          document.querySelector(".jamaah .prayer-time-value:nth-child(5)"), // Maghrib
          document.querySelector(".jamaah .prayer-time-value:nth-child(6)"), // Isha
          document.querySelector(".jamaah .prayer-time-value:nth-child(7)")  // Jumuah
        ];

        for (var i = 0; i < jamaahTimes.length; i++) {
          if (jamaahTimes[i]) {
            var jamaahTimeStr = jamaahTimes[i].getAttribute('data-time');
            if (jamaahTimeStr) {
              var jamaahParts = jamaahTimeStr.split(':');
              if (jamaahParts.length === 2) {
                var jamaahHour = parseInt(jamaahParts[0]);
                var jamaahMin = parseInt(jamaahParts[1]);
                
                // Calculate 30 minutes before
                var refreshMin = jamaahMin - 30;
                var refreshHour = jamaahHour;
                if (refreshMin < 0) {
                  refreshMin += 60;
                  refreshHour -= 1;
                  if (refreshHour < 0) {
                    refreshHour += 24;
                  }
                }
                
                // Check if current time matches refresh time (30 min before Jamaah)
                if (irishHours === refreshHour && irishMins === refreshMin) {
                  shouldRefresh = true;
                  break;
                }
              }
            }
          }
        }
      }

      if (shouldRefresh) {
        timeModule.persistentRefresh();
      }

      // Lighter drift checking - only once every 10 seconds
      if (now.getUTCSeconds() % 10 === 0) {
        var displayedSeconds = document.querySelector('.time-sub .seconds');
        if (displayedSeconds) {
          var displayedSecondsValue = parseInt(displayedSeconds.textContent, 10);
          if (isNaN(displayedSecondsValue) || Math.abs(now.getUTCSeconds() - displayedSecondsValue) > 1) {
            if (window.timeUpdateTimeout) {
              clearTimeout(window.timeUpdateTimeout);
            }
            timeModule.updateTime();
          }
        }
      }
    }, 1000);

    // Force time sync every 30 seconds as a backup measure
    window.timeRefreshInterval = setInterval(function() {
      if (window.timeUpdateTimeout) {
        clearTimeout(window.timeUpdateTimeout);
      }
      timeModule.updateTime();
    }, 30000);
  }
};

// Start the application when the DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", app.initialize);
} else {
  app.initialize();
}
