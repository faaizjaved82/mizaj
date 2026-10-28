#!/usr/bin/env bash
# Nightly SQLite backup, 21 days kept.
set -euo pipefail
DIR=/opt/mizaj/backups
mkdir -p "$DIR"
STAMP=$(date +%Y%m%d)
/opt/mizaj/venv/bin/python - "$DIR/mizaj-$STAMP.db" <<'PY'
import sqlite3, sys
src = sqlite3.connect("/opt/mizaj/data/mizaj.db")
dst = sqlite3.connect(sys.argv[1])
src.backup(dst)
dst.close(); src.close()
PY
gzip -f "$DIR/mizaj-$STAMP.db"
find "$DIR" -name 'mizaj-*.db.gz' -mtime +21 -delete
