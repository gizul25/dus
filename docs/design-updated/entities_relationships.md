# Entities

- All of entities validate user IDs and other IDs, so that they are authorized to perform methods with these IDs. E.g., so that user cannot create/edit/delete health reminder preferences for another user.

## User

### Data

- ID
- First name
- Last name
- Email
- Password hash
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

- Get users (offset, limit) -> data
- Get user (ID) -> data
- Create user (data) -> ID
- Update user (ID, data)
- Delete user (ID)
- Login (ID)
- Logout (ID)
- Set status (ID, new status)
- Update password (ID, new password)

Update user is both for admin, which allows to change almost everything. If it is user who is changing, they are limited to password and status.

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

- Get WebSocket connection (ID) -> data
- Add WebSocket connection (ID, user ID)
- Remove WebSocket connection (ID)
- Send multicast WebSocket message (ID, message)

### Events

- On WebSocket connection added (ID, WebSocket connection)
- On WebSocket message received (ID, user ID, message)
- On WebSocket connection removed (ID, WebSocket connection)

## Desk

### Data

- ID
- Name
- REST API URL
- Min height (in mm)
- Max height (in mm)
- Manually changed desk height
- Current desk profile ID (can be null)
- Pending desk profile ID (can be null)
- Is desk profile autocorrection enabled

When manually changing desk height, if height exits current desk profile threshold, current desk profile is removed.

ID:
- Receiving MQTT packets
- Desk association

### Actions

- Get desks (offset, limit) -> data
- Get desk (ID) -> data
- Get full desk (ID) -> data
- Create desk (data) -> ID
- Update desk (ID, data)
- Delete desk (ID)
- Set manually changed desk height (ID, manually changed desk height)
- Set new desk profile (desk profile ID)
- Set desk profile autocorrection (ID, desk profile autocorrection enabled)

- Get desk returns data without REST API URL. Get full desk returns all data.
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

- Get desk categories (offset, limit) -> data
- Get desk category (ID) -> data
- Create desk category (data) -> ID
- Update desk category (ID, data)
- Delete desk category (ID)

### Events

- On desk category created (ID)
- On desk category updated (ID, old desk category, new desk category)
- On desk category deleted (ID)

## Desk session

### Data

- ID
- User ID
- Desk ID
- Started at timestamp
- Finished at timestamp
- Finished reason: ['timeout', 'checkout']
- Automatic timeout notification timer ID
- Automatic timeout action timer ID

At the end of desk session, ideally if there is no another desk session, it should clear any current or pending desk profiles for the desk, and it should reset back to desk category's default desk profile.

### Actions

- Get desk sessions (offset, limit) -> data
- Get desk session (ID) -> data
- Get user desk session (user ID) -> data
- Check-in (user ID, desk ID) -> desk session ID
- Check-out (ID)
- Check-out user (user ID)
- Check-out desk (desk ID)

### Events

- On desk session started (ID)
- On desk session ended (ID)
- On automatic timeout notification (ID)
- On automatic timeout action (ID)

## Desk session config

### Data

- Automatic desk association timeout duration

It is global config for all. There is only one entry, so ID is not needed.

### Actions

- Update config (new config)

### Events

- On config changed (old config, new config)

## Desk profile

### Data

- ID
- User ID
- Name
- Desk height (in mm)
- Enter desk profile threshold (in mm)
- Exit desk profile threshold (in mm)

Enter and exit desk profile thresholds are needed when the user is manually changing the desk height. It should detect that the desk has entered height range of a new desk profile. E.g., user has manually moved their desk from standing position to a sitting one. Different enter and exit thresholds are needed to prevent high fluctuation at the boundary of thresholds.
Automatic profile switching would also mean that overlap between desk heights is not expected or not even allowed.

### Actions

- Get user desk profiles (user ID, offset, limit) -> data
- Get desk profile (ID) -> data
- Create desk profile (data) -> ID
- Update desk profile (ID, data)
- Delete desk profile (ID)

### Events

- On desk profile created (ID)
- On desk profile updated (ID, old desk profile, new desk profile)
- On desk profile deleted (ID)

## Health reminder

### Data

- ID
- Desk session ID
- Started at timestamp
- Time elapsed before pause
- Is paused
- Is away paused
- Is user paused
- Next reminder timer ID
- Next desk profile ID
- Automatic warning timer ID
- Is Automatic
    - If it is automatic, on "Next reminder timer ID" will show a notification, and after "Automatic warning timer ID" it will switch to "Next desk profile"
    - If it is not, it will not switch to "Next desk profile"

Notification sending will take "Desk session ID", get "User ID", and send notification to all WebSocket connections.

"Time elapsed before pause" is stored when the health reminder is stopped. When it is resumed, it uses paused time elapsed to recalculate "Next reminder timer ID"

TODO: If during health reminder timer period, the user switches their desk from sitting to standing mode, and vice versa, should the timer reset?

### Actions

- Get health reminder (ID) -> data
- Get user health reminder (user ID) -> data
- Get desk session health reminder (desk session ID) -> data
- Set is user paused (ID, is user paused)
- Cancel health reminder (ID)

### Events

- On next reminder timer (ID)
- On warning duration finished (ID)
- On paused (ID)
- On health reminder cancelled (ID)
- Is automatic changed (ID)

