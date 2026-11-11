# Module features

- Get the overview of all the desks with their respective status; i.e., normal/malfunctioning(if yes, display the error)
- Search for desks based on the name, associated user, or the specified error(better flexibility for troubleshooting in large workspaces)
- report malfunctions or collisions of each specific desk in real time(for each desk return the time since last error occurred)
- notify the user once the error has occurred

# Use cases

- User gets a notification in case of malfunction to inform them that there is a problem with their desk
- All desks can be monitored independently at any given moment(administration system)
- A view of all desks and their status can be displayed(map)

# Test cases

Negative:

- `404 Not Found` : Desk or category not found
- The desk is found, but no status is returned (ERR_NOSTATUS)

Positive:

- Shows the overview of the desks
- Displays the search query results based on the key prompt entered
- Reports current status of the specific desk based on the request

Edge Case:

- Multiple issues occuring at the same time(one error code overwrites previous without issue being solved)

# Modules

[DIRS.drawio](https://github.com/user-attachments/files/33003922/DIRS.drawio)

<img width="812" height="492" alt="Image" src="https://github.com/user-attachments/assets/991ee520-edb6-482d-90a4-ee1f91b14c1d" />

- Search module
- RT Reporting
- Overview
- Notification

# Dependencies

- Pico SDK
- Data ingestion(?)
