/**
 * Prayer Times Application - Announcement Module
 * Manages announcements and special event messages
 */

// Core announcement texts and configurations
var announcements = {
  // Permanent announcements
  default:
    "SILENCE, PLEASE. WE ARE IN THE HOUSE OF ALLAH. KINDLY TURN OFF YOUR MOBILE.",

  // Regular recurring announcements
  thursday_darood: function () {
    return "DUROOD/SALAT-ALA-NABI صلى الله عليه وسلم GATHERING • THURSDAY AFTER ISHA";
  },

  friday_tafseer: function () {
    return "TAFSEER OF THE QUR'AN • SURAH TUR • FRIDAY AFTER ISHA";
  },

  clock_go_forward: function () {
    return "REMEMBER CLOCKS GO FORWARD 1 HOUR THIS SUNDAY";
  },

  clock_go_backward: function () {
    return "REMEMBER CLOCKS GO BACKWARD 1 HOUR THIS SUNDAY";
  },

  // Warnings - these are permanent and take priority
  warnings: {
    sunrise: function (sunriseTime, endTime) {
      return (
        "NO SALAH AFTER SUNRISE (" +
        timeUtils.formatTimeWithAmPm(sunriseTime) +
        ") • Please Wait Until " +
        timeUtils.formatTimeWithAmPm(endTime)
      );
    },
    zawal: function (zawalTime, zohrTime) {
      return (
        "NO SALAH AT ZAWAL TIME (" +
        timeUtils.formatTimeWithAmPm(zawalTime) +
        ") • Please Wait for Zohr to Begin (" +
        timeUtils.formatTimeWithAmPm(zohrTime) +
        ")"
      );
    },
    sunset: function (magribTime) {
      return (
        "NO SALAH DURING SUNSET • Please Wait for Magrib Adhan (" +
        timeUtils.formatTimeWithAmPm(magribTime) +
        ")"
      );
    },
  },
};

// Dynamic announcements loaded from external source
var dynamicAnnouncements = []; // Initialize as empty array to avoid undefined errors

// Track announcement display states
var displayState = {
  pausedAnnouncement: null,
  resumeTimeout: null
};

