# User account and auth high-level design #19

## Module features
- User accounts allow for the user to be able to change their desk preferences
  - They can change the height, velocity and set specific settings as a profile for their needs
- User can choose a desk of choice which they want to work on
  - To do that they can interact with the map interface 
  - If a desk is occupied the map interface will inform them that the desk in question is busy
- User can log into their account by providing the right credentials such as first and last name and password 
- The interface allows users to report issues with their desk

### Maybe?
- Users can put in comments on the desks they are using for co-workers to see
  - Could be useful if they are not at their desk currently and want to notify others on a certain matter 
- The users can view the amount of time they had spent while working on the desk

## Module handling
- Authorization
  - User can only log into their account by inputting the right data
- Error handling
  - Deny request if wrong or empty information is used
- Testing - Vitest, Playwright, manual

## Use cases
- User logs into their account
- User selects a desk to use
- User sets up their profile for work
- User changes their preferences in their settings
- User sends an error report
- User makes a comment(From the Maybe? section)
- User views time spent on desk(From the Maybe? section)

## Test cases
- User successfully logs into their account
- User successfully sets their preferences for the desk
- User is unable to send an error report(insufficient)
- User sends an error report successfully
- User leaves a comment successfully
- User is unable to leave a comment(insufficient)
- User is able to select a desk to work on
- User is unable to select a desk(busy or already chosen)

## Dependencies
### Module
- Data visualization
- Office map system
- Frontend
  - Web interface 
- Databases
  - Error logs
  - User accounts

### External
- N/A