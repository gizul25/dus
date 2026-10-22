# Environment

For Kafka Python scripts, enter kafka container and enter Python virtual environment of `ws` container:
```bash
uv venv --seed --allow-existing
source .venv/bin/activate
uv pip install -r pyproject.toml
```

# Commands

```bash
# Get messages sent from WebSocket connections
python consumer-ws.py
# Send messages to WebSocket connections
python producer-ws.py
```