#!/usr/bin/env bash
# MathWeb local development helper.
# Sets up (idempotently) the Postgres container, the pgvector extension,
# migrations and the Tailscale-aware .env, then serves the Django app.
#
# Usage:
#   ./dev.sh                        # setup + runserver
#   NO_SUPERUSER=1 ./dev.sh         # skip the superuser check
#   TESTS=1 ./dev.sh                # run the Django test suite before serving
#
# Re-run as many times as needed: existing pieces get started, not recreated.

set -euo pipefail

PG_CONTAINER=mathweb-pg
PG_USER=alfer_user
PG_PASSWORD=teladeunarajna123
PG_DB=mathweb_db
PG_IMAGE=pgvector/pgvector:pg16
PORT="${PORT:-8010}"

fail() { echo "ERROR: $*" >&2; exit 1; }

# --- Docker ------------------------------------------------------------
command -v docker >/dev/null || fail "docker is not installed"
if ! docker ps >/dev/null 2>&1; then
    if docker ps 2>&1 | grep -q "permission denied"; then
        fail "Docker socket permission denied: add yourself to the docker group with 'sudo usermod -aG docker $USER', then run 'newgrp docker' (or re-login)"
    fi
    fail "Docker daemon not running (start Docker Desktop, or 'sudo systemctl start docker')"
fi

if ! docker inspect "$PG_CONTAINER" >/dev/null 2>&1; then
    echo "Creating Postgres container ($PG_IMAGE)..."
    docker run -d --name "$PG_CONTAINER" \
        -e POSTGRES_USER="$PG_USER" \
        -e POSTGRES_PASSWORD="$PG_PASSWORD" \
        -e POSTGRES_DB="$PG_DB" \
        -p 127.0.0.1:5432:5432 \
        -v mathweb_pgdata:/var/lib/postgresql/data \
        "$PG_IMAGE"
else
    echo "Starting existing Postgres container..."
    docker start "$PG_CONTAINER" >/dev/null
fi

echo "Waiting for Postgres..."
ready=0
for _ in $(seq 1 30); do
    if docker exec "$PG_CONTAINER" pg_isready -U "$PG_USER" -d "$PG_DB" >/dev/null 2>&1; then
        ready=1; break
    fi
    sleep 1
done
[[ "$ready" == "1" ]] || fail "Postgres did not become ready in time"

# VectorField needs the pgvector extension (stock postgres does not ship it).
docker exec "$PG_CONTAINER" psql -U "$PG_USER" -d "$PG_DB" \
    -c "CREATE EXTENSION IF NOT EXISTS vector;"

# --- .env: allow the Tailscale IP ----------------------------------------
TAIL_IP="$(tailscale ip -4 2>/dev/null || true)"
BIND_IP="${TAIL_IP:-0.0.0.0}"
if [[ -z "$TAIL_IP" ]]; then
    echo "WARNING: no Tailscale IP found; server will bind to $BIND_IP"
fi

python3 - "$TAIL_IP" "$PORT" <<'PYEOF'
import sys
tail_ip = sys.argv[1]
path = ".env"
lines = open(path, newline="").read().splitlines()

def set_csv(lines, key, value):
    out, found = [], False
    for line in lines:
        name = line.split("=", 1)[0].strip()
        if name == key:
            items = [i for i in line.split("=", 1)[1].strip().split(",") if i]
            if value and value not in items:
                items.append(value)
            out.append(f"{key}={','.join(items)}")
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f"{key}={value}")
    return out

if tail_ip:
    lines = set_csv(lines, "ALLOWED_HOSTS", tail_ip)
    lines = set_csv(lines, "CSRF_TRUSTED_ORIGINS", f"http://{tail_ip}:{sys.argv[2]}")
    open(path, "w", newline="\n").write("\n".join(lines) + "\n")
    print(f".env updated with Tailscale IP {tail_ip}")
PYEOF

# --- Django ---------------------------------------------------------------
source .venv/bin/activate
python manage.py migrate --noinput

if [[ "${NO_SUPERUSER:-0}" != "1" ]]; then
    counting=$(python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
print(User.objects.filter(is_superuser=True).count())
" | tail -1)
    if [[ "$counting" == "0" ]]; then
        echo "No superuser yet; please create one:"
        python manage.py createsuperuser
    fi
fi

if [[ "${TESTS:-0}" == "1" ]]; then
    echo "Running the Django test suite..."
    python manage.py test
fi

echo "Serving on http://${BIND_IP}:${PORT} (Ctrl+C to stop)"
exec python manage.py runserver "${BIND_IP}:${PORT}"
