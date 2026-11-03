# Height Control: embedded design #68

### Research
The LINAK Control Box provides access to desk height data through a REST API, which contains all the necessary information for monitoring desk height without interfering with motor control.

LINAK provides interfaces such as USB2LIN06 for compatible systems, but support for reading height data directly from a microcontroller must be confirmed for the specific Control Box model.

### Proposed embedded design

<img width="579" height="928" alt="Image" src="https://github.com/user-attachments/assets/6571c96a-573f-431c-8abc-5e19b3e80ae1" />

### How to obtain desk height data?
Read desk height directly from the LINAK Control Box through its REST API. The embedded controller retrieves the required data over Wi-Fi, using the supported API access. The LINAK Control Box remains responsible for motor control.

### Embedded software design
The embedded controller will:
- Read height: Retrieve desk height measurements through the LINAK REST API over Wi-Fi.
- Validate and filter: Ignore invalid readings and small fluctuations.
- Detect changes: Identify significant height changes.
- Add timestamps: Record when each measurement is taken.
- Send data: Transmit height measurements to the backend over Wi-Fi.

Example data:

{
  "deskId": "desk-001",
  "heightCm": 74.5,
  "timestamp": "2026-10-27T08:45:00Z"
}

The controller reads height periodically and reports communication failures without treating missing data as a height change.
