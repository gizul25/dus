# Data Visualsation Design
The simplified version is simpler to imlement.
## Frontend
The page list up all relevant informations of any desk.  

### Simplified page design
``` 
-----------------------------------------
|  Enviromental                         |
|  -----------------------------------  |
|  temperature: ...                     |
|  ...                                  |
|  -----------------------------------  |
|  User                                 |
|  -----------------------------------  |
|  Sitting time: ...                    |
|  Standing time: ...                   |
|  -----------------------------------  |
|  [Desk-DropDown]                      |
|  -----------------------------------  |
|  Desk ID: ...                         |
|  Status: ...                          |
|  Height: ...                          |
|  Usage: ...                           |
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
- usages

A extra section for logs. Displaying every log entry for this desk.
log entries are:
- Errors
- Warnings
- Changes
- Whatever information related to the desk.

Data gathering only on_change or on_load demand.

## Backend
Probaly a wrapper that gives the information from DB.
Some safety check account related could be also good.

The wrapper gets a desk model based on requested desk.

