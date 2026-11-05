# Data ingestion system high-level design #10

# Module features

- Collect the data from the desk
- Collect the data from the Raspberry Pico
- Collect the data from the user interactions (frontend)
  - This includes only telemetry

Any other data is collected by respective modules.

Responsibilities are clear. Collect respective data.

What concrete data? Preliminary idea:

- Desk:
  - Current height
  - Current profile
  - Current user
  - Voltage usage (from motor)
  - Error notifications (e.g. collisions)
- Raspberry Pi Pico
  - Temperature
  - Humidity
  - Light
- User interactions
  - Telemetry everything has time and relevant entities associated - user, desk,
    Raspberry Pico device, etc.

Note: desk control such as desk go up or down is handled by parameter editing
module, which is not part of data ingestion module.

It stores all the data in MongoDB. The module is also concerned with some
database schemas.

# Module handling

Strange input values:

- Low-key nothing fancy, as long as it conforms to the schema in which we store
  the data in the database, it's fine. And there might be plenty of room for
  NULL values.
- Each device type has its own set of schemas it can add, so need to handle
  invalid data types
- Adding data points retroactively (from very far past) is allowed (e.g. device
  was offline for quite some time) for Raspberry Pi Pico
- Also it only takes the data from authenticated devices - yes, Raspberry Pico
  will have some authenticated encrypted channel, and for ID it will take the
  current device, so it shouldn't be a concern about fake or invalid IDs.
  - For user telemetry, there will be separate endpoint '/telemetry' to handle
    web data more securely, and allow blocking by 3rd party extensions

- What if device was offline for some time and unable to send data? Well, it
  should just send data when it can. It can send data from very far past. For
  browser, telemetry is not really relevant when internet is not accessible, so
  it shouldn't handle offline data telemetry collection.

Logging:

- Standard backend logging into console (stdout) which is redirected to a file.
  Log levels split into DEBUG, INFO, WARNING, ERROR, FATAL in a standard
  fashion. Mostly any connection data is important, and any accidentally dropped
  connections or failed to connect should be properly logged. Same for any
  incoming data which for some reason doesn't match the database schema.

Debugging:

- Reading logs, inspecting database, sending testing requests

Async requests:

- All I can say is yes.

API:

- Polling method for Raspberry Pi and desk data. Raspberry Pi exposes desk data
  together with its own data. Raspberry Pi hosts endpoint called '/get_data',
  which returns Pico environment data since last request, timestamp is relative.
  same for desk data.
- relative timestamp means that pico collects data from desk and environment
   periodically, and stores it in its own timestamp. then when request is
   received, it substracts requests timestamp from data timestamp. in backend,
   timestamps are converted to regular server timestamp
- the data buffer entries are removed, which are before request timestamp (not
   all to handle any data updates while request is handled)
- picos are connected to corporate network (i know, very secure, not sure how
   to solve), and server runs on-prem, direct access to picos from server
   shouldn't be a problem. IP addresses of picos are part of desk admin setup.
- though maybe it should treat as server runs on cloud? then problematic for
    server to poll data. it makes sense then for device to initiate connection
    to the server, but it gives access to internet.
- device verifies server's connection certificate that it is really a server
   and not another unrelated device
- For Raspberry Pi, connection to the server might be changed depending on the
   infrastructure.
- For the browser, it will call `/telemetry` endpoint from the browser with user
  credentials.

# Use cases

- Every 5 seconds, the sensor data from Raspberry Pi Pico is sent to the server,
  and is stored in the database.
- On error on the browser, telemetry is sent to the server.

## Test cases

- Connection drops
- Internet goes down
- Database is full
- 100+ example devices are connected and sending data, a lot of it
- Data was not retrieved or collected for an hour or so
