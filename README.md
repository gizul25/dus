# Development setup

Constraints:
- Suited only for developments purposes.
- Security is not enforced: passwords are plaintext, services are exposed to LAN without encryption.  

```bash
# Launching dev server
docker compose up --build
# Press Ctrl+C to stop the server
# Because frontend doesn't close gracefully yet, need to press Ctrl+C twice to exit.
```

Relaunch `docker compose` if `docker-compose.yaml`, `nginx.conf`, `Dockerfile`s or other core infra files were changed. Changing Svelte in frontend and Python files in backend should automatically update them live with HMR (hot-module reloading). Websocket only reloads when files inside `ws/` folder change.

Currently MongoDB and Kafka have no persistence.

Server URIs:
- Nginx (w/ frontend + backend): http://localhost:8080/
- MongoDB: `mongodb://root:password@localhost:27017/`
- Raw frontend: http://localhost:5173/
- Backend: http://localhost:8000/

# Debugging tools

## Docker

```bash
# List running containers
docker ps

# Enter a running container
docker exec -it dus-frontend-1 /bin/bash
docker exec -it dus-backend-1 /bin/bash
```
Dev containers (all containers except Nginx and mongo one) have `tmux` installed, if you need to have multiple terminals open easily.

If any commands in Docker complain about missing env vars, such as `SHELL`, inside the attached container run:
```bash
sudo su user
```

Container starting order is not enforced, so fallback, timeouts and retries for connecting to other services are important.

## MongoDB Compass

GUI database debugging tool.

Download: https://www.mongodb.com/products/tools/compass

### Setup

- Disable telemetry in `Settings -> Privacy`.
- Add connection with URI `mongodb://root:password@localhost:27017/`.

## Nginx

- If you restart containers many times, the containers might get different IP addresses, and Nginx caches DNS lookup IP addresses. If you encounter any gateway issues, restart nginx container.

## Kafka

Inspection commands from https://kafka.apache.org/quickstart/ . You can run `bin/*` commands from `/home/user/kafka_2.13-4.3.1`. However, those commands are quite slow, so you kinda could use `kafka-python` (https://github.com/dpkp/kafka-python) for administration commands. For the lowest latency, use Python scripts in `infra/kafka/` (supported version).

Currently there's no automatic Kafka topic creation, you have to do it manually:
```bash
docker exec -it dus-kafka-1 /bin/bash
cd ~/kafka_2.13-4.3.1
bin/kafka-topics.sh --create --topic websocket-messages-client --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --topic websocket-messages-server --bootstrap-server localhost:9092
```

## WS

- Websocket receive is basically immediate on dev machine. Text updates immediately, but `console.log` in browser is delayed roughly ~0.5s. Might be because I used software rendering for the browser.
- If you have any errors in async task, it will not report error logs until it is cancelled. Notably, in `async def process_server_messages()`.