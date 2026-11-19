# Backend services

We're using event-driven microservices architecture. Services are loosely coupled, and they communicate with messages and events between them. In our case, it is REST API for messaging, which maps well to actions, and Apache Kafka for events. What this means is that direct coupling is not allowed. If you access another service, it has to go through REST API or Apache Kafka.

Each service should be able to be scaled independently. Currently, our approach is one Python binary containing the code for all microservices. However, when launching, there should be functionality to specify which microservices are being run in the binary.

Load balancing/scaling REST APIs is easy, especially in Kubernetes with services, so that's not a concern. With Apache Kafka, you have different topics for different types of events. Partition key in the event message is used to determine, which node processes the event. Once the event is processed, it is consumed. To support multiple separate consumers, groups should be used. Partitioning provides scaling for event producers. Groups provide scaling for event consumers. If one group subscriber goes down, other subscribers will receive the event and process it. If during consumption of the event there is an error, the acknowledgment of the event is not sent, which means that the event is going to be sent to consumers again. This means Apache Kafka provides "exactly once" event delivery guarantee. Ideally, event processing should be idempotent, meaning that duplicate event should not modify application state further. You can read more about Apache Kafka here:
- https://kafka.apache.org/44/design/design/
- https://developer.confluent.io/learn-more/kafka-on-the-go/consumer-groups/
- https://www.conduktor.io/glossary/kafka-consumer-groups-explained

Follows `entities_relationships.md`. Frontend is expected to use REST API and WebSockets to communicate with the services. If in the future frontend needs to access more information, relevant services need to be modified. If the frontend needs to store more data, it depends. If it fits to already existing services, they are modified. If it a new feature, e.g. maps, then it should be a new service, which is loosely-coupled and has clear responsibilities.

Potentially missing:
- Analytics/statistics service
- Map service (e.g. user preferences, search)

Timer research:
- https://hackernoon.com/building-a-distributed-timer-service-at-scale-handling-100k-timers-per-second

Timing is a bit more complicated, as we need to keep track of timers between service restarts. Main issue is making it work reliably in a distributed system with multiple same service instances running on different nodes, and partitioning timers nicely with a decent plan of recovering timers from instances, which stopped working. A simple but problem approach we can take is to have a service, and it knows all the timestamps relevant to in a database. It is already handled by design. At the start of the service, service would start all the timers, which should end on relevant timestamps. If service needs to restart, no problem, as it would pick up the timers again on next start. However, there's no clear definition of partitioning timers between different service instances. Also, introducing timers to services adds a little bit of state too, which doesn't make the services itself stateless. So, a better idea would be to have a timer service, which would allow to register, add, remove timers, and it would send events when timers are triggered. It would scale independently from services themselves, and the stateful nature of them would be isolated, allowing easier scaling for other services depending on timers.

## User service

Fully owns "User" entity. Anything that modifies "User" entity goes through this handler. This includes CRUD for users and authentication. Authentication is too tightly-connected with User to move it to a separate service.

Creation, editing and deletion exposed to admin. Updating password and status is available to respective user.

When user logs in, the service will set status for the user to "online". And it will trigger "on status changed" event.

## WebSocket connection service

Fully owns "WebSocket connection" entity. Fully responsible for taking in WebSocket connections, communicating with User service to authenticate users, and to associate WebSocket connections to users. It also includes providing message receiving and sending functionality.

## Desk service

Fully owns "Desk" entity. This includes CRUD for desks for admins, automatic controlling of desk height based on desk profile data, updating desired target height from manual adjustments, which are retrieved from WebSockets messages (WebSocket connection service handles retrieving messages, and pushing them to Apache Kafka as events), adjusting height based on manual adjustments, and other parameters. It does not handle desk sessions or modifying desk profiles, as it is a concern of different services. It is responsible for sending PUT requests to update desk height. However, it is not responsible for retrieving data from the desk, as it is handled by desk data ingestion service.

## Desk session service

Fully owns "Desk session", and "Desk session config" entities. Fully responsible for check-in/check-out, handling automatic timeouts, and updating user status based on desk activity. Note that it has timestamps, which means it needs to correctly handle timers when service instances are restarting.

## Health reminder service

Fully owns "Health reminder" and "Health reminder preferences" entities. Fully responsible for handling all health related functionalities: tracking sitting and standing timers, sending notifications, changing profiles automatically, pausing timers when user changes their status to "away", and determining middle desk height threshold.

Similarly to "Desk session service", it contain timers.

## Desk profile service

Fully owns "Desk profile" entity. This service only has one responsibility - CRUD for desk profiles. However, it is separated as a separate service to more loosely couple and separate responsibilities, and to provide better room for future expansion.

## Desk issue service

Fully owns "Desk issue" entity. Responsible for CRUD for desk issues, sending notifications to admin when issues arise, and sending notifications to reporters when issues are resolved.

## Pico environmental data ingestion service

Fully owns "Pico environmental data" entity. Responsible for getting environmental data from Pico device, and storing it in the database. This service has embedded component written in C++, which is located in Raspberry Pi Pico, which publishes and subscribes to MQTT topics. Backend part is responsible for listening and responding to MQTT messages, storing them in a database, and sending relevant events.

## Desk data ingestion service

Fully owns "Last desk API fetch", "Realtime desk API data", and "Periodic desk API data" entities. Responsible for collecting the data from all desk REST APIs, storing them in a database, and sending relevant events. It is not responsible for modifying or sending commands to desk REST API server.

## Frontend telemetry service

Fully owns "Frontend telemetry" entity. Responsible for capturing frontend errors, and sending them to backend to be stored in a database. This service contains frontend element, which adds an error hook to frontend, and forwards these errors to backend.

## Timer service

Fully owns "Timer" entity. Responsible for CRUD (no update tho) for timers, and sending event once timer timestamp is reached. Service contains state, so it needs special attention. Scaling this service is problematic, so the best course of action for now is to define fixed partition count at the start of running the cluster, and use timer ID as a partition key.