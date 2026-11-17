# Entities

## User

### Data

- ID
- First name
- Last name
- Email
- Password
- Role: ['user', 'admin']
- Active desk session
- Status: ['available', 'busy']
    - TODO: any more statuses?    

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

### Considerations

- Storing session data
- Active WebSocket connection. Would need to be an array for multiple devices


## Desk

### Data

- ID
- Name
- Associated user
- Is Faulty
- Current height (can be null)
- Current profile (can be null) TODO: is it needed? but it's good if height drifts. But is it desired functionality? If the user used physical buttons, it would count it as drift and change it back to profile height.
- Profile autocorrection enabled

TODO: adjustments timeout

ID:
- Receiving MQTT packets
- Desk association

## Desk session

### Data

- ID
- Start timestamp
- User ID
- Desk ID

TODO: associate with stuff, also handle health stuff

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

Notification sending will take "Desk session ID", get "User ID", and send notification to all WebSocket connections.

## Pico environmental data

### Data

- ID
- Desk ID
- Timestamp
- Temperature
- Humidity
- Light

Only used for analytics and map.

## Desk API data

### Data

- ID
- Desk ID
- Timestamp
- [TODO: essentially entire dump of REST API access]

## Frontend telemetry

### Data

- ID
- User agent
- Timestamp
- Error message
- Stack trace
- [TODO: anything more?]

## Config

- Automatic desk association timeout