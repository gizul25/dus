#!/bin/bash

set -e

. "$HOME/.local/bin/env"

uv venv .venv-ws --allow-existing
. ".venv-ws/bin/activate"

export PYTHONUNBUFFERED=1
cd app/
exec uv run uvicorn ws:ws_app --host 0.0.0.0 --port 7000 --reload --reload-dir=/app/backend/app/ws --ws=websockets-sansio