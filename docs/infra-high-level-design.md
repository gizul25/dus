# Overall high-level infra design #20

<img width="1152" height="342" alt="Image" src="https://github.com/user-attachments/assets/a66afb3e-9526-47be-a516-eee6bcaf3066" />

[infra_graph.drawio](https://github.com/user-attachments/files/33046808/infra_graphh.drawio)

- All the components except MongoDB and Apache Kafka are stateless
- WebSocket connections are stateless. Eavh connectiom has session id and messages are sent and received from Apache Kafka. In case WebSocket instance needs to be moved, client is asked to connect again, which will register a new connection with old session id.
- Kubernetes takes care of distributed and scaling part. Every server component is a Kubernetes service. Only Frontend is exposed under "/", websocket under "/ws", and backend under "/api". Exposing these services publically is responsibility of a load balancer. Load balancer also takes care of HTTPS termination. Authentication and authorization is left for each service, not part of load balancer.