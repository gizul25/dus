# Check-in/check-out system high-level design #13

Module responsible for:

- authentication
- desk assignment
- session management
- occupancy status

## Features

### User Web Authentication

**Purpose**: identifying the user in the web application

- user logins with work email and password
- user stays logged in (no daily login, usually same laptop, kinda annoying)
- cookies or JWT handling

### Desk Check-In

**Purpose**: associating the user with a specific desk

- Main: tap RFID reader with a card to occupy desk
- Secondary: QR with mobile scanning (could have a simple sticker, could display QR on the little screen when something pressed)

### Desk Check-Out

**Purpose**: removing association between the user and a desk

- Main: tap RFID again to check-out
- Second: check-out button on web app
- Backup: automatic timeout after X h

### Deck Occupancy Status

Purpose: tracking whether desk is available or occupied

- Tracking whether desk is available or occupied (user associated? LED on/off?)
- If available, any valid card can check-in
- If occupied, only the user check-in can tap and check-out, others are ignored (they can see the LED on/off to determine if no response was a faulty desk or is it occupied)

## Handling

- unknown card
- card removed during scan
- desk already occupied
- no desk in the system
^ probably some indicator with the LED, and then logs send and up for viewing in dev/maintenance/debug mode

- user checked into desk and tries on another desk
^ probably automatically move; helping coworkers maybe does not require the perfect height, because otherwise it can get complicated with automatic switch, checking-in at the main workstation again, returning to previous profile of the coworker, and etc.

- user by mistake taps the reader few times on check-in and accidentally checks-out
^ we probably need some lock on reader for some time after first read

## Flows

Two flows, and backend combines both user identity and desk assigment.

### Checking In/Out

Tap RFID card -> RFID reader reads UID > UID send to Pico -> Pico sends UID + DeskID to Backend -> Backend validates

#### Validation

User found?

- no -> error (logs/flashing LED?) -> reject
- yes -> continue

Desk occupied?

- no -> user already assigned?
 	- yes -> **move desks** (would be good to have some prompt to check if they are sure they want to change, but not sure how? Pico screen? web? mobile?)
 	- no -> **check-in**
- yes -> same user?
 	- yes -> **check-out**
 	- no -> reject (maybe LED flash to show error, logs send for dev/debug/maintenance mode)

#### Check-In (other modules doing some of the work)

- create session (UID, DeskID, SessionID, some time tracker for the inactive check-out)
- assign user to desk (or desk to user?)
- set desk occupied -> turn on the LED
- load profile -> move desk (probably sitting position as default)
- update map

#### Check-Out (other modules doing some of the work)

- remove desk assignment
- mark desk as available
- turn off the LED
- reset desk position to default (for easy cleaning, for neat looking office)
- close session
- update map

Triggered by:

- RFID tap by already checked-in user
- Check Out button on web app/mobile app
- Automatic timeout after x h of inactivity

#### Move Desks (other modules doing some of the work)

- check-out on first desk
- check-in on second desk
- would be good to have some prompt for the user to confirm

### Signing In/Out

Browser -> Web app

#### Signing-In

Already Signed-In?

- yes -> restore browser session
- no -> enter email and password -> valid credentials?
 	- no -> show error
 	- yes -> create browser session

*What if the user is signed-in, but not checked-in?*

- we could still allow them to access map, edit profile, and etc. without having desk specific actions (set height, check-out, standing/sitting)
- we could display something like "No desk assigned. Please check-in"
=> Some reminder to check-in, but have all the base functionality

#### Signing-Out

Active desk session?

- yes -> check out first (prompt to confirm maybe?)
- no -> delete web session

---------------

## Dependencies

### External

**RFID-RC522:**

- reading employee RFID cards
- obtaining card UID
**Raspberry Pi Pico W:**
- reading RFID cards
- controlling occupancy LED
- sending requests to backend
- communicating with desk hardware
**LED**:
- on = occupied
- off = available

Pico SDK (GPIOs, WIFI, RFID)
MFRC522 library (RFID): decode/encode incoming data from RFID module
SPI (RFID): helps establish the SPI communication
JWT Library (if we go with JWT)

### Internal

- authentication module (login and check-in)
- profile module (loading profiles on check-in)
- desk control module (moving desk on check-in/check-out)
- map module (updating occupancy)
-

*Why not NFC?*

- we need a tag on the desk, like a sticker or something
- issues with iPhones, issues with phones without NFC, issues with using the reader with NFC

*Should we use UID or employeeID on the card?*

- would be nice in case of replaced cards, since the UID would change
- plus cards could be reused, as they would only need to rewrite the employeeID for it to work for another user without deleting the previous user's profile
- admin/manager/someone in charge would have the possibility to write cards with new employeeID (some register card workflow)

*Healthy Habit*

- does it count time from check-in? what should give reminders then? does the desk move itself?
- does it count time from entering the web app? is it the web app that gives notification?
- probably start time of desk session would be the one determining when someone has to get up, but then what is reacting? the desk, the embedded parts, the web app?

## Useful Maybe?

- [[RC522 RFID Module Pinout, Interfacing with Arduino, Applications](https://microcontrollerslab.com/rc522-rfid-reader-pinout-arduino-interfacing-examples-features/)](<https://microcontrollerslab.com/rc522-rfid-reader-pinout-arduino-interfacing-examples-features/>)
- [[RC522 RFID Module Pinout, Features, Specs & How to Use It](https://components101.com/wireless/rc522-rfid-module)](<https://components101.com/wireless/rc522-rfid-module>)
- [[RC522 RFID Reader Module with Raspberry Pi Pico](https://microcontrollerslab.com/raspberry-pi-pico-rfid-rc522-micropython/)](<https://microcontrollerslab.com/raspberry-pi-pico-rfid-rc522-micropython/>)
