#!/usr/bin/env bash
# Status WebUI.command — doppio click su Mac per verificare lo stato del server
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/server.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Server: DOWN"
    sleep 4
    exit 0
fi

SERVER_PID=$(cat "$PID_FILE")

if kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Server: UP (PID: $SERVER_PID) — http://localhost:5001"
else
    echo "Server: DOWN (processo non trovato, PID file rimosso)"
    rm -f "$PID_FILE"
fi

sleep 4
