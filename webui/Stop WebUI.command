#!/usr/bin/env bash
# Stop WebUI.command — doppio click su Mac per fermare il server build
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/server.pid"

# ── Leggi PID ─────────────────────────────────────────────────────────────
if [ ! -f "$PID_FILE" ]; then
    echo "ℹ️  Nessun PID file trovato — il server non risulta in esecuzione."
    sleep 4
    exit 0
fi

SERVER_PID=$(cat "$PID_FILE")

if [ -z "$SERVER_PID" ]; then
    echo "ℹ️  PID file vuoto — rimozione."
    rm -f "$PID_FILE"
    sleep 4
    exit 0
fi

# ── Verifica che il processo esista ──────────────────────────────────────
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "ℹ️  Il processo $SERVER_PID non è più in esecuzione."
    rm -f "$PID_FILE"
    sleep 4
    exit 0
fi

# ── Kill ──────────────────────────────────────────────────────────────────
echo "→ Fermando il server (PID $SERVER_PID)..."
kill "$SERVER_PID"

# Aspetta fino a 5 secondi che il processo termini
for i in 1 2 3 4 5; do
    sleep 1
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        break
    fi
    if [ "$i" -eq 5 ]; then
        echo "⚠️  Il processo non risponde — forzando (SIGKILL)..."
        kill -9 "$SERVER_PID" 2>/dev/null || true
    fi
done

rm -f "$PID_FILE"
echo "✅ Server fermato."
sleep 3
