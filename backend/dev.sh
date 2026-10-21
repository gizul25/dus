#!/bin/bash

set -e

. "$HOME/.local/bin/env"
exec uv run uvicorn app:app --host 0.0.0.0 --reload