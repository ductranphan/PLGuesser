# PLGuesser

Premier League–themed Wordle clone with guest play, daily challenges, stats, and a global leaderboard.

## Features
- Free play (guest) and daily challenge (logged-in)
- Player stats and win streaks
- Global leaderboard (win rate with tie-breakers)
- Premier League–inspired UI theme

## Tech Stack
- Frontend: React + Vite + Tailwind
- Backend: FastAPI + SQLAlchemy
- Database: SQLite (local) or PostgreSQL (prod)

## Getting Started (Local)

### 1) Clone and install
```
git clone <your-repo-url>
cd PLGuesser
```

#### Frontend
```
cd frontend
npm install
npm run dev
```

#### Backend
```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 2) Environment variables
Create `backend/.env`:
```
DATABASE_URL=sqlite:///./soccer_wordle.db
ALLOWED_ORIGINS=http://localhost:5173
SECRET_KEY=your_secret_key
```

Create `frontend/.env` (optional for local):
```
VITE_API_URL=http://localhost:8000
```

### 3) Seed players
```
python backend/scripts/seed_players.py
```

## Using PostgreSQL (Render)

1) Set backend env:
```
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

2) Set frontend env (Vercel):
```
VITE_API_URL=https://your-render-backend.onrender.com
```

3) (Optional) Migrate SQLite data to Postgres:
```
python backend/scripts/migrate_sqlite_to_postgres.py
```

4) If you migrated and get duplicate key errors:
```
python backend/scripts/reset_postgres_sequences.py
```

## How to Use From GitHub
1) Clone the repo and install dependencies (see Getting Started).
2) Set env vars for backend and frontend.
3) Seed players.
4) Run backend and frontend, then open the Vite URL (default `http://localhost:5173`).

## Scripts
- `backend/scripts/seed_players.py` — seed player data
- `backend/scripts/migrate_sqlite_to_postgres.py` — migrate SQLite to Postgres
- `backend/scripts/reset_postgres_sequences.py` — fix Postgres sequence ids after migration

## Notes
- Daily challenge uses Eastern Time for player selection.
- Guest mode is unlimited but does not track stats.
