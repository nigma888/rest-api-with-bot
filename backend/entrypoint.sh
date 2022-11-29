#!/bin/bash

echo $SERVICE

if [ "$SERVICE" = "bot" ]; then
    python3 bot.py
else
    alembic upgrade head
    uvicorn api.main:app --host 0.0.0.0 --port 5001 --reload --log-level=info
fi
