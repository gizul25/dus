# Data visualization high-level design #16

## Module features

- Desk data
  - Show desk usage and occupancy data
  - Display desk height changes over time
  - Show statistics for a selected desk or workspace
  - Visualize data using charts and workspace maps
  - Filter data by desk and time period
- User data
  - Display sitting and standing time
  - Environmental parameters: temperature, etc.

## Module handling

- Invalid or missing sensor data should not be displayed as valid data
- Desk height cannot be negative or outside the supported range
- Missing data should be marked as unavailable
- Invalid date ranges and filters should be rejected
- Temporary connection problems should not crash the visualization

## Error handling

The API should return clear errors:

DATA_NOT_FOUND INVALID_DATA INVALID_DATE_RANGE UNAUTHORIZED DATA_UNAVAILABLE

## Use cases

- Check how often a desk is used
- See sitting/standing statistics
- Check which desks are currently occupied
- Compare desk usage over different days
- View historical desk data
- Identify unusual desk usage or possible maintenance issues

## Dependencies

- Desk module – desk and workspace information
- Embedded module – height, occupancy and sensor data
- Database – historical measurements
- Authentication – access permissions
- MongoDB – provides directly data to the visualization module
