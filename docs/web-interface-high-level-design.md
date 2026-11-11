# Web interface high-level design #14

## FEATURES

Sign-in/Sign-out:

- log-in page
- log-out button
- display authentication errors
- confirmation for signing-out

Desk Control (Desk Control module) UI (so provide controllers for:)

- raise desk
- lower desk
- move to sitting height
- move to standing height
- move to default profile
- move to custom profile
- display current desk height

Profile Management:

- display all profiles
- edit profiles (see profile management module)
- display desk profile data
- save profile changes

Desk/Worker Status Management:

- display employee status
- edit employee status:
- avaliable
- occupied
- away
- do not disturb?
- save employee status

Issure Reporting (reporting module)

- display report form
- submit report
- MAYBE: see previous reports? show some kind of status?

Health (health module)

- configure sit/stand reminders
- enable/disable reminders
- enable/disable automatic desk movements
- display reminder settings
- display timer (it will be running in the background, right?)

Admin Interface:

- add account
- delete/archive account
- edit account
- form with UID, email, password, full name

Main:

- display current desk
- display session status (signed in, checked in)
- display user status
- display notifications for health timers, soon expiring session
- display errors
- display loading indicators (ex. loading map, desk in movement?)

USE CASES Open web application. Enter email. Enter password. Submit.
Authentication error or sucess. Main page displayed.

- correct credentials
- wrong password
- wrong email
- empty fields

Open profile list. View profiles. Click edit profile. Write new standing height.
Save profile. Click profile to set height.

- no desk assigned
- height out of range
- correct height
- many many profiles
- desk offline
- repeated clicking

Open reporting page. Provide description. Submit report. Confirmation shown.

- empty
- too long (probably display word limit)

Click logout. Confirmation with information that user will be checked-out and if
they want to logout. Press yes. Logout and checkout successful.

## HANDLING

- disabling buttons on forms if not valid
- display errors
- retrying

Async: disable buttons, show loading indicators

## COMPONENTS?

- Login Page
- Main Page
- Map Page
- Profiles Page (/section)
- Reporting Page (or popup)
- Health Page (/section)
- Admin Page for Account Management
- Admin Page for Statistics
- Admin Page for Viewing Logs