var announcementModule = {
  // Helper function to check if a control entry is hidden
  isControlHidden: function(controlId) {
    if (!dynamicAnnouncements || !Array.isArray(dynamicAnnouncements)) {
      return false; // Default to showing if JSON not loaded
    }
    
    var controlEntry = dynamicAnnouncements.find(function(announcement) {
      return announcement.id === controlId && announcement.type === "control";
    });
    
    return controlEntry ? (controlEntry.hide === true) : false;
  },

  init: function () {
    // Load dynamic announcements when the page loads
    this.loadDynamicAnnouncements();

    // Set up periodic refresh of dynamic announcements (e.g., every hour)
    setInterval(this.loadDynamicAnnouncements.bind(this), 60 * 60 * 1000);
  },

  // Load dynamic announcements from external file
  loadDynamicAnnouncements: function () {
    fetch('/static/data/' + (window.MOSQUE_SLUG || 'tralee') + '/announcements.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok: " + response.status);
        }
        return response.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          dynamicAnnouncements = data;
          console.log(
            "Loaded dynamic announcements:",
            dynamicAnnouncements.length
          );
        } else {
          console.error("Invalid announcements data format:", data);
          dynamicAnnouncements = [];
        }
        // Update announcements immediately after loading
        this.updateAnnouncement();
      })
      .catch((error) => {
        console.error("Error loading dynamic announcements:", error);
        // Fallback to empty array if loading fails
        dynamicAnnouncements = [];
        // Still attempt to update announcements with default values
        this.updateAnnouncement();
      });
  },

  // Find active announcement from the dynamic list based on current date/time
  getActiveDynamicAnnouncement: function (now) {
    // Ensure dynamicAnnouncements exists and has items
    if (
      !dynamicAnnouncements ||
      !Array.isArray(dynamicAnnouncements) ||
      dynamicAnnouncements.length === 0
    ) {
      return null;
    }

    var currentTime = now.getTime();
    var activeAnnouncements = {
      textAnnouncement: null,
      imageAnnouncements: [],
    };

    // Check all announcements
    for (var i = 0; i < dynamicAnnouncements.length; i++) {
      var announcement = dynamicAnnouncements[i];

      // Skip invalid announcements
      if (!announcement || !announcement.id) {
        continue;
      }

      var isActive = false;

      // Handle recurring weekly announcements
      if (announcement.type === "recurring_weekly") {
        isActive = this.isRecurringWeeklyActive(announcement, now);
        console.log("DEBUG: Recurring weekly check for", announcement.id, "- Active:", isActive, "Day:", now.getDay(), "Required:", announcement.dayOfWeek);
      }
      // Handle regular date-based announcements
      else if (announcement.startDate && announcement.endDate) {
        var startTime = new Date(announcement.startDate).getTime();
        var endTime = new Date(announcement.endDate).getTime();
        isActive = currentTime >= startTime && currentTime <= endTime;
        console.log("DEBUG: Date-based check for", announcement.id, 
                    "- Current:", new Date(currentTime).toISOString(),
                    "Start:", new Date(startTime).toISOString(), 
                    "End:", new Date(endTime).toISOString(),
                    "Active:", isActive);
      }

      if (isActive) {
        console.log("DEBUG: Found active announcement:", announcement.id, "Type:", announcement.type);
        // Handle both text messages and image announcements
        if (
          announcement.type === "image" ||
          (announcement.type === "recurring_weekly" && announcement.images)
        ) {
          console.log("DEBUG: Adding image announcement:", announcement.id, "Images:", announcement.images);
          activeAnnouncements.imageAnnouncements.push({
            id: announcement.id,
            isImage: true,
            images: announcement.images || [],
            displayCondition: announcement.displayCondition || {},
            isSpecial: announcement.isSpecial || false,
          });
        } else if (announcement.message) {
          console.log("DEBUG: Adding text announcement:", announcement.id);
          activeAnnouncements.textAnnouncement = {
            message: announcement.message || "",
            isSpecial: announcement.isSpecial || false,
          };
        }
      }
    }

    // Create rotation schedule if multiple are active
    if (activeAnnouncements.imageAnnouncements.length > 0) {
      var imageSchedule = this.createImageRotationSchedule(
        activeAnnouncements.imageAnnouncements
      );
      return {
        textAnnouncement: activeAnnouncements.textAnnouncement,
        imageAnnouncement: imageSchedule,
      };
    }

    return activeAnnouncements.textAnnouncement
      ? { textAnnouncement: activeAnnouncements.textAnnouncement }
      : null;
  },

  // Check if a recurring weekly announcement is currently active
  isRecurringWeeklyActive: function (announcement, now) {
    // Check if announcement is hidden
    if (announcement.hide === true) {
      return false;
    }

    // Check day of week
    var currentDay = testMode.enabled ? testMode.dayOfWeek : now.getUTCDay();
    if (!testMode.enabled) {
      var isIrishSummerTime = dateUtils.isIrelandDST(now);
      var irishOffset = isIrishSummerTime ? 1 : 0;
      var irishHours = now.getUTCHours() + irishOffset;
      if (irishHours < now.getUTCHours()) {
        currentDay = (currentDay + 1) % 7;
      }
    }

    if (currentDay !== announcement.dayOfWeek) {
      return false;
    }

    // Get current time in minutes
    var currentTime;
    if (testMode.enabled) {
      currentTime = testMode.getCurrentTimeMinutes();
    } else {
      var isIrishSummerTime = dateUtils.isIrelandDST(now);
      var irishOffset = isIrishSummerTime ? 1 : 0;
      var irishHours = now.getUTCHours() + irishOffset;
      irishHours = irishHours >= 24 ? irishHours - 24 : irishHours;
      currentTime = irishHours * 60 + now.getUTCMinutes();
    }

    // Determine season and get timing
    var isIrishSummerTime = dateUtils.isIrelandDST(now);
    var seasonKey = isIrishSummerTime ? "summer" : "winter";
    var timing = announcement.seasonalTiming[seasonKey];

    if (!timing) {
      return false;
    }

    // Get prayer time references
    var startTime = this.getPrayerTimeMinutes(timing.startReference);
    var endTime =
      this.getPrayerTimeMinutes(timing.endReference) + (timing.endOffset || 0);

    return currentTime >= startTime && currentTime <= endTime;
  },

  // Get prayer time in minutes from prayer time reference
  getPrayerTimeMinutes: function (reference) {
    var selectorMap = {
      fajrBeginning: selectors.prayerTimes.fajrBeginning,
      zohrBeginning: selectors.prayerTimes.zohrBeginning,
      asrBeginning: selectors.prayerTimes.asrBeginning,
      magribBeginning: selectors.prayerTimes.magribBeginning,
      ishaBeginning: selectors.prayerTimes.ishaBeginning,
      fajrJamaah: selectors.prayerTimes.fajrJamaah,
      zohrJamaah: selectors.prayerTimes.zohrJamaah,
      asrJamaah: selectors.prayerTimes.asrJamaah,
      magribJamaah: selectors.prayerTimes.magribJamaah,
      ishaJamaah: selectors.prayerTimes.ishaJamaah,
    };

    var selector = selectorMap[reference];
    if (!selector) {
      return 0;
    }

    var element = document.querySelector(selector);
    if (!element) {
      return 0;
    }

    var timeStr = element.getAttribute("data-time");
    return timeUtils.timeToMinutes(timeStr);
  },

  // Create sequential display schedule for multiple image announcements
  createImageRotationSchedule: function (imageAnnouncements) {
    var schedule = [];
    var isSpecial = false;
    var maxFrequency = 0;
    var gapBetweenImages = 40; // Default 20 seconds gap between images

    // Build sequential schedule from all active announcements
    for (var i = 0; i < imageAnnouncements.length; i++) {
      var announcement = imageAnnouncements[i];
      if (announcement.images && announcement.images.length > 0) {
        var frequency = announcement.displayCondition.frequency || 1;
        var duration = announcement.displayCondition.duration || 10;
        var announcementGap = announcement.displayCondition.gapBetweenImages;
        
        // Use the gap from first announcement that specifies it, or default
        if (announcementGap !== undefined && schedule.length === 0) {
          gapBetweenImages = announcementGap;
        }
        
        // Track maximum frequency to determine cycle wait time
        if (frequency > maxFrequency) {
          maxFrequency = frequency;
        }
        
        // Add each image from this announcement to the sequential schedule
        for (var j = 0; j < announcement.images.length; j++) {
          schedule.push({
            imagePath: announcement.images[j],
            frequency: frequency,
            duration: duration,
            avoidJamaahTime: announcement.displayCondition.avoidJamaahTime !== false,
            announcementId: announcement.id
          });
        }
      }
      if (announcement.isSpecial) {
        isSpecial = true;
      }
    }

    // Calculate total cycle time: sum of all durations + gaps + max frequency wait
    var gapDuration = gapBetweenImages;
    var totalActiveDuration = 0;
    for (var k = 0; k < schedule.length; k++) {
      totalActiveDuration += schedule[k].duration;
    }
    var totalGapTime = (schedule.length - 1) * gapDuration; // gaps between images
    var totalActiveTime = totalActiveDuration + totalGapTime;
    var cycleWaitTime = maxFrequency * 60; // Convert max frequency (minutes) to seconds
    var totalCycleTime = totalActiveTime + cycleWaitTime;
    
    return {
      isImage: true,
      images: schedule.map(function(item) { return item.imagePath; }), // For compatibility
      displayCondition: { // For compatibility
        frequency: maxFrequency,
        duration: schedule.length > 0 ? schedule[0].duration : 10,
        avoidJamaahTime: schedule.length > 0 ? schedule[0].avoidJamaahTime : true
      },
      schedule: schedule,
      isSpecial: isSpecial,
      maxFrequency: maxFrequency,
      gapDuration: gapDuration,
      totalActiveTime: totalActiveTime,
      totalCycleTime: totalCycleTime
    };
  },

  // Update the announcement message based on current time and special events
  updateAnnouncement: function () {
    console.log("DEBUG: updateAnnouncement called");
    var now = testMode.enabled ? testMode.getMockDate() : new Date(); // Get current time in minutes from midnight
    var currentTime;
    if (testMode.enabled) {
      // In test mode, use progressing test time
      currentTime = testMode.getCurrentTimeMinutes();
    } else {
      // Normal mode: apply Irish time offset
      var isIrishSummerTime = dateUtils.isIrelandDST(now);
      var irishOffset = isIrishSummerTime ? 1 : 0;
      var irishHours = now.getUTCHours() + irishOffset;
      irishHours = irishHours >= 24 ? irishHours - 24 : irishHours;
      currentTime = irishHours * 60 + now.getUTCMinutes();
    }

    // For day-of-week, handle potential day rollover
    var currentDay = testMode.enabled ? testMode.dayOfWeek : now.getUTCDay();
    if (!testMode.enabled && irishHours < now.getUTCHours()) {
      currentDay = (currentDay + 1) % 7;
    }

    var dayOfWeek = currentDay; // 0 is Sunday, 5 is Friday, 6 is Saturday

    // Determine if it's summer or winter time
    var isIrishSummerTime = dateUtils.isIrelandDST(now);

    // Get prayer times
    var times = {
      sunrise: document
        .querySelector(selectors.importantTimes.sunrise)
        .getAttribute("data-time"),
      zawal: document
        .querySelector(selectors.importantTimes.zawal)
        .getAttribute("data-time"),
      fajrBeginning: document
        .querySelector(selectors.prayerTimes.fajrBeginning)
        .getAttribute("data-time"),
      zohrBeginning: document
        .querySelector(selectors.prayerTimes.zohrBeginning)
        .getAttribute("data-time"),
      magribBeginning: document
        .querySelector(selectors.prayerTimes.magribBeginning)
        .getAttribute("data-time"),
      fajrJamaah: document
        .querySelector(selectors.prayerTimes.fajrJamaah)
        .getAttribute("data-time"),
      zohrJamaah: document
        .querySelector(selectors.prayerTimes.zohrJamaah)
        .getAttribute("data-time"),
      asrJamaah: document
        .querySelector(selectors.prayerTimes.asrJamaah)
        .getAttribute("data-time"),
      magribJamaah: document
        .querySelector(selectors.prayerTimes.magribJamaah)
        .getAttribute("data-time"),
      ishaJamaah: document
        .querySelector(selectors.prayerTimes.ishaJamaah)
        .getAttribute("data-time"),
    };

    // Convert times
    var sunriseTime = timeUtils.timeToMinutes(times.sunrise);
    var zawalTime = timeUtils.timeToMinutes(times.zawal);
    var fajrTime = timeUtils.timeToMinutes(times.fajrBeginning);
    var zohrTime = timeUtils.timeToMinutes(times.zohrBeginning);
    var magribTime = timeUtils.timeToMinutes(times.magribBeginning);
    var fajrJamaahTime = timeUtils.timeToMinutes(times.fajrJamaah);
    var zohrJamaahTime = timeUtils.timeToMinutes(times.zohrJamaah);
    var asrJamaahTime = timeUtils.timeToMinutes(times.asrJamaah);
    var magribJamaahTime = timeUtils.timeToMinutes(times.magribJamaah);
    var ishaJamaahTime = timeUtils.timeToMinutes(times.ishaJamaah);

    var announcementElement = document.querySelector(selectors.announcement);
    var message = announcements.default;
    var isWarning = false;
    var isSpecialAnnouncement = false;
    var imageData = null;

    // Check if we should display Adhkar poster - THIS TAKES ABSOLUTE PRIORITY
    var adhkarPosterCheck = this.checkAdhkarPoster(currentTime, dayOfWeek, isIrishSummerTime, {
      fajrJamaah: fajrJamaahTime,
      zohrJamaah: zohrJamaahTime,
      asrJamaah: asrJamaahTime,
      magribJamaah: magribJamaahTime,
      ishaJamaah: ishaJamaahTime
    });
    
    if (adhkarPosterCheck.shouldDisplay) {
      console.log("DEBUG: Adhkar poster should display - superseding all other announcements");
      // Build schedule from settings so durations reflect mosque configuration
      var _adhkarCfg = (window.appSettings || DEFAULT_SETTINGS).adhkar;
      var _p1secs  = _adhkarCfg.poster1Seconds       || 90;
      var _winsecs = (_adhkarCfg.displayWindowMinutes || 3) * 60;
      var _p2secs  = Math.max(1, _winsecs - _p1secs);
      // Display Adhkar poster ONLY - skip all other announcements during this time
      imageData = {
        images: ['/static/images/Adhkar1.jpg', '/static/images/Adhkar2.jpg'],
        displayCondition: {
          frequency: 1,
          duration: _winsecs,
          avoidJamaahTime: false
        },
        isSpecial: true,
        isAdhkarPoster: true,  // Special flag to bypass cycle rotation logic
        adhkarStartSeconds: adhkarPosterCheck.adhkarStartSeconds,
        schedule: [
          {
            imagePath: '/static/images/Adhkar1.jpg',
            frequency: 1,
            duration: _p1secs,
            avoidJamaahTime: false,
            announcementId: 'adhkar_poster_1'
          },
          {
            imagePath: '/static/images/Adhkar2.jpg',
            frequency: 1,
            duration: _p2secs,
            avoidJamaahTime: false,
            announcementId: 'adhkar_poster_2'
          }
        ],
        gapDuration: 0,
        totalActiveTime: _winsecs,
        totalCycleTime: _winsecs  // No gap for Adhkar
      };
      
      // Display the Adhkar poster and skip all other processing
      this.handleImageAnnouncement(imageData, currentTime, [
        fajrJamaahTime,
        zohrJamaahTime,
        asrJamaahTime,
        magribJamaahTime,
        ishaJamaahTime,
      ]);
      
      // Update text announcement to default
      announcementElement.textContent = message;
      announcementElement.className = "";
      return; // Exit early - don't process any other announcements
    }

    // Check for any dynamic announcements (only if Adhkar is not active)
    var activeDynamicAnnouncement = this.getActiveDynamicAnnouncement(now);
    console.log("DEBUG: Active dynamic announcement:", activeDynamicAnnouncement);
    if (activeDynamicAnnouncement) {
      // Handle text announcement
      if (activeDynamicAnnouncement.textAnnouncement) {
        message =
          activeDynamicAnnouncement.textAnnouncement.message ||
          announcements.default;
        isSpecialAnnouncement =
          activeDynamicAnnouncement.textAnnouncement.isSpecial;
      }

      // Handle image announcement separately (can exist alongside text)
      if (activeDynamicAnnouncement.imageAnnouncement) {
        console.log("DEBUG: Found imageAnnouncement:", activeDynamicAnnouncement.imageAnnouncement);
        imageData = {
          images: activeDynamicAnnouncement.imageAnnouncement.images,
          displayCondition:
            activeDynamicAnnouncement.imageAnnouncement.displayCondition,
          isSpecial: activeDynamicAnnouncement.imageAnnouncement.isSpecial,
          schedule: activeDynamicAnnouncement.imageAnnouncement.schedule,
          gapDuration: activeDynamicAnnouncement.imageAnnouncement.gapDuration,
          totalActiveTime: activeDynamicAnnouncement.imageAnnouncement.totalActiveTime,
          totalCycleTime: activeDynamicAnnouncement.imageAnnouncement.totalCycleTime,
        };
        console.log("DEBUG: Created imageData with schedule:", imageData.schedule ? imageData.schedule.length : 'undefined', "items");
      }
    }
    // If no dynamic announcement, use standard recurring announcements
    else {
      // Regular announcements logic
      if (isIrishSummerTime) {
        if (!this.isControlHidden("thursday_darood_control") &&
          dayOfWeek === 4 &&
          currentTime >= fajrTime &&
          currentTime < magribJamaahTime + 5
        ) {
          // Thursday
          message = announcements.thursday_darood();
        }
        else if (!this.isControlHidden("friday_tafseer_control") && dayOfWeek === 4 && currentTime >= magribJamaahTime + 6 && currentTime < (23 * 60 + 59)) {
          // Thursday After Magrib
          message = announcements.friday_tafseer();
        }
        else if (!this.isControlHidden("friday_tafseer_control") && dayOfWeek === 5 && currentTime > (0 * 60 + 1) && currentTime < magribJamaahTime + 10) {
          // Friday
          message = announcements.friday_tafseer();
        }
      } else {
        // Winter time rules
        if (!this.isControlHidden("thursday_darood_control") &&
          dayOfWeek === 4 &&
          currentTime >= fajrTime &&
          currentTime < ishaJamaahTime + 5
        ) {
          // Thursday
          message = announcements.thursday_darood();
        } 
        else if (!this.isControlHidden("friday_tafseer_control") &&
          dayOfWeek === 4 &&
          currentTime >= ishaJamaahTime + 6 &&
          currentTime < 23 * 60 + 59
        ) {
          // Thursday After Isha
          message = announcements.friday_tafseer();
        } else if (!this.isControlHidden("friday_tafseer_control") &&
          dayOfWeek === 5 &&
          currentTime > 0 * 60 + 1 &&
          currentTime < ishaJamaahTime + 10
        ) {
          // Friday
          message = announcements.friday_tafseer();
        }
      }
    }

    // Then check for warnings (which take precedence over any other messages)
    if (currentTime >= sunriseTime && currentTime < sunriseTime + 15) {
      message = announcements.warnings.sunrise(
        times.sunrise,
        timeUtils.addMinutes(times.sunrise, 15)
      );
      isWarning = true;
      isSpecialAnnouncement = false;
    } else if (currentTime >= zawalTime && currentTime < zawalTime + 10) {
      message = announcements.warnings.zawal(times.zawal, times.zohrBeginning);
      isWarning = true;
      isSpecialAnnouncement = false;
    } else if (currentTime >= magribTime - 10 && currentTime < magribTime) {
      message = announcements.warnings.sunset(times.magribBeginning);
      isWarning = true;
      isSpecialAnnouncement = false;
    }

    if (announcementElement) {
      // First update the text announcement
      announcementElement.textContent = message;

      // Remove all classes first
      announcementElement.classList.remove(
        "announcement-text-normal",
        "announcement-text-long",
        "announcement-text-very-long"
      );
      announcementElement.classList.remove(
        "announcement-warning",
        "special-announcement"
      );
      document
        .querySelector(".announcement")
        .classList.remove("warning-active", "special-active");

      // Add appropriate animation class based on message length
      if (message.length < 60) {
        announcementElement.classList.add("announcement-text-normal");
      } else if (message.length < 100) {
        announcementElement.classList.add("announcement-text-long");
      } else {
        announcementElement.classList.add("announcement-text-very-long");
      }

      // Add styling classes (warning takes priority)
      if (isWarning) {
        announcementElement.classList.add("announcement-warning");
        document.querySelector(".announcement").classList.add("warning-active");
      } else if (isSpecialAnnouncement) {
        announcementElement.classList.add("special-announcement");
        document.querySelector(".announcement").classList.add("special-active");
      }

      // Process image announcement separately - even if there's a text announcement
      console.log("DEBUG: Image processing decision - imageData exists:", !!imageData, "isWarning:", isWarning);
      
      // Check if slideshow is already active to prevent constant recreation
      var existingSlideshow = document.querySelector(".image-slideshow-container");
      if (existingSlideshow) {
        console.log("DEBUG: Slideshow already active, skipping image processing to prevent blinking");
      } else if (imageData && !isWarning) {
        console.log("DEBUG: Calling handleImageAnnouncement with schedule:", imageData.schedule ? imageData.schedule.length : 'undefined');
        this.handleImageAnnouncement(imageData, currentTime, [
          fajrJamaahTime,
          zohrJamaahTime,
          asrJamaahTime,
          magribJamaahTime,
          ishaJamaahTime,
        ]);
      } else if (imageData && isWarning) {
        console.log("DEBUG: Image announcement blocked by warning");
      } else if (!imageData) {
        console.log("DEBUG: No image data found");
      }
    }

    // Safety check: Ensure prayer-times and important-times are visible when nothing is active
    this.ensureElementsVisible();
  },

  // Ensure prayer-times and important-times are visible when no overlays are active
  ensureElementsVisible: function () {
    console.log("DEBUG: ensureElementsVisible called - checking for active overlays");
    
    // Check if any image slideshow is active
    var activeSlideshow = document.querySelector(".image-slideshow-container");
    if (activeSlideshow) {
      console.log("DEBUG: Image slideshow is active, elements should be hidden");
      return; // Image is showing, elements should be hidden
    }

    // No overlays active - ensure clean state and both elements visible
    console.log("DEBUG: No active overlays found, ensuring elements are visible");
    
    // Double-check that prayer elements are actually visible
    var prayerTimesElement = document.querySelector(".prayer-times");
    var importantTimesElement = document.querySelector(".important-times");
    
    var prayerVisible = prayerTimesElement && window.getComputedStyle(prayerTimesElement).display !== 'none';
    var importantVisible = importantTimesElement && window.getComputedStyle(importantTimesElement).display !== 'none';
    
    if (!prayerVisible || !importantVisible) {
      console.log("DEBUG: Prayer elements not visible, forcing cleanup", "prayer:", prayerVisible, "important:", importantVisible);
      this.cleanupAllPosterElements();
    }
  },

  // Helper function to hide both prayer-times and important-times together
  hidePrayerElements: function() {
    var prayerTimesElement = document.querySelector(".prayer-times");
    var importantTimesElement = document.querySelector(".important-times");
    
    if (prayerTimesElement) {
      prayerTimesElement.style.display = "none";
      prayerTimesElement.style.zIndex = "1";
    }
    if (importantTimesElement) {
      importantTimesElement.style.display = "none";
      importantTimesElement.style.zIndex = "1";
    }
  },

  // Helper function to show both prayer-times and important-times together
  showPrayerElements: function() {
    console.log("DEBUG: Showing prayer elements");
    var prayerTimesElement = document.querySelector(".prayer-times");
    var importantTimesElement = document.querySelector(".important-times");
    
    if (prayerTimesElement) {
      var prayerWasHidden = prayerTimesElement.style.display === "none";
      if (prayerWasHidden) {
        prayerTimesElement.style.removeProperty('display');
        console.log("DEBUG: Restored prayer-times visibility");
      }
      prayerTimesElement.style.zIndex = "1";
    } else {
      console.warn("WARNING: prayer-times element not found");
    }
    
    if (importantTimesElement) {
      var importantWasHidden = importantTimesElement.style.display === "none";
      if (importantWasHidden) {
        importantTimesElement.style.removeProperty('display');
        console.log("DEBUG: Restored important-times visibility");
      }
      importantTimesElement.style.zIndex = "1";
    } else {
      console.warn("WARNING: important-times element not found");
    }
  },

  // Comprehensive cleanup function to remove ALL poster elements
  // Helper function to fade out an element and then remove it
  fadeOutAndRemove: function(element, callback) {
    if (!element || !element.parentNode) {
      if (callback) callback();
      return;
    }

    // Set transition if not already set
    var currentTransition = element.style.transition;
    if (!currentTransition || currentTransition.indexOf('opacity') === -1) {
      element.style.transition = 'opacity 0.5s ease-in-out';
    }

    // Fade out
    element.style.opacity = '0';

    // Remove after transition completes
    setTimeout(function() {
      if (element && element.parentNode) {
        element.parentNode.removeChild(element);
      }
      if (callback) callback();
    }, 500); // Match the transition duration
  },

  cleanupAllPosterElements: function(callback, skipShowPrayerElements) {
    console.log("DEBUG: Starting comprehensive cleanup of all poster elements");
    
    // Remove all possible poster container types
    var containerSelectors = [
      '.image-slideshow-container',
      '.tafseer-display-container',
      '[id^="single-image-"]',
      '[id^="slideshow-"]',
      '[class*="image-container"]',
      '[class*="poster"]'
    ];

    var elements = [];
    containerSelectors.forEach(function(selector) {
      var found = document.querySelectorAll(selector);
      found.forEach(function(element) {
        if (element && element.parentNode) {
          elements.push({element: element, selector: selector});
        }
      });
    });

    // Also collect stray image elements that might have high z-index
    var allImages = document.querySelectorAll('img[style*="z-index"]');
    allImages.forEach(function(img) {
      var zIndex = parseInt(window.getComputedStyle(img).zIndex);
      if (zIndex > 100) { // Remove images with high z-index that might be poster remnants
        if (img.parentNode) {
          elements.push({element: img, selector: 'high-z-index-img'});
        }
      }
    });

    if (elements.length === 0) {
      console.log("DEBUG: Cleanup complete, no elements to remove");
      if (!skipShowPrayerElements) { this.showPrayerElements(); }
      if (callback) callback();
      return;
    }

    console.log("DEBUG: Found", elements.length, "elements to fade out and remove");
    
    var self = this;
    var removedCount = 0;
    var totalElements = elements.length;

    // Fade out all elements
    elements.forEach(function(item) {
      self.fadeOutAndRemove(item.element, function() {
        removedCount++;
        console.log("DEBUG: Removed container:", item.selector, item.element.id || item.element.className);
        
        // After all elements are removed
        if (removedCount === totalElements) {
          console.log("DEBUG: Cleanup complete, removed", removedCount, "elements");
          if (!skipShowPrayerElements) { self.showPrayerElements(); }
          if (callback) callback();
        }
      });
    });
  },


  // Display the Tafseer image for Friday
  displayTafseerImage: function (durationSeconds) {
    // Get both the prayer-times and important-times elements that we'll hide
    var prayerTimesElement = document.querySelector(".prayer-times");
    var importantTimesElement = document.querySelector(".important-times");

    // Save original state of prayer-times
    var originalPrayerTimesState = null;
    if (prayerTimesElement) {
      originalPrayerTimesState = {
        display: prayerTimesElement.style.display,
        html: prayerTimesElement.innerHTML,
        className: prayerTimesElement.className,
      };
    }

    // Save original state of important-times
    var originalImportantTimesState = null;
    if (importantTimesElement) {
      originalImportantTimesState = {
        display: importantTimesElement.style.display,
        html: importantTimesElement.innerHTML,
        className: importantTimesElement.className,
      };
    }

    // Hide both elements together using helper function
    this.hidePrayerElements();

    // Create tafseer container
    var tafseerContainer = document.createElement("div");
    tafseerContainer.className = "tafseer-container image-slideshow-container";
    tafseerContainer.style.width = "100%";
    tafseerContainer.style.height = "132vh"; // Set container height to 60% of viewport height
    tafseerContainer.style.display = "flex";
    tafseerContainer.style.justifyContent = "center";
    tafseerContainer.style.alignItems = "center";
    tafseerContainer.style.marginTop = "0"; // Reduced margin to give more space for image
    tafseerContainer.style.padding = "0"; // Remove padding to maximize space

    // Insert the tafseer container where prayer-times would normally be
    if (prayerTimesElement && prayerTimesElement.parentNode) {
      prayerTimesElement.parentNode.insertBefore(
        tafseerContainer,
        prayerTimesElement
      );
    } else {
      // Fallback: add after date-container's divider
      var dateContainer = document.querySelector(".date-container");
      var insertAfterElement = dateContainer
        ? dateContainer.nextElementSibling
        : document.body;
      if (insertAfterElement) {
        insertAfterElement.parentNode.insertBefore(
          tafseerContainer,
          insertAfterElement.nextSibling
        );
      } else {
        document.body.appendChild(tafseerContainer);
      }
    }

    // Create the image element
    var imgElement = document.createElement("img");
    imgElement.src = "/static/images/Tafseer of the Quran.jpg";
    imgElement.style.maxWidth = "100%"; // Increased from 90%
    imgElement.style.maxHeight = "100%"; // Added maxHeight to fill container height
    imgElement.style.height = "auto";
    imgElement.style.width = "auto";
    imgElement.style.objectFit = "contain"; // Ensure image maintains aspect ratio while filling space
    imgElement.style.transition = "opacity 0.5s ease-in-out";
    imgElement.style.opacity = "0";
    imgElement.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)"; // Add subtle shadow for better visibility

    // Add the image to container
    tafseerContainer.appendChild(imgElement);

    // Fade in the image
    setTimeout(function () {
      imgElement.style.opacity = "1";
    }, 100);

    // Set up cleanup and resumption of original content
    displayState.resumeTimeout = setTimeout(function () {
      // Fade out and remove tafseer container
      fadeOutAndRemove(tafseerContainer, function() {
        // Restore prayer-times element
        if (prayerTimesElement && originalPrayerTimesState) {
          prayerTimesElement.className = originalPrayerTimesState.className || "";
        }

        // Restore important-times element
        if (importantTimesElement && originalImportantTimesState) {
          importantTimesElement.className =
            originalImportantTimesState.className || "";
        }

        // Comprehensive cleanup to ensure no poster remnants
        announcementModule.cleanupAllPosterElements();
      });
    }, durationSeconds * 1000);


  },

  // Handle sequential image announcements with gaps and cycle timing
  handleImageAnnouncement: function (imageData, currentTime, jamaahTimes) {
    // Special handling for Adhkar poster - bypass all cycle logic
    if (imageData.isAdhkarPoster) {
      console.log("DEBUG ADHKAR: Displaying Adhkar poster immediately - bypassing cycle logic");
      var now = new Date();
      var currentTotalSeconds = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
      var elapsedSeconds = currentTotalSeconds - (imageData.adhkarStartSeconds || 0);
      var _adhkarCfgH = (window.appSettings || DEFAULT_SETTINGS).adhkar;
      var _p1secs  = _adhkarCfgH.poster1Seconds       || 90;
      var _winsecs = (_adhkarCfgH.displayWindowMinutes || 3) * 60;
      var adhkarImage, remaining;
      if (elapsedSeconds < _p1secs) {
        adhkarImage = imageData.schedule[0];
        remaining   = _p1secs - elapsedSeconds;
      } else {
        adhkarImage = imageData.schedule[1];
        remaining   = _winsecs - elapsedSeconds;
      }
      remaining = Math.max(1, remaining);
      console.log("DEBUG ADHKAR: elapsedSeconds:", elapsedSeconds, "remaining:", remaining, "- showing:", adhkarImage.imagePath);
      this.displaySingleImage(
        adhkarImage.imagePath,
        remaining,
        adhkarImage.announcementId,
        imageData.isSpecial || false
      );
      return;
    }

    // Check if we have a rotation schedule
    console.log("DEBUG: Checking schedule - exists:", !!imageData.schedule, "isArray:", Array.isArray(imageData.schedule), "length:", imageData.schedule ? imageData.schedule.length : 'N/A');
    if (!imageData.schedule || !Array.isArray(imageData.schedule) || imageData.schedule.length === 0) {
      console.log("DEBUG: Exiting - invalid schedule");
      return;
    }

    // Check if any images should avoid jamaah time
    var shouldAvoidJamaah = false;
    for (var i = 0; i < imageData.schedule.length; i++) {
      if (imageData.schedule[i].avoidJamaahTime) {
        shouldAvoidJamaah = true;
        break;
      }
    }
    console.log("DEBUG: shouldAvoidJamaah:", shouldAvoidJamaah, "currentTime:", currentTime);

    // Check if we're within 2 minutes of any jamaah time
    if (shouldAvoidJamaah && jamaahTimes) {
      console.log("DEBUG: Checking jamaah times proximity - jamaahTimes:", jamaahTimes);
      for (var j = 0; j < jamaahTimes.length; j++) {
        var jamaahTime = jamaahTimes[j];
        var timeDiff = Math.abs(currentTime - jamaahTime);
        console.log("DEBUG: Jamaah", j, "time:", jamaahTime, "diff:", timeDiff);
        if (jamaahTime && !isNaN(jamaahTime) && timeDiff <= 2) {
          console.log("DEBUG: Exiting - too close to jamaah time", jamaahTime);
          return; // Too close to jamaah time, don't show any images
        }
      }
    }

    var now = new Date();
    var totalSeconds = (now.getHours() * 3600) + (now.getMinutes() * 60) + now.getSeconds();
    var cyclePosition = totalSeconds % imageData.totalCycleTime;

    console.log("DEBUG: Cycle calculation - totalSeconds:", totalSeconds, "totalCycleTime:", imageData.totalCycleTime, "cyclePosition:", cyclePosition, "totalActiveTime:", imageData.totalActiveTime);

    // Check if we're in the active display period or the wait period
    if (cyclePosition >= imageData.totalActiveTime) {
      // We're in the wait period (no posters should be displayed)
      console.log("DEBUG: In wait period - no posters displayed");
      return;
    }

    // We're in the active period - determine which image to show
    console.log("DEBUG: In active period - determining which image to show");
    var currentPosition = 0;
    var gapDuration = imageData.gapDuration;

    for (var k = 0; k < imageData.schedule.length; k++) {
      var scheduleItem = imageData.schedule[k];
      var itemDuration = scheduleItem.duration;

      console.log("DEBUG: Checking schedule item", k, "- imagePath:", scheduleItem.imagePath, "duration:", itemDuration, "currentPosition:", currentPosition, "cyclePosition:", cyclePosition);

      // Check if we're in this item's display window
      if (cyclePosition >= currentPosition && cyclePosition < (currentPosition + itemDuration)) {
        var remainingTime = (currentPosition + itemDuration) - cyclePosition;
        console.log("DEBUG: Showing image:", scheduleItem.imagePath, "for", remainingTime, "seconds (position", cyclePosition, "of", imageData.totalCycleTime, ")");
        this.displaySingleImage(scheduleItem.imagePath, remainingTime);
        return;
      }

      // Move to next position (item duration + gap)
      currentPosition += itemDuration;
      console.log("DEBUG: After item", k, "currentPosition now:", currentPosition);
      
      // Add gap time if not the last item
      if (k < imageData.schedule.length - 1) {
        // Check if we're in the gap period after this item
        console.log("DEBUG: Checking gap after item", k, "- gap start:", currentPosition, "gap end:", currentPosition + gapDuration);
        if (cyclePosition >= currentPosition && cyclePosition < (currentPosition + gapDuration)) {
          console.log("DEBUG: In gap period after", scheduleItem.imagePath);
          return; // In gap, don't show anything
        }
        currentPosition += gapDuration;
        console.log("DEBUG: After gap", k, "currentPosition now:", currentPosition);
      }
    }
  },

  // Display a single image for a specified duration
  displaySingleImage: function (imagePath, duration) {
    console.log("DEBUG: displaySingleImage called for:", imagePath, "duration:", duration);
    
    // Check if there's already a slideshow running with the same image
    var existingSlideshow = document.querySelector(
      ".image-slideshow-container"
    );
    if (existingSlideshow) {
      var existingImg = existingSlideshow.querySelector('img');
      var currentImageName = imagePath.split('/').pop();
      var existingImageName = existingImg ? existingImg.src.split('/').pop() : '';
      
      console.log("DEBUG: Comparing images - current:", currentImageName, "existing:", existingImageName);
      
      if (existingImg && existingImageName === currentImageName) {
        console.log("DEBUG: Same image already displaying, skipping recreation");
        return;
      } else {
        console.log("DEBUG: Different image requested, replacing existing slideshow");
        // Clean up existing slideshow first - skip showPrayerElements since we're immediately replacing
        this.cleanupAllPosterElements(null, true);
      }
    } else {
      console.log("DEBUG: No existing slideshow, creating new one");
      // Clean up any existing poster elements first to ensure clean state
      this.cleanupAllPosterElements(null, true);
    }

    // Create ID for this slideshow session to avoid conflicts
    var slideshowId = "slideshow-" + new Date().getTime();

    // Get the prayer-times and important-times elements that we'll hide
    var prayerTimesElement = document.querySelector(".prayer-times");
    var importantTimesElement = document.querySelector(".important-times");

    // Save original state of prayer-times
    var originalPrayerTimesState = null;
    if (prayerTimesElement) {
      originalPrayerTimesState = {
        display: prayerTimesElement.style.display,
        html: prayerTimesElement.innerHTML,
        className: prayerTimesElement.className,
      };
    }

    // Save original state of important-times
    var originalImportantTimesState = null;
    if (importantTimesElement) {
      originalImportantTimesState = {
        display: importantTimesElement.style.display,
        html: importantTimesElement.innerHTML,
        className: importantTimesElement.className,
      };
    }

    // Hide both elements together using helper function
    this.hidePrayerElements();

    // Create image container that will be placed in the same location as prayer-times
    var imageContainer = document.createElement("div");
    imageContainer.id = slideshowId;
    imageContainer.className = "image-slideshow-container";
    imageContainer.style.width = "100%";
    imageContainer.style.height = "132vh";
    imageContainer.style.display = "flex";
    imageContainer.style.justifyContent = "center";
    imageContainer.style.alignItems = "center";
    imageContainer.style.marginTop = "1.0vw";
    imageContainer.style.padding = "0";
    // Keep poster at normal z-index to prevent layering issues
    imageContainer.style.position = "relative";
    imageContainer.style.zIndex = "1";
    imageContainer.style.backgroundColor = "transparent";

    // Insert the image container where prayer-times would normally be
    if (prayerTimesElement && prayerTimesElement.parentNode) {
      prayerTimesElement.parentNode.insertBefore(
        imageContainer,
        prayerTimesElement
      );
    } else {
      // Fallback: add after date-container's divider
      var dateContainer = document.querySelector(".date-container");
      var insertAfterElement = dateContainer
        ? dateContainer.nextElementSibling
        : document.body;
      if (insertAfterElement) {
        insertAfterElement.parentNode.insertBefore(
          imageContainer,
          insertAfterElement.nextSibling
        );
      } else {
        document.body.appendChild(imageContainer);
      }
    }

    // Create the image element
    var imgElement = document.createElement("img");
    imgElement.src = imagePath;
    imgElement.style.maxWidth = "100%";
    imgElement.style.maxHeight = "100%";
    imgElement.style.height = "auto";
    imgElement.style.width = "auto";
    imgElement.style.objectFit = "contain";
    imgElement.style.transition = "opacity 0.5s ease-in-out";
    imgElement.style.opacity = "0";
    imgElement.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";

    // Add the image to container
    imageContainer.appendChild(imgElement);

    // Fade in the image
    setTimeout(function () {
      imgElement.style.opacity = "1";
    }, 100);

    // Function to clean up slideshow and restore original elements
    var cleanupSlideshow = function () {
      console.log("DEBUG: Cleaning up slideshow for image:", imagePath);
      
      try {
        // Fade out and remove the slideshow container
        announcementModule.fadeOutAndRemove(imageContainer, function() {
          console.log("DEBUG: Removed slideshow container with fade-out");
          
          // Restore the prayer-times element
          if (prayerTimesElement && originalPrayerTimesState) {
            prayerTimesElement.innerHTML = originalPrayerTimesState.html;
            prayerTimesElement.className = originalPrayerTimesState.className;
            console.log("DEBUG: Restored prayer-times element");
          }

          // Restore the important-times element
          if (importantTimesElement && originalImportantTimesState) {
            importantTimesElement.innerHTML = originalImportantTimesState.html;
            importantTimesElement.className = originalImportantTimesState.className;
            console.log("DEBUG: Restored important-times element");
          }

          // Comprehensive cleanup to ensure no poster remnants
          announcementModule.cleanupAllPosterElements();
          
          console.log("DEBUG: Slideshow cleanup completed successfully");
        });
      } catch (error) {
        console.error("ERROR: Exception during slideshow cleanup:", error);
        // Force cleanup even if there's an error
        announcementModule.cleanupAllPosterElements();
      }
    };

    // Set up cleanup after the specified duration
    setTimeout(cleanupSlideshow, duration * 1000);
  },

  // Display rotating images with proper timing
  displayRotatingImages: function (images, duration) {
    // Removed the announcementElement parameter since we're not modifying it
    if (!images || images.length === 0) return;

    // Create ID for this slideshow session to avoid conflicts
    var slideshowId = "slideshow-" + new Date().getTime();

    // Check if there's already a slideshow running
    var existingSlideshow = document.querySelector(
      ".image-slideshow-container"
    );
    if (existingSlideshow) {
      // Already displaying images, don't start another slideshow
      return;
    }

    // Get the prayer-times and important-times elements that we'll hide
    var prayerTimesElement = document.querySelector(".prayer-times");
    var importantTimesElement = document.querySelector(".important-times");

    // Save original state of prayer-times
    var originalPrayerTimesState = null;
    if (prayerTimesElement) {
      originalPrayerTimesState = {
        display: prayerTimesElement.style.display,
        html: prayerTimesElement.innerHTML,
        className: prayerTimesElement.className,
      };

      // Hide the prayer-times element
      prayerTimesElement.style.display = "none";
    }

    // Save original state of important-times
    var originalImportantTimesState = null;
    if (importantTimesElement) {
      originalImportantTimesState = {
        display: importantTimesElement.style.display,
        html: importantTimesElement.innerHTML,
        className: importantTimesElement.className,
      };

      // Hide the important-times element
      importantTimesElement.style.display = "none";
    }

    // Store the original states in window for later retrieval
    window[slideshowId] = {
      prayerTimesState: originalPrayerTimesState,
      prayerTimesElement: prayerTimesElement,
      importantTimesState: originalImportantTimesState,
      importantTimesElement: importantTimesElement,
    };

    // Create image container that will be placed in the same location as prayer-times
    var imageContainer = document.createElement("div");
    imageContainer.id = slideshowId;
    imageContainer.className = "image-slideshow-container";
    imageContainer.style.width = "100%";
    imageContainer.style.textAlign = "center";
    imageContainer.style.marginTop = "2.0vw";
    imageContainer.style.padding = "0.5vw";

    // Insert the image container where prayer-times would normally be
    if (prayerTimesElement && prayerTimesElement.parentNode) {
      prayerTimesElement.parentNode.insertBefore(
        imageContainer,
        prayerTimesElement
      );
    } else {
      // Fallback: add after date-container's divider
      var dateContainer = document.querySelector(".date-container");
      var insertAfterElement = dateContainer
        ? dateContainer.nextElementSibling
        : document.body;
      if (insertAfterElement) {
        insertAfterElement.parentNode.insertBefore(
          imageContainer,
          insertAfterElement.nextSibling
        );
      } else {
        document.body.appendChild(imageContainer);
      }
    }

    // Create the image element with simple fade transition
    var imgElement = document.createElement("img");
    imgElement.style.maxWidth = "90%";
    imgElement.style.height = "auto";
    imgElement.style.transition = "opacity 0.5s ease-in-out";
    imgElement.style.opacity = "1";

    // Add the image to container
    imageContainer.appendChild(imgElement);

    var currentIndex = 0;
    // Function to show the next image with simple fade transition
    var showNextImage = function () {
      // Check if we've reached the end of the duration
      var currentTime = new Date().getTime();
      if (currentTime >= startTime + duration * 1000) {
        // Duration is over, clean up and restore original content
        cleanupSlideshow(slideshowId);
        return;
      }

      // Cycle through images
      if (currentIndex >= images.length) {
        currentIndex = 0; // Reset to start for continuous rotation
      }

      // Load the next image
      imgElement.style.opacity = "0";

      setTimeout(function () {
        // Set new image source
        imgElement.src = images[currentIndex];

        // When image loads, fade it in
        imgElement.onload = function () {
          imgElement.style.opacity = "1";
        };

        // Handle image load error
        imgElement.onerror = function () {
          console.error("Failed to load image:", images[currentIndex]);
          currentIndex++;
          setTimeout(showNextImage, 100); // Try next image quickly
        };

        // Increment index for next round
        currentIndex++;

        // Set timer for next image (show each image for a portion of the total duration)
        var imageDisplayTime = Math.max(
          2,
          (duration * 1000) / (images.length * 2)
        ); // At least 2 seconds per image
        setTimeout(showNextImage, imageDisplayTime);
      }, 500); // Brief fade-out transition
    };
    // Store the start time for duration checking
    var startTime = new Date().getTime();

    // Function to clean up slideshow and restore original elements
    var cleanupSlideshow = function (id) {
      // Fade out and remove the slideshow container
      var container = document.getElementById(id);
      if (container) {
        fadeOutAndRemove(container, function() {
          // Restore the prayer-times and important-times elements
          var savedState = window[id];
          if (savedState) {
            // Restore prayer-times
            if (savedState.prayerTimesElement && savedState.prayerTimesState) {
              var el = savedState.prayerTimesElement;
              var state = savedState.prayerTimesState;

              // Remove inline display style to let CSS rules take over
              el.style.removeProperty('display');
              el.className = state.className || "";
            }

            // Restore important-times
            if (
              savedState.importantTimesElement &&
              savedState.importantTimesState
            ) {
              var el = savedState.importantTimesElement;
              var state = savedState.importantTimesState;

              // Remove inline display style to let CSS rules take over
              el.style.removeProperty('display');
              el.className = state.className || "";
            }
          }

          // Clean up saved state
          delete window[id];
        }); // End fadeOutAndRemove callback
      } // End if (container)
    }; // End cleanupSlideshow
    // Start the slideshow
    imgElement.onload = function () {
      imgElement.style.opacity = "1";
      currentIndex++;
      // Calculate time per image (show each image for a portion of the total duration)
      var imageDisplayTime = Math.max(
        2000,
        (duration * 1000) / (images.length * 2)
      ); // At least 2 seconds per image
      setTimeout(showNextImage, imageDisplayTime);
    };
    // Set the first image
    imgElement.src = images[0];

    // Safety timeout to ensure cleanup happens
    setTimeout(function () {
      cleanupSlideshow(slideshowId);
    }, duration * 1000 + 1000); // Add 1 second buffer
  },

  // Show next message in the queue with scrolling effect
  showNextMessage: function (message) {
    var announcementElement = document.querySelector(selectors.announcement);
    if (!announcementElement) return;

    // Set the message
    announcementElement.textContent = message;

    // Add class for older browsers
    if (announcementElement.classList) {
      announcementElement.classList.add("scroll-announcement");
    } else {
      // Fallback for older browsers without classList
      announcementElement.className += " scroll-announcement";
    }
    isScrolling = true;

    // Wait for animation to complete
    setTimeout(function () {
      // Remove class for older browsers
      if (announcementElement.classList) {
        announcementElement.classList.remove("scroll-announcement");
      } else {
        // Fallback for older browsers
        announcementElement.className = announcementElement.className.replace(
          /\bscroll-announcement\b/,
          ""
        );
      }
      isScrolling = false;

      // Small delay before next message
      setTimeout(function () {
        if (messageQueue && messageQueue.length > 0) {
          showNextMessage(messageQueue.shift());
        }
      }, 3000);
    }, 25000);
  },

  // Check if Adhkar poster should be displayed
  checkAdhkarPoster: function(currentTime, dayOfWeek, isIrishSummerTime, jamaahTimes) {
    console.log("DEBUG ADHKAR: Checking Adhkar poster - currentTime:", currentTime, "dayOfWeek:", dayOfWeek, "jamaahTimes:", jamaahTimes);
    var result = { shouldDisplay: false };
    
    // For Friday Zohr: display at specific times
    var _adhkarCfg = (window.appSettings || DEFAULT_SETTINGS).adhkar;
    if (dayOfWeek === 5) { // Friday
      var fridayZohrTime = isIrishSummerTime
        ? timeUtils.timeToMinutes(_adhkarCfg.fridayZohrSummer || '14:10')
        : timeUtils.timeToMinutes(_adhkarCfg.fridayZohrWinter || '13:42');
      var fridayZohrEndTime = fridayZohrTime + 3; // Display for 3 minutes
      
      console.log("DEBUG ADHKAR: Friday check - fridayZohrTime:", fridayZohrTime, "fridayZohrEndTime:", fridayZohrEndTime);
      if (currentTime >= fridayZohrTime && currentTime < fridayZohrEndTime) {
        console.log("DEBUG ADHKAR: ✓ Friday Adhkar should display!");
        result.shouldDisplay = true;
        result.adhkarStartSeconds = fridayZohrTime * 60;
        return result;
      }
    }
    
    // For other prayers: display Jamaah + N minutes
    var adhkarDelay    = _adhkarCfg.delayAfterJamaah      || 8;
    var adhkarDuration = _adhkarCfg.displayWindowMinutes  || 3;
    
    var jamaahList = [
      { name: 'fajrJamaah', time: jamaahTimes.fajrJamaah, excludeFriday: false },
      { name: 'zohrJamaah', time: jamaahTimes.zohrJamaah, excludeFriday: true }, // Excluded on Friday
      { name: 'asrJamaah', time: jamaahTimes.asrJamaah, excludeFriday: false },
      { name: 'magribJamaah', time: jamaahTimes.magribJamaah, excludeFriday: false },
      { name: 'ishaJamaah', time: jamaahTimes.ishaJamaah, excludeFriday: false }
    ];
    
    for (var i = 0; i < jamaahList.length; i++) {
      var jamaah = jamaahList[i];
      
      // Skip Friday Zohr (already handled above)
      if (dayOfWeek === 5 && jamaah.excludeFriday) {
        continue;
      }
      
      if (jamaah.time && !isNaN(jamaah.time)) {
        var adhkarStartTime = jamaah.time + adhkarDelay;
        var adhkarEndTime = adhkarStartTime + adhkarDuration;
        
        console.log("DEBUG ADHKAR: Checking", jamaah.name, "- jamaahTime:", jamaah.time, "adhkarWindow:", adhkarStartTime, "-", adhkarEndTime);
        if (currentTime >= adhkarStartTime && currentTime < adhkarEndTime) {
          console.log("DEBUG ADHKAR: ✓ Adhkar should display for", jamaah.name, "!");
          result.shouldDisplay = true;
          result.adhkarStartSeconds = adhkarStartTime * 60;
          return result;
        }
      }
    }
    
    console.log("DEBUG ADHKAR: No Adhkar time matched - returning false");
    return result;
  }
};

