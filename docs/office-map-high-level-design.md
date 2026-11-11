# Office map high-level design #11

### Module features

- A 2d map as a overview of all the desks.
- Quick status reflection of all the desks.
  - is used
  - on break
  - free to use
- Usage overview via a heat-map.

### Maybe?

- Location accurate depiction.
  - to arrange desk layout with a editor
  - Error reporting of desk

### Module handling

Error: Missing data
Debugging: Vitest, Playwright, manual

### Use cases

- open map page via app or web interface
- click on a desk to see more details.
- switch freely between heat-map and current status map.

### Test cases

- loading all necessary data
- display all desks
- switch between heat-map, status-map and possible more
- click on a desk in both modes

### Modules

- Map page

### Other module dependencies

- database
  - to get the data
- frontend:
  - app/we-interface to include this page.