## Health reminder preferences

### Data

- ID
- User ID
- Sitting duration
- Main sitting desk profile ID
- Standing duration
- Main standing desk profile ID
- Warning duration
- Is Automatic
- Middle desk height threshold (derived value from main sitting desk height and main standing desk height, in mm)

Detection if desk is in sitting or standing position is determined by "Middle desk height threshold".

### Actions

- Get health reminder preferences (ID) -> data
- Get user health reminder preferences (user ID) -> data
- Create health reminder preferences (data) -> ID
- Update health reminder preferences (ID, data)
- Delete health reminder preferences (ID)

### Events

- On health reminder preferences created (ID)
- On health reminder preferences updated (ID, old preferences, new preferences)
- On health reminder preferences deleted (ID)

## Desk issue

### Data

- ID
- Desk ID
- Reporter user ID (can be null)
- Created at timestamp
- Resolved at timestamp
- Severity: ['info', 'warning', 'error', 'fatal', 'user-reported']
- Error code (can be null)
- Title (can be null)
- Description (can be null)

Reporter user ID is either the person who notified the issue, or *perhaps* the person who was working with the desk when the issue occured. This is to be able to ask for further information, and to notify them once the issue has been resolved. If issue occured when no one was using the desk, and the issue was reported by the system, there is no assigned reporter user ID.

If there is a user, who is associated with the current desk, which received an error, they should get a notification. After the issue is resolved, reporter and/or current desk user should get a notification too.

### Actions

- Get desk issues (query, offset, limit) -> data
- Get desk issue (ID) -> data
- Create desk issue (data) -> ID
- Update desk issue (ID, data)
- Mark as resolved (ID)

No delete issue action is intentional, as issues should be resolved, not deleted.

### Events

- On desk issue created (ID)
- On desk issue updated (ID, old desk issue, new desk issue)
- On desk issue resolved (ID)

## Pico environmental data

### Data

- ID
- Desk ID
- Timestamp
- Temperature celsius
- Humidity
- Light

Only used for analytics and map.

### Actions

- Get desk latest temperature (desk ID) -> data
- Get desk latest humidity (desk ID) -> data
- Get desk latest light (desk ID) -> data

### Events

- On new environmental data (ID)

Pending new environmental data event was considered, which would be generated by MQTT packet handler to request addition to database. But it adds unnecessary overhead, as the module itself can add data to database, and then send notify event.

On new environmental data:
- This event is generated by the module, which handles MQTT packets from MQTT broker, after Pico environmental data was added to the database. This makes sure that ID is valid.

## Last desk API fetch

### Data

- ID
- Desk ID
- Next realtime desk fetch timer ID
- Next periodic desk fetch timer ID
- Desk last fetched error time (time_s for last error from desk)

## Realtime desk API data

### Data

- ID
- Desk ID
- Timestamp
- Desk height (LINAK calls it position, in mm)
- Speed (in mm/s)

Polled every 5 seconds.
Speed is for hardware and issue diagnostics.
New errors are immediately added to desk issues.

### Events

- On new desk API data (ID)
- On desk height changed (ID, old height, new height)

Same reasoning for events as for Pico environmental data.

## Periodic desk API data

### Data

- ID
- Desk ID
- Device name
- Manufacturer
- Status
- Is position lost
- Is overload protection up
- Is overload protection down
- Is anti collision

Polled every minute.

## Frontend telemetry

### Data

- ID
- Occured at timestamp
- Received at timestamp
- Error message
- Stack trace (can be null)
- Source
- URL
- User agent
- Context (can be null)
- Client host (can be null)
- Request ID (can be null)

### Events

- On frontend telemetry created (ID)

## Timer

### Data

- ID
- Trigger timestamp

### Actions

- Create timer (timestamp) -> ID
- Delete timer (ID)

### Events

- On timer triggered (ID)

## Statistics

TODO: Currently statistics data is underspecified

### Actions

- Get desk height (time period, user ID) -> data
- Get desk speed (time period, user ID) -> data
- Get desk utilization (time period, desk ID) -> data
- Get average temperature (time period) -> data
- Get average humidity (time period) -> data
- Get average light (time period) -> data
- Get desk issues (time period) -> data

### Events

Not required.

## Office map

### Data

- Layers
    - ID
    - Name
    - Bounds
    - Rectangles
        - ID
        - Position
        - Size
        - Rotation
        - Desk ID

### Actions

- Get layers (offset, limit) -> data
- Get layer (ID) -> data
- Create layer (data) -> ID
- Update layer (ID, data)
- Delete layer (ID)
- Search user (query) -> data
- Search desk (query) -> data
- Get occupancy data (layer ID, time period) -> data
- Get temperature data (layer ID, time period) -> data
- Get humidity data (layer ID, time period) -> data
- Get light data (layer ID, time period) -> data

For user and desk searching, limit is 5 and cannot be overridden.

### Events

- On layer created (ID)
- On layer metadata updated (ID, old layer metadata, new layer metadata)
- On layer deleted (ID)
- On rectangle created (ID)
- On rectangle updated (ID, old rectangle, new rectangle)
- On rectangle deleted (ID)

Any desk session and error changes should come from respective entities.

## Pico peripherals

### Data

TODO: underspecified. Only minor information for state tracking.