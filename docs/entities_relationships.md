# Entities

TODO: message passing and events between modules

## User

### Data

- ID
- First name
- Last name
- Email
- Password
- Role: ['user', 'admin']
- Active desk session
- Status: ['available', 'busy', 'offline']
    - TODO: any more statuses?
- WebSocket connections

ID:
- Used for login purposes (not sure)
- Desk association

First name and last name used:
- Dashboard to show the logged in user
- Statistics page
- Map page to see who is associated with the desk

Email and password:
- Only used for logging in

Role:
- Admin role has access to admin login page, which has access to admin interface

### Actions

TODO: check if create/update should return ID or the whole struct. Another way could be that all actions have no return type, and what you would usually return, would be an event. I am not sure about tradeoffs of both of these approaches.

- Create user (data) -> ID
- Update user (ID, data)
- Delete user (ID)
- Login (ID)
- Logout (ID)
- Set new desk session (ID, desk session ID)
- Set status (ID, new status)
- Add WebSocket connection (ID, WebSocket connection)
- Remove WebSocket connection (ID, WebSocket connection)
- Send multicast WebSocket message (ID, message)

Set new desk session:
- Setting to null removes the session
Any errors are returned naturally, and are not specified in the return type.

TODO: missing check-in/check-out

### Events

- On logged in (ID)
- On logged out (ID)
- On desk session started (ID, desk session ID)
- On desk session ended (ID, desk session ID)
- On status changed (ID, old status, new status)
- On WebSocket connection added (ID, WebSocket connection)
- On WebSocket connection removed (ID, WebSocket connection)

## Desk

### Data

- ID
- Name
- Associated desk session
- Is Faulty
- Min height
- Max height
- Current height (can be null)
- Current desk profile (can be null) TODO: is it needed? but it's good if height drifts. But is it desired functionality? If the user used physical buttons, it would count it as drift and change it back to profile height.
- Profile autocorrection enabled

TODO: adjustments timeout (I forgot what I meant here)
TODO: Is Faulty should be connected to desk issue system
TODO: desk profile and autocorrection have no events or actions

ID:
- Receiving MQTT packets
- Desk association

### Actions

- Create desk (data) -> ID
- Update desk (ID, data)
- Delete desk (ID)
- Check-in (ID, user ID) -> desk session ID
- Check-out (ID, user ID)

- Request association with user. On success, creates new desk session.

### Events

- On desk updated (ID, old desk data, new desk data)
- On current height changed (ID, old height, new height)
- On desk session started (ID, desk session ID)
- On desk session ended (ID, desk session ID)
- On height changed (ID)
- On desk profile changed (ID)

On desk updated:
- Event is triggered when name, min or max height is changed.

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

### Events

- On automatic timeout notification timestamp (ID)
- On automatic timeout action timestamp (ID)

## Health reminder

### Data

- ID
- Desk session ID
- Next reminder timestamp
- Next desk profile
- Warning duration
- Is Automatic
    - If it is automatic, on "Next reminder timestamp" will show a notification, and after "Warning duration" it will switch to "Next desk profile"
    - If it is not, it will not switch to "Next desk profile"

TODO: Needs last acknowledged started profile in case health profiles change

Notification sending will take "Desk session ID", get "User ID", and send notification to all WebSocket connections.

### Events

- On next reminder timestamp (ID)
- On warning duration finished (ID)
- Is automatic changed (ID)

## Health reminder preferences

### Data

- ID
- User ID
- Sitting duration
- Sitting desk profile
- Standing duration
- Standing desk profile
- Warning duration
- Is Automatic

### Events

- On preferences changed (old preferences, new preferences)

On preferences changed:
- TODO: The event should have previous and new health reminder preferences, so the consumers of the event can see if they need to change anything regarding preference usage. However, it is problematic to send the data in an event. If we send 2 IDs, the old ID doesn't exist in the database and is overriden in place. Which leaves probably last option of sending entire data struct over event parameters.

## Desk Profile

### Data

- ID
- Name
- Desk height
- Enter desk profile threshold
- Exit desk profile threshold

Enter and exit desk profile thresholds are needed when the user is manually changing the desk height. It should detect that the desk has entered height range of a new desk profile. E.g., user has manually moved their desk from standing position to a sitting one. Different enter and exit thresholds are needed to prevent high fluctuation at the boundary of thresholds.
Automatic profile switching would also mean that overlap between desk heights is not expected or not even allowed.

TODO: needs something to use thresholds

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

## Desk API data

### Data

- ID
- Desk ID
- Timestamp
- [TODO: essentially entire dump of REST API access]

### Events

- On new desk API data (ID)

Same reasoning for events as for Pico environmental data.

## Desk issue

### Data

- ID
- Desk ID
- Reporter user ID
- Created timestamp
- Resolved timestamp
- Severity: ['info', 'warning', 'error', 'fatal']
- Error code
- Description

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

## Config

- Automatic desk association timeout

TODO: tracking in which profile desk sessions are in for analytical purposes
TODO: no events for config