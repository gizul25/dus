# Mobile app high-level design #5

# Module features

- All of the features as the web interface (due to nature of using web for UI)
  - Responsibility: Well, provide all the existing web interface features
    without introducing bugs. Mobile layout is already handled by existing web
    interface, as web page can be accessed through mobile web browser
- QR code scanner for check-in/check-out (might be integrated into web interface
  accessible through browser, turning into not mobile app exclusive)
  - Responsibility: Allow the user to be associated with the desk quickly by
    scanning QR code.
- NFC reader for check-in/check-out
  - Responsibility: Allow the user to be associated with the desk quickly by
    interacting with NFC reader (part of our Raspberry Pico, hopefully).

## Maybe?

- Notifications? Does any module need push notifications?
- NFC reading without app being open?
  - In that case, it would use Android NFC intents to launch an app with intent
    information, which would launch an NFC page immediately with popup to sign
    in (and optionally, don't ask me again).

# Module handling

Strange input values:

- The application UI will work without the internet, as the web interface will
  be SPA (single page application), meaning we will include entire frontend into
  the mobile app without making any server requests during runtime. The only
  server requests will be API requests.
  - Additional banner can be added which would show that there is no network
    connection (e.g. Youtube)
- QR code scanning will have separate page, so until the QR code scanning has
  completed, the page does not close. At any time, user can cancel QR code
  scanning by leaving the page. Any errors due to malformed QR code, no QR code
  will be displayed to the user as a popup. Multiple QR codes are handled by
  only using the first one, and no further detections should be done after the
  first QR code is detected, unless operation is cancelled. But then page is
  left, and state is reset, so no special handling in the code.

Logging:

- Any error popups and successful QR code scans will have logging sent to a
  central telemetry server based on user telemetry settings
- There can be debug mode enabled which would enable verbose logging into the
  web devtools.
- Any app-wide errors are catched by web interface already, so no additional
  logic there. Any Tauri or Tauri plugin errors will be visible in `adb logcat`,
  but it will not be sent to the server for telemetry, as most of the error
  logging is already covered by frontend.

Everything the same applies for NFC reading as for QR code. Separate page, error
popups, optional telemetry, interaction flow and so on.

Debugging:

- Really just verbose logs with developer mode (toggled in user settings).

Async requests:

- Handled by default by plugins. If not async, will have to rewrite to use
  async/await.

API:

- There will be QR and NFC plugins, which will expose JS API to use in the
  frontend code. The frontend will have a check if the plugins exist, and if
  they do, it will display additional pages for QR and NFC authentication.

So quite a bit of code will live in frontend, some in Android build itself (NFC
intents), some as Tauri plugins, and separate folder for Tauri app wrapping for
frontend and connecting Tauri plugins.

# Use cases

- User comes in and sees QR code. User opens app, navigates to *easily*
  accessible QR code page, scans QR code, and sees that it was successful.
- User comes in and sees NFC reader. User opens app, navigates to *easily*
  accessible NFC reader page, holds his phone to NFC reader, and sees that it
  was successful.
- User comes in and sees NFC reader. Holds his phone to NFC reader, app opens up
  with NFC page which displays approve sign in. Clicks okay, and then it goes
  successfully.

## Test cases

- Regular, standard, working QR code
- Distorted QR code
- Malformed QR code (invalid text)
- Correct QR code (structurally), invalid desk
- QR code scanned (due to in frame) while some popup is active

- NFC reader, all good, valid and working
- NFC reader, invalid desk

- Multiple QR codes in frame
- Multiple NFC readers in close proximity
- Another NFC reader scanned during NFC popup confirmation

- NFC supported but NFC not enabled on the phone
- QR code supported but camera is disabled on the phone

# Modules

- Tauri app
- NFC intent module
  - Web page intent receiver
- NFC reader Tauri plugin
  - NFC reader page
- QR code Tauri plugin
  - QR code page

<img width="852" height="509" alt="Image" src="https://github.com/user-attachments/assets/9403881b-b19d-4eac-ad54-380e3c86ce44" />

[Mobile_app_module_UML.drawio](https://github.com/user-attachments/files/32796594/Mobile_app_module_UML.drawio)

# Other module dependencies

- Check-in/check-out system
  - Will just pass desk ID to which the current user wants to log in, and it
    expects standard response as to other check-in/check-out module user
- Web interface
  - To add the pages, and to add intent handling redirection behaviour.

# External dependencies

- <https://tauri.app/>
- <https://v2.tauri.app/plugin/nfc/>
- <https://v2.tauri.app/plugin/barcode-scanner/> (despite the name, it handles
  QR codes)
- <https://v2.tauri.app/plugin/deep-linking/> (if we ever need deep links)
- <https://v2.tauri.app/plugin/notification/> (if we ever need native
  notifications)

# Missing pieces

- Where and when to ask for permissions for QR code and NFC. At app first
  launch, on first/any QR/NFC page navigation. For QR code, probably on any QR
  page navigation. For NFC especially, I'm not sure due to intent, and if it
  requires perms for that (most likely yes, as it would request nearby devices).
  Then probably could have popup on first launch, and any time in NFC page.
- Maybe Android intent receiver and NFC reader Tauri plugin could be merged.
  We'll see.
- What about having custom link handling so if user decices to scan the QR code
  with another QR scanning app, like their phone, it would still work. Would
  require handling deep links, and probably then would be great to show the user
  a popup if the link comes from another app, that they can use "better" and
  "easier" QR code scanning from the app.
