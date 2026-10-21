#!/bin/bash

set -e

. "$HOME/.local/bin/env"

uv venv .venv-ws --allow-existing
. ".venv-ws/bin/activate"

exec uv run uvicorn app:ws_app --host 0.0.0.0 --port 7000 --reload --ws=websockets-sansio