#!/bin/bash

# 1. Start FastAPI in the background to satisfy Koyeb port requirements
uvicorn wrapper.server:app --host 0.0.0.0 --port 8000 &

# 2. Start the Telegram Bot
python /app/wrapper/bot.py
