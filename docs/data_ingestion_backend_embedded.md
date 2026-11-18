# Design for data ingestion backend-embedded - #92

## High-level design

### Module features

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
> Voltage usage might not be available.
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

### Module handling

Strange input values:

- Low-key nothing fancy, as long as it conforms to the schema in which we store
  the data in the database, it's fine. And there might be plenty of room for
  NULL values.
- Each device type has its own set of schemas it can add, so need to handle
  invalid data types
- Adding data points retroactively (from very far past) is allowed (e.g. device
  was offline for quite some time) for Raspberry Pi Pico
> Currently handled by MQTT configuration.
- Also it only takes the data from authenticated devices - yes, Raspberry Pico
  will have some authenticated encrypted channel, and for ID it will take the
  current device, so it shouldn't be a concern about fake or invalid IDs.
  - For user telemetry, there will be separate endpoint '/telemetry' to handle
    web data more securely, and allow blocking by 3rd party extensions
> MQTT is using TLS with client and server certificates. Frontend `/telemetry` uses WebSockets, and will use WSS in production environment.
> Desk API REST server can be setup with HTTPS.
- What if device was offline for some time and unable to send data? Well, it
  should just send data when it can. It can send data from very far past. For
  browser, telemetry is not really relevant when internet is not accessible, so
  it shouldn't handle offline data telemetry collection.
> For Pico, any buffering and error handling is handled by MQTT protocol. Frontend telemetry does not need buffering and resending.
> Desk API REST server is external server, and any reliability of REST API server is out of scope.

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

## Use cases

- Every 5 seconds, the sensor data from Raspberry Pi Pico is sent to the server,
  and is stored in the database.
- On error on the browser, telemetry is sent to the server.

### Test cases

- Connection drops
- Internet goes down
- Database is full
- 100+ example devices are connected and sending data, a lot of it
- Data was not retrieved or collected for an hour or so

## Pico

### Data

Embedded:
- temperature
- humidity
- light

Desk REST API:
- errors
- status
All available sensor readings in one message, if one is unavailable, the field is omitted.

### MQTT

MQTT Broker - Mosquitto:

- container running `mosquitto` from the image `eclipse-mosquitto:latest` with
  ports `1883:1883`
- Port `1883`: standard MQTT (unencrypted)
- configure in `/mosquitto.conf`

Backend Python MQTT Client - subscriber:

- connect to MQTT broker, subscribe to relevant topics, receive messages, and
  forward valid data for processing
- `paho-mqtt`

Pico W MQTT Client - publisher:

- connects to MQTT broker and publishes sensor measurement/relevant device
  status/error info
- `MQTTClient.h` (IwIP)

#### TOPICS (created on subscription)

- `pico/pico-001/sensors` -> or any other desk#
- message has: timestamp, temperature, humidity, light
- if we have errors/status, it would be under a different topic Publishing:
- sends message topic, message QOS and retain flag
- `QOS-1`: guarantees message delivery (duplicate) Subscribing:
- QOS-1 of topic subscription?
- pico/+/sensors (subscribe to all picos)

### Processing

- Pico ID from MQTT topic
- Look up of Pico's registration and desk association in DB
- Sensor reading not stored if Pico is not registered/not associated
- Validating available sensor readings
- One historical doc containing all avaliable readings and the associated desk ID (if a pico moves to a diff desk, the historical data should be associated with the desk, not pico)

### Database Schemas

## Desk

- All desks connect to WiFi2BLE Box, which connects to backend through REST API

### Data

Desk REST API:
- Number of desks connected to WiFi2BLE box
- Desk ID, Name, Manufacturer
- Position (get/set)
- Position Lost flag
- Overload Protection Up/Down flags
- Anti Collision flag
- Status
- Last errors with timestamps
- Activation counter
- Sit/stand counter

### REST API

- [SDM Edu / WiFi2BLE Box Simulator · GitLab](https://source.coderefinery.org/sdm-edu/wifi2ble-box-simulator)
- `requests`

## Database Schemas

desks:

- "desk_id"
- "pico_id"

(identify desk and store Pico associated with that desk)

sensor_readings:

- "_id"
- "desk_id"
- "timestamp"
- "temperature"
- "humidity"
- "light"

desk_readings:

- "id"
- "desk_id"
- "timestamp"
- "height"
- "status"
- "pico_id" -> maybe needed for debugging?