// Initialize announcements when the DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  announcementModule.init();
  
  // Set up periodic cleanup to prevent ghost poster elements
  setInterval(function() {
    var now = new Date();
    console.log("DEBUG: Periodic cleanup check at", now.toLocaleTimeString());
    
    // Check for active display elements
    var activeSlideshow = document.querySelector(".image-slideshow-container");
    var activeTafseer = document.querySelector(".tafseer-display-container");
    var allActiveElements = [activeSlideshow, activeTafseer].filter(Boolean);
    
    console.log("DEBUG: Found", allActiveElements.length, "active poster elements");
    
    if (allActiveElements.length === 0) {
      // Check if prayer elements are visible, if not, there might be ghost elements
      var prayerTimesElement = document.querySelector(".prayer-times");
      var importantTimesElement = document.querySelector(".important-times");
      
      if (prayerTimesElement && importantTimesElement) {
        var prayerVisible = window.getComputedStyle(prayerTimesElement).display !== 'none';
        var importantVisible = window.getComputedStyle(importantTimesElement).display !== 'none';
        
        console.log("DEBUG: Prayer visible:", prayerVisible, "Important visible:", importantVisible);
        
        // If both should be visible but aren't, run cleanup
        if (!prayerVisible || !importantVisible) {
          console.log("WARNING: Prayer elements hidden but no active posters found - running cleanup");
          announcementModule.cleanupAllPosterElements();
        }
      } else {
        console.warn("WARNING: Could not find prayer-times or important-times elements");
      }
    } else {
      // Active elements found - check if they're stale (older than 5 minutes)
      allActiveElements.forEach(function(element, index) {
        if (element.id && element.id.startsWith('slideshow-')) {
          var timestamp = parseInt(element.id.split('-')[1]);
          var elementAge = now.getTime() - timestamp;
          if (elementAge > 5 * 60 * 1000) { // 5 minutes
            console.log("WARNING: Found stale slideshow element (age:", Math.round(elementAge/1000), "seconds) - cleaning up");
            announcementModule.cleanupAllPosterElements();
          }
        }
      });
    }
  }, 5000); // Check every 5 seconds (increased frequency)
});
