#!/usr/bin/env bash
# Start WebUI.command — doppio click su Mac per avviare il server build
set -euo pipefail

# ── Trova la root del repo (parent di webui/) ─────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOGS_DIR="$SCRIPT_DIR/logs"
PID_FILE="$LOGS_DIR/server.pid"
LOG_FILE="$LOGS_DIR/server.log"

cd "$REPO_ROOT"

# ── Controlla se il server è già in esecuzione ────────────────────────────
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "⚠️  Il server è già in esecuzione (PID $OLD_PID)."
        echo "   Apri http://localhost:5001"
        echo "   Per fermarlo: doppio click su 'Stop WebUI.command'"
        sleep 5
        exit 0
    else
        # PID file stale — rimuovi
        rm -f "$PID_FILE"
    fi
fi

# ── Seleziona interprete Python ───────────────────────────────────────────
if [ -f "$REPO_ROOT/venv/bin/activate" ]; then
    echo "→ Attivazione venv: $REPO_ROOT/venv"
    # shellcheck disable=SC1091
    source "$REPO_ROOT/venv/bin/activate"
    PYTHON="python"
elif [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    echo "→ Attivazione venv: $SCRIPT_DIR/venv"
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/venv/bin/activate"
    PYTHON="python"
else
    PYTHON="python3"
    echo "→ Usando python3 di sistema: $(which python3)"
fi

# ── Verifica Flask ────────────────────────────────────────────────────────
if ! $PYTHON -c "import flask" 2>/dev/null; then
    echo ""
    echo "❌ Flask non trovato."
    echo "   Installa con:  pip3 install flask"
    echo ""
    sleep 8
    exit 1
fi

# ── Avvia il server ───────────────────────────────────────────────────────
echo "→ Avvio server..."
echo "   Log: $LOG_FILE"
echo ""

nohup $PYTHON webui/server.py > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

# Aspetta un momento per verificare che il processo sia partito
sleep 1
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "❌ Il server non è partito. Controlla il log:"
    echo ""
    cat "$LOG_FILE"
    rm -f "$PID_FILE"
    sleep 10
    exit 1
fi

echo "✅ Server avviato (PID $SERVER_PID)"
echo ""
echo "   URL:   http://localhost:5001"
echo "   Log:   $LOG_FILE"
echo "   Stop:  doppio click su 'Stop WebUI.command'"
echo ""
echo "Questa finestra può essere chiusa."
sleep 5
