# Development setup

Constraints:
- Suited only for developments purposes.
- Security is not enforced: passwords are plaintext, services are exposed to LAN without encryption.  

```bash
# Launching dev server
docker compose up --build
# Press Ctrl+C to stop the server
```

Relaunch `docker compose` if `docker-compose.yaml` or `Dockerfile`s were changed.

Server URIs:
- MongoDB: `mongodb://root:password@localhost:27017/`
- Web server: http://localhost:5173/

# Debugging tools

## Docker

```bash
# List running containers
docker ps

# Enter a running container
docker exec -it dus-frontend-1 /bin/bash
```

If any commands in Docker complain about missing env vars, such as `SHELL`, inside the attached container run:
```bash
sudo su user
```

## MongoDB Compass

GUI database debugging tool.

Download: https://www.mongodb.com/products/tools/compass

### Setup

- Disable telemetry in `Settings -> Privacy`.
- Add connection with URI `mongodb://root:password@localhost:27017/`.
