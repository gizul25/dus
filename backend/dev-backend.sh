#!/bin/bash

set -e

. "$HOME/.local/bin/env"

uv venv .venv-backend --allow-existing
. ".venv-backend/bin/activate"

export PYTHONUNBUFFERED=1
exec uv run uvicorn app:backend_app --host 0.0.0.0 --port 8000 --reload