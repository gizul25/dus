# Frontend modules

TODO: desk session config not exposed

## Authentication

- Authenticating should open a WebSocket to the server. WebSocket should not be closed when navigating between pages. WebSocket should only be closed when logging out, tab with active WebSocket connection was closed, or WebSocket connection has timed out (checked on server-side, I think it's already automatic with WebSockets).
- Multiple active devices/instances connected as the same user is possible, which is expected.
- Ideally, user data in all of the pages needs to be kept in sync as changes occur. Naïve approach would be to always poll the data or refresh the page to get fresh data, which we don't expect to be changed externally (e.g. without user action), and receive notifications with WebSockets for changes, which are important to retrieve in real time (e.g. notifications, health timers, office map changes). Probably due to time constraints, we will be going with this naïve approach. For example, when using lists, users are expected to refresh the page to receive new contents when user did not create/edit/delete list entries.
- More broadly, there might be cases when due to user or administrator changes, various IDs in data structures become invalid. It is more of a backend concern, but frontend and backend should not assume that returned IDs in data structures will always be valid. However, most of these IDs will be passed straight to backend, so it should be much of a worry for frontend.

## Dashboard

### Current user widget

- Current user first name and last name
- Get/set status
- Currently associated desk name
- Check-in/check-out button

Settings:
- Set new password

### Current desk widget

- Get/set desk manual desk height
- Get current desk profile
- Get/set pending desk profile

### Desk profile widget

- Show a list of user's desk profiles
    - Show columns: Name, desk height, enter desk profile threshold, exit desk profile threshold.
    TODO: decide if exposing thresholds is too much, and we should hide it under advanced options, and provide default values instead.
    - Create desk profile: Name, desk height, enter desk profile threshold, exit desk profile threshold.
    - Edit desk profile: Name, desk height, enter desk profile threshold, exit desk profile threshold.
    - Delete desk profile

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
- Cancel button in automatic warning notification and in standing timer widget
- Receive manual move notification
- Receive automatically moving notification (after automatic warning)

## Statistics page

- Available to everyone, including users

- For each graph, there is also a summary aggregate statistics displayed next to the graph. E.g., sum, average, min, max.

- Time-series graph component for desk height for a particular user
    - Show graph values only if the user had desk session at that time
    - The graph is colored in 2 areas. The top area "standing" zone has one background, and bottom area "sitting" zone has another background color. In the threshold height value, there is dotted line with opacity 0.5.
    Dropdown to choose different users. Selecting multiple users is not supported
    - In addition to other summary aggregate statistics, show total sitting and standing time
- Desk utilization graph (in hrs/day or hrs)
- Average temperature for all desks graph
- Average humidity for all desks graph
- Average light for all desks graph
- Amount of desk issues graph
- Desk speed for a particular desk graph
    - Dropdown to choose different users

## Desk issues page

- Available to everyone, including users

- Show a list of current desk issues
    - Show columns: is resolved, created timestamp, severity, desk ID, reporter first name and last name (or none if null), error code, title and description
        - Each column can be toggled on/off
    - Enable/disable is resolved filtering 
    - Search issues by title, description, error code, reporter, 
        - Searching works in a similar way like GitHub, but simplified: `title:abc` would search for abc in title field, `first_name:leon` would case-insensitively search for first name to contain leon. Multiple filters, e.g. `title:abc title:def`, would be treated as AND operator. String escaping, e.g. `title:"Some \"text\""` is allowed, but might be tricky to implement correctly. Time queries, e.g. `created_at` or `resolved_at` are left non-queryable due to query string representation complexity for now.
- Create desk issues
    - Opens a popup with dropdown for desk, and fields for title and description. Any issues created this way automatically have `user-reported` severity assigned to them.
- Viewing desk issues
    - Clicking on a row will open a popup with desk name, severity, error code, title, description fields shown.
- Editing desk issues
    - Shows a same popup as viewing desk issues, except fields are editable. It also includes a button to mark issue as resolved. It is only possible if the user is authorized to edit, which is permitted to reporter, and to administrators.

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

Currently, administrator has to enter desk name, min height and max height, meanwhile they are technically accessible from REST API URL.
Any added desk does not automatically move on its own, because "is desk profile autocorrection enabled" is set to false. This allows the administrator, for instance, to set default category to a desk before desk is controlled.
TODO: does it make sense to change manually changed desk height, current desk profile ID, pending desk profile ID, and is desk profile autocorrection enabled

### Desk categories tab

- Show list component of desk categories
    - Show columns: ID, Name, Desk IDs, Default desk profile ID
    - Copy desk category ID
    - Create desk category: name, Desk IDs, Default desk profile ID
    - Edit desk category: name, Desk IDs, Default desk profile ID
    - Delete desk category

UI will not be the best looking one, as it will have a desk ID array inside a list row. Furthermore, it contains a lot of IDs. We could hide details of IDs, and always show to user desk names and desk profile names. When creating and editing, there would be dropdowns with desk names and desk profile names, not ID field.

### Desk sessions tab

- Show list component of desk sessions
    - Show columns: ID, User ID, Desk ID, Start timestamp, Finished timestamp, finished reason
    - List is purely read-only, and even admin should not modify or delete desk sessions

### Shared tabs

Same tabs added to tab list:
- Office map
- Statistics page
- Issues page

## Office map

3 different map modes:
- Standard mode
- Heatmap mode
- Desk layout editor mode (only for admins)

Camera:
- In any mode, camera can pan and zoom, and has bounds based on map dimensions

Map contains several layers. Layers can be different floors of an office building, could be different rooms/areas. Layers are ordered by admins, always displayed on the screen, and clicking switches between them. Map with one layer hides layer selection.

Standard mode:
- User/desk search
    - Dropdown to select what you are searching for - a desk or a user
    - Ideally, search should provide autocompletion, and clicking on a result should navigate to it
    - If there are no results, autocompletion should show no results found, and entering does nothing
- Current occupancy data
    - Show user names associated with desks
    - Show user statuses and color desks based on their status
    - Any desks with issues have their colour distinctly changed
- Click on desk information
    - Clicking on desk shows slightly detailed information: desk ID, desk name, user, user status, temperature, humidity, light
    TODO: should we add when session was started?
    - Ideally, in addition, small chart of temperature, humidity, light.
    - Report button for the desk. It redirects to desk issue page with preassigned desk ID

Heatmap mode:
- Meant to see current or historical desk data
- Time period selection, same as time-series graphs, except you can select to show current information
- Data types: occupancy (in hrs/day), temperature, humidity, light
- Each desk is coloured based on a value. There is a legend in one of the corners of the screen, and clicking on a desk shows precise value

Desk layout editor mode:
- Create, edit, rearrange, delete layers
- Define layer bounds
- Create rectangles ("desks"), move them, rotate them, delete them
- A panel which lists all rectangles in a layer, and their associations with desk IDs. There can be rectangles with no desk ID. Same desk ID can appear multiple times. However, we can highlight in red rectangles with no ID or duplicate IDs in rectangle panel.
- Assigning desk IDs is possible through rectangle panel. Perhaps through edit button, which opens a popup to select desk from a dropdown.

- Office map is one of the modules, which is crucial to update live with WebSockets connection

# Frontend components

List:
    - Paginated, ideally from server-side, with settable page size
    - Each column can be toggled on/off
    - Refreshed is called from component callee anytime user attempts any action, which should modify list state (e.g. create, update, delete actions)
Time-series graph:
    - Standard graph, but allows to select time period
    - Time period selection: today, yesterday, this week, last week, customly selected day range using calendar widget
Time period selector might be reusable between statistics and office map.

Standard elements, such as buttons, popups/dialogs, form elements, dropdowns, checkboxes, select boxes, tabs, textareas, toggle boxes.