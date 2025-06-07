#!/bin/bash
set -e

# Activate venv
source .venv/bin/activate

# Ensure logs directory exists
mkdir -p logs

# Start bot in background if not running
if pgrep -f "python bot/engine.py" > /dev/null; then
  echo "Bot already running."
else
  nohup python bot/engine.py "$@" > logs/bot_$(date +%Y%m%d).log 2>&1 &
  echo "Bot started."
fi

# Launch Streamlit dashboard
streamlit run dashboard/sb_dashboard.py --logger.level=error 2>> logs/dashboard.log 