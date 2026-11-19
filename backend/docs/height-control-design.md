# Desk Height Control

* Pass the height measurements after the height has been changed (for any external module that would require it)
* Communicate directly with the desk board (i/o) in case of small adjustments on the user's side (use buttons instead of changing the profiles in the app)
* Send signal to the board on height change
* Get user's profile set and adjust the height based on one currently selected

## User input

* For each profile user should be able to precisely adjust the height of the desk (via slider) before applying said profile
* In case of small RT adjustments it should **only** be possible to make incremental changes(+/- buttons) either through physical control panel on the desk, or in the web interface 
* The profile and RT should not conflict, in case of profile being applied there should be a timeout during which the incremental option should be disabled on the web interface and physical control too, same for using the buttons before applying the profile

## Frontend 

* Current desk height should be displayed in components view 
* Current height should be possible to adjust through various controls (buttons for current, slider for profiles)


## Embedded

* For each desk the value of max/min possible height must be returned to prevent any illegal values (values _should be passed_ through the database to the backend and checked against model-specific data provided by the manufacturer, before it prompts the board to change height)
* The desk board shall receive a signal from the system on height change request and respond with either success code and current height, or an error code in case of any issues