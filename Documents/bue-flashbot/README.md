# BUE FlashBot

## Setup

```bash
bash scripts/install.sh
```

## Launch

```bash
bash scripts/launch.sh
```

- All logs are stored in `logs/`
- Dashboard runs via Streamlit
- Bot runs in background (auto-restart safe)

## File Structure

- `bot/` - Core trading logic
- `dashboard/` - Streamlit dashboard
- `logs/` - Log files (auto-rotated)
- `scripts/` - Install and launch scripts 