# Healthy habits system high-level design #9

### Module features

- Tracking Habits by desk height data over time
  - compare data every 5 seconds from freshly collected data.
  - compare data from previous to detect changes (to reset time in case of
    change by the user before reminders)
- Reminding user
  - Remind the user to stand if the user is sitting for too long.
  - Notification via a LED or Buzzer, App related push notification.
- Forcing stand-up instead of notification.
- Configuration via profiles
  - stand up Timer settings

### Module handling

- Error missing data / configurations.
- Debugging via PyTest for Backend.

### Use cases

- User login with his/her profile. The desk adjust to his/her profile and start
  tracking desk height.
- Reminds / force the user to stand if a timer runs out.

### Test cases

- Missing data (Backend/Database)
- Missing configuration (Backend/Database)
- Process Data correctly (Backend)
- Get reminded from timer (Backend)
- Notification call (Backend/Frontend)
- Force Standing (Backend/Embedded)

### Modules

- Health Process
- Notification event

### Other module dependencies

- Data ingestion
- Frontend system Notification
- Profile configuration
- Other Backend Modules
  - Conflict potential??
