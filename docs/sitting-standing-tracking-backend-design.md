# Sitting/Standing Tracking Design #73

- Define how desk height data is collected and compared over time.
- Define the timer logic for detecting prolonged sitting and resetting after height changes.

### Desk Height Data Collection and Comparison
- Data collection: The backend receives desk height measurements from the desk or frontend at regular intervals. Each measurement is associated with a timestamp.
- Data storage: The backend stores height measurements persistently. It keeps the current and previous measurements for comparison and can store historical measurements to track height changes over time and generate graphs.
- Height comparison: Each new measurement is compared with the previous measurement to detect changes in desk height. Historical measurements can also be compared with adjacent measurements to analyze height changes over time.
- Position detection: Configurable height thresholds are used to determine whether the desk is in a sitting or standing position. The system uses a sitting threshold and a standing threshold to distinguish between the two positions. If the desk height falls between these thresholds, the system retains its previously confirmed position until the height reaches the threshold for the other position.
- Filtering fluctuations: Small height adjustments are handled by the configured thresholds. A new position is confirmed only after the desk height meets the relevant threshold conditions for a defined period, preventing temporary fluctuations from causing unnecessary position changes

### Timer Logic
- Timer start: When the desk is confirmed to be at sitting height, the backend starts a sitting period and records its start timestamp.
- Timer tracking: The backend calculates the sitting duration using the start timestamp and the current time.
- Height changes: Each new height measurement is checked by the position detection logic. Small adjustments that do not meet the threshold for a position change do not reset the sitting timer.
- Timer reset: When standing height is confirmed, the current sitting period ends and its duration is recorded. If the desk returns to sitting height, a new sitting period begins.
- Prolonged sitting detection: When the sitting duration reaches the configured time limit, the backend triggers a reminder.
- Reminder handling: The system prevents repeated reminders during the same sitting period by default. Recurring reminders can optionally be configured.
- Missing measurements: If measurements stop arriving, the system does not automatically assume that the desk has changed position or reset the timer. The last confirmed position and sitting period remain unchanged until new measurements arrive.

### Possible Implementation Structure
The implementation can be divided into separate modules to keep the system organized and easy to maintain.

- HeightMeasurementService: Receives and validates height measurements and timestamps.
- PositionDetectionService: Compares measurements against configured height thresholds and determines the desk's position.
- SittingTimerService: Starts and ends sitting periods, calculates sitting duration, and checks the configured time limit.
- ReminderService: Triggers reminders and prevents duplicate notifications.
- MeasurementRepository: Stores current and historical height measurements for comparison and graph generation.
- SittingPeriodRepository: Stores sitting period start times, end times, and durations.

A database can be used for persistent storage, while the programming language's built-in date and time functionality can handle timestamps and duration calculations. A frontend graphing library can optionally be used to visualize historical desk height measurements.