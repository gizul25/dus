# Reminder System Design #76

#### Purpose and Scope
- Purpose is so that the user can adjust the reminder of the the sit and stand up timer for their preferences
- It will consist of multiple functions like LED light switching on and off, a buzzer sound activation and a notification system
- The system will store the preferences in a MongoDB database which will introduce persistence to the the reminder system
- For it to function it will need the Sitting/Standing Tracking system as a dependency since it is responsible for the timer and trigger for the reminder

#### User Preferences
- The user can adjust the way they can be reminded - whether they want only one of the the functions to be active or all
- If a user hasn't set any of the reminder systems then even when the timer runs out it will not output any notification to the user
- The settings themselves should apply immediately   as the user saves the preferences into the database
- The user has to stop reminders either manually or by adjusting the desk's height

#### Reminder Logic
- The system should receive a signal from the tracking system when the time limit is reached
- If no reminder methods are enabled, the system should not react to the timer running out, thus stopping the activation of the reminders
- The system receives the user's saved preferences from a MongoDB database to determine which preferences need to be active
- The system's code should be able to make a connection with the embedded elements of the desk as to successfully start the reminder - LED lights/Buzzer
- The system should be able to connect to the frontend elements of the interface as to display the notification

#### Reminder Lifecycle
- The Reminder System becomes active once the time limit the has been set in the tracking system has reached its limit
- Once the countdown has finished the Reminder system sends a reminder notification(interface, LED or buzzer) to the user to remind them to stand up
- The user has to stop the notification and to decide whether to apply to the request or not
- The Reminder system is stopped when the tracking system "sees" that the desk height has been adjusted
- (If there were adjustments) After the desk height has been returned to "sitting" height, the tracking system detects it and restarts the countdown again

#### Optional Forced Standing Logic
- An optional feature that user can turn on and off
- If enabled when the timer runs out the interface locks out the user until they have adjusted their desk
- Unlike the ordinary preferences the user cannot turn off the reminder manually
- Once the tracking system detects a change in the desk height, the countdown starts again
- If disabled the system continues like usually
