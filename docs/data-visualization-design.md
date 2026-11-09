# Data Visualsation Design
## Frontend
The page list up all relevant informations of any desk.  

### Simplified page design
``` 
-----------------------------------------
|  [Desk-DropDown]                      |
|  -----------------------------------  |
|  Desk ID: ...                         |
|  Status: ...                          |
|  Height: ...                          |
|  -----------------------------------  |
|  Logs:                                |
|      ....                             |
|                                       |
-----------------------------------------
```
Selection of a desk via Dropdown menu. 
Given information:
- Desk ID
- Status
- Height

A extra section for logs. Displaying every log entry for this desk.
log entries are:
- Errors
- Warnings
- Changes
- Whatever information related to the desk.

## Backend
Probaly a wrapper that gives the information from DB.
Some safety check account related could be also good.

The wrapper gets a desk model based on requested desk.
