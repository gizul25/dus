# Entities

## User

### Data

- ID
- First name
- Last name
- Email
- Password
- Role: ['user', 'admin']
- Status: ['online', 'away', 'do not disturb', 'offline']
- User card ID

ID:
- Used for login purposes (not sure)
- Desk association
- Anywhere in backend

First name and last name used:
- Dashboard to show the logged in user
- Statistics page
- Map page to see who is associated with the desk

Email and password:
- Only used for logging in

Role:
- Admin role has access to admin dashboard page

Idea: for frontend, big banner for 'away' which prevents doing anything before changing status back to something else not 'away'.

### Actions

- Create user (data) -> ID
- Update user (ID, data)
- Delete user (ID)
- Login (ID)
- Logout (ID)
- Set status (ID, new status)

Update user is both for admin, which allows to change almost everything. If it is user who is changing, they are limited to email, password, and status.

### Events

- On user deleted (ID)
- On logged in (ID)
- On logged out (ID)
- On status changed (ID, old status, new status)

## WebSocket connection

### Data

- ID
- User ID

### Actions

- Add WebSocket connection (ID, user ID)
- Remove WebSocket connection (ID)
- Send multicast WebSocket message (ID, message)

### Events

- On WebSocket connection added (ID, WebSocket connection)
- On WebSocket connection removed (ID, WebSocket connection)

## Desk

### Data

- ID
- Name
- Min height
- Max height
- Manually changed desk height
- Current desk profile ID (can be null)
- Pending desk profile ID (can be null)
- Is desk profile autocorrection enabled

When manually changing desk height, if height exits current desk profile threshold, current desk profile is removed.

ID:
- Receiving MQTT packets
- Desk association

### Actions

- Create desk (data) -> ID
- Update desk (ID, data)
- Delete desk (ID)
- Set new desk profile (desk profile ID)
- Set desk profile autocorrection (ID, desk profile autocorrection enabled)

- Request association with user. On success, creates new desk session.
- On desk creation, default desk profile with height should be set in pending desk profile ID field.

### Events

- On desk updated (ID, old desk data, new desk data)
- On desk deleted (ID)
- On desk profile changed (ID)
- On desk profile target height reached (ID)

On desk updated:
- Event is triggered when name, min or max height is changed.

## Desk category

### Data

- ID
- Name
- Desk IDs
- Default desk profile ID

### Actions

TODO

### Events

TODO

## Desk session

### Data

- ID
- User ID
- Desk ID
- Start timestamp
- Finished timestamp
- Finished reason: ['timeout', 'checkout']
- Automatic timeout notification timestamp
- Automatic timeout action timestamp

### Actions

- Check-in (user ID, desk ID) -> desk session ID
- Check-out (ID)
- Check-out user (user ID)
- Check-out desk (desk ID)

### Events

- On desk session started (ID)
- On desk session ended (ID)
- On automatic timeout notification timestamp (ID)
- On automatic timeout action timestamp (ID)

## Health reminder

### Data

- ID
- Desk session ID
- Start timestamp
- Time elapsed before pause
- Is paused
- Next reminder timestamp
- Next desk profile
- Automatic warning duration
- Is Automatic
    - If it is automatic, on "Next reminder timestamp" will show a notification, and after "Automatic warning duration" it will switch to "Next desk profile"
    - If it is not, it will not switch to "Next desk profile"

Notification sending will take "Desk session ID", get "User ID", and send notification to all WebSocket connections.

"Time elapsed before pause" is stored when the health reminder is stopped. When it is resumed, it uses paused time elapsed to recalculate "Next reminder timestamp"

### Events

- On next reminder timestamp (ID)
- On warning duration finished (ID)
- Is automatic changed (ID)

## Health reminder preferences

### Data

- ID
- User ID
- Sitting duration
- Main sitting desk profile
- Standing duration
- Main standing desk profile
- Warning duration
- Is Automatic
- Middle desk height threshold (derived value from main sitting desk height and main standing desk height)

Detection if desk is in sitting or standing position is determined by "Middle desk height threshold".

Idea: for frontend, the desk height graph will have 2 areas. The top area "standing" zone has one background, and bottom area "sitting" zone has another background color. In the threshold height value, there is dotted line with opacity 0.5.

### Events

- On preferences changed (old preferences, new preferences)

## Desk Profile

### Data

- ID
- User ID
- Name
- Desk height
- Category: ['none', 'standing', 'sitting']
- Enter desk profile threshold
- Exit desk profile threshold

Enter and exit desk profile thresholds are needed when the user is manually changing the desk height. It should detect that the desk has entered height range of a new desk profile. E.g., user has manually moved their desk from standing position to a sitting one. Different enter and exit thresholds are needed to prevent high fluctuation at the boundary of thresholds.
Automatic profile switching would also mean that overlap between desk heights is not expected or not even allowed.

## Pico environmental data

### Data

- ID
- Desk ID
- Timestamp
- Temperature
- Humidity
- Light

Only used for analytics and map.

### Events

- On new environmental data (ID)

Pending new environmental data event was considered, which would be generated by MQTT packet handler to request addition to database. But it adds unnecessary overhead, as the module itself can add data to database, and then send notify event.

On new environmental data:
- This event is generated by the module, which handles MQTT packets from MQTT broker, after Pico environmental data was added to the database. This makes sure that ID is valid.

## Last desk fetch API

### Data

- Desk ID
- Desk last fetched error time (time_s for last error from desk)

## Realtime desk API data

### Data

- ID
- Desk ID
- Timestamp
- Desk height (LINAK calls it position)
- Speed

Polled every 5 seconds.
Speed is for hardware and issue diagnostics.
New errors are immediately added to desk issues.

### Events

- On new desk API data (ID)
- On desk height changed (ID, old height, new height)

Same reasoning for events as for Pico environmental data.

## Periodic desk API data

### Data

- Device name
- Manufacturer
- Status
- Is position lost
- Is overload protection up
- Is overload protection down
- Is anti collision

Polled every minute.

## Desk issue

### Data

- ID
- Desk ID
- Reporter user ID (can be null)
- Created timestamp
- Resolved timestamp
- Severity: ['info', 'warning', 'error', 'fatal', 'user-reported']
- Error code (can be null)
- Title (can be null)
- Description (can be null)

Reporter user ID is either the person who notified the issue, or *perhaps* the person who was working with the desk when the issue occured. This is to be able to ask for further information, and to notify them once the issue has been resolved. If issue occured when no one was using the desk, and the issue was reported by the system, there is no assigned reporter user ID.

### Events

- On desk issue created (ID)
- On desk issue resolved (ID)

## Frontend telemetry

### Data

- ID
- User agent
- Timestamp
- Error message
- Stack trace
- [TODO: anything more?]

- On frontend telemetry created (ID)

## AdminConfig

- Automatic desk association timeout

### Events

TODO