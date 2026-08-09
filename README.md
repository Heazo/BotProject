# Polaris bot
A messanger bot for get individual lesson schedule.

## Dependencies :dizzy:
- vkbottle
- aiogram
- requests
- beautifulsoup4
- asyncpg
- sphinx
- thefuzz

## Installation

The project uses `pyproject.toml` as the dependency manifest:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .
```

For local development, copy `.env.example` to `.env` and fill in the real
tokens and database password. The `.env` file is ignored by Git and must not
be committed.

Start the application with:

```powershell
python main.py
```
