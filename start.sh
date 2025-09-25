#!/bin/bash
export PATH="/opt/venv/bin:$PATH"
python -c "from database import init_db; init_db()" 2>/dev/null || echo "DB init failed"
exec gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1 --preload