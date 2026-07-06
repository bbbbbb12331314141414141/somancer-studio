#!/bin/bash
# Seed the genre database with initial data
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/packages/backend"

echo "🎵 Seeding Somancer genre database…"

cd "$BACKEND_DIR"

# Activate venv if present
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

python -m aimusic.utils.seed_genres

echo "✅ Done!"
