# (Desk) profile configuration system high-level design #7

### Module features

- Create desk profiles
- Edit desk profiles
- Delete desk profiles
- Select profile for occupied, free, custom, idle etc.
- Configure preferred desk heights/profile for each profile (make it automatic
  for which time it should move up/down or on your own select)
  - Sitting height
  - Standing height
  - Desk reads another desk picked on the map by the user and it reads the
    height of the other desk and then it automatically switches the height of
    the other desk (find on map and switches the height of the selected desk)
  - Optional custom positions
- Associate a profile with a specific desk

### Module handling

- Strange input values
  - Height cannot be negative
  - Height must be within the minimum and maximum height supported by the desk
  - Profile name cannot be empty and should have a reasonable maximum length
  - Invalid data types should be rejected
  - A user should only be able to edit their own profiles
  - If a desk does not provide its height limits, the profile should not accept
    a new height until the desk configuration is available
  - Two desk profiles can't be assigned at the same time

### Error handling

The API should return a clear error when a profile cannot be created or edited

INVALID_HEIGHT NOT_SAVED_PROFILE PROFILE_NOT_FOUND NOT_AUTHORIZED
INVALID_PROFILE_NAME

### Use cases

- Configure freely desk's profile
- Change the height of the desk to suit the user
- Automatic timer of desk up/down
