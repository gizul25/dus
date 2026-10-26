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

Relaunch `docker compose` if `docker-compose.yaml` or `Dockerfile`s were changed.

Server URIs:
- Nginx (w/ frontend + backend): http://localhost:8080/
- MongoDB: `mongodb://root:password@localhost:27017/`
- Raw frontend: http://localhost:5173/
- Backend: http://localhost:8000/

# Debugging tools

## Frontend

If you feel like import errors are false, you can try restarting frontend container:
```bash
docker restart dus-frontend-1
```

## Docker

```bash
# List running containers
docker ps

# Enter a running container
docker exec -it dus-frontend-1 /bin/bash
docker exec -it dus-backend-1 /bin/bash
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
