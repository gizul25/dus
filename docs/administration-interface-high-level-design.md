# Administration interface high-level design #8

## Module features

- Special interface for the Administrator that allows them to monitor and manage the entire desk system and its users
  - The Administrator can log in through an address designated for them
- Administrator receives reports of errors about the desks from the users
  - A database of the error reports can be viewed in a sizable format
  - They can send the error to the appropriate person to fix it

### Maybe?

- The interface allows the Administrator to assign tasks for the workers in charge of them
  - Could be used if there is an urgent matter on the workplace(like a co-worker being unable to do their task)

## Module handling

- Authorization
  - Only Administrators can enter this interface
- Error handling
  - Deny login request to user if they had input wrong or empty information  
- Testing - Vitest, Playwright, manual

## Use Cases

- Administrator logs into the interface
- Administrator monitors status of the system and the users
- Administrator views the error logs and sends them to the appropriate repairman
- Administrator assigns tasks to workers(From the Maybe? section)

## Test Cases

- Successful login
- Administrator successfully views an error
- Unauthorized access of a non-Administrator account
- Administrator sends a error log to a repairman successfully
- Administrator unable to view an error log(non-existent or insufficient)

## Dependencies

### Module

- Data visualization
- Databases
  - Error logs
- Frontend
  - Web interface

### External

- N/A
