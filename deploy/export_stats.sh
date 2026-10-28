#!/usr/bin/env bash
# Weekly: write aggregate stats (no personal data) into the repo so the weekly COO session can read them.
set -euo pipefail
cd /opt/mizaj/app
/opt/mizaj/venv/bin/python -m mizaj export-stats ops/stats/latest.json
cp ops/stats/latest.json "ops/stats/$(date +%Y-%m-%d).json"
git add ops/stats
git -c user.name="Mizaj VPS" -c user.email="ops@mizaj.pk" commit -q -m "ops: weekly stats $(date +%Y-%m-%d)" || exit 0
git push -q origin HEAD:main || echo "push failed (check deploy key has write access)"
