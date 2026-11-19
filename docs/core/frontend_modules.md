# Frontend modules

TODO: go over entire document, and see compatibility with design refactoring

## Authentication

- Authenticating should open a WebSocket to the server. WebSocket should not be closed when navigating between pages. WebSocket should only be closed when logging out, tab with active WebSocket connection was closed, or WebSocket connection has timed out (checked on server-side).

TODO: WebSocket connection timeout

## Dashboard

### Current user widget

- Current user first name and last name
- Get/set status
- Currently associated desk name
- Check-in/check-out button

Settings:
- Set new password

TODO: handling to user service changing status automatically
TODO: multiple client devices/instances connected as the same user

### Current desk widget

- Get/set desk manual desk height
- Get current desk profile
- Get/set pending desk profile

### Desk profile widget

### Healthy habits widget

Settings:
- Get/set sitting duration
- Get/set standing duration
- Get/set sitting desk profile
- Get/set standing desk profile
- Get/set is automatic
- Get/set automatic warning duration

- Get current timer start and end timestamps
- Get current timer paused
- Set current timer user paused

- Receive automatic warning notification
- TODO: Cancel button in automatic warning notification and in standing timer widget
- Receive manual move notification
- Receive automatically moving notification (after automatic warning)

## Statistics page (TODO: DESIGN)

- Available to everyone, including users

- Time graph for desk height for a particular user
    - Time period selection: today, yesterday, this week, last week, customly selected day range using calendar widget
    - Show graph values only if the user had desk session at that time
    - TODO: colored graph, areas, summary aggregate statistics
    - TODO: choosing different users. selecting multiple users is not supported

TODO: more graphs
TODO: desk api statistics
TODO: pico statistics

## Desk issues page

- Available to everyone, including users

TODO: creation of issues for users, resolving their own issues

TODO: admin editing or resolving any issues

- Show a list of current desk issues
    - Show columns: is resolved, created timestamp, severity, desk ID, reporter first name and last name (or none if null), error code, title and description
        - Each column can be toggled on/off
        - TODO: does the client receive all the data, paging
    - Enable/disable is resolved filtering 
    - Search issues by title, description, error code, reporter, 
        - TODO: how searching works?

- TODO: refreshing the list

## Admin interface

### Users tab

- Show list component of all users
    - Show columns: ID, first name, last name, email, role, user card ID
    - Copy user ID
    - Create user: first name, last name, email, role, password, user card ID
    - Edit user: first name, last name, email, role, password, user card ID
    - Delete user

### Desks tab

- Show list component of all desks
    - Show columns: ID, name, REST API URL, min height, max height, manually changed desk height, current desk profile ID, pending desk profile ID, is desk profile autocorrection enabled
    - Copy desk ID
    - Create desk: name, REST API URL, min height, max height
    - Edit desk: name, REST API URL, min height, max height
    - Delete desk

TODO: should it fetch min and max height from desk REST API?
TODO: handling updating properties for other services
TODO: does it make sense to change manually changed desk height, current desk profile ID, pending desk profile ID, and is desk profile autocorrection enabled
TODO: default category??

### Desk categories tab

- Show list component of desk categories
    - Show columns: ID, Name, Desk IDs, Default desk profile ID
    - Copy desk category ID
    - Create desk category: name

TODO: needs a dropdown for default desk profile ID
TODO: needs to handle if desks are removed or desk profile is removed
TODO: rendering desk IDs nicely in a list
TODO: also, it might just not fit well. but default desk profile ID makes sense

### Desk sessions tab

- Show list component of desk sessions
    - Show columns: 

### Shared tabs

Same tabs added to tab list:
- Office map
- Statistics page
- Issues page

## Office map

TODO: map panning, zooming, bounds
TODO: desk positions, rotation, adding, moving, deleting, associating IDs
TODO: updating map data live
TODO: show occupied desks and users who are using it
TODO: show information on click
TODO: environmental data heat map?

# Frontend components

List:
    - Paginated, ideally from server-side, with settable page size
    - Each column can be toggled on/off
    - Refreshed is called from component callee anytime user attempts any action, which should modify list state (e.g. create, update, delete actions)

TODO: list
TODO: more components