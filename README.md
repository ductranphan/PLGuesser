**⚽️ PLGuesser**

https://pl-guesser.vercel.app/

PLGuesser is a Premier League–themed Wordle clone. Test your football knowledge by guessing the mystery player based on their stats, nationality, and position!

✨ Features
🟢 Free Play (Guest Mode): Jump right in and play unlimited rounds without an account.

📅 Daily Challenge: A unique player to guess every day (synchronized globally). Log in to track your streak!

📊 Advanced Stats: Track your win rate, current streak, and max streak.

🏆 Global Leaderboard: Compete against other users based on win rate and tie-breakers.

🎨 Immersive UI: A clean, responsive interface inspired by the official Premier League branding.

🛠 Tech Stack
Frontend
Framework: React + Vite

Styling: Tailwind CSS

State/Routing: React Router

Backend
API: FastAPI (Python)

ORM: SQLAlchemy

Database: PostgreSQL (Production) / SQLite (Optional for local dev)

🚀 Getting Started (Local Development)
Follow these steps to get a local copy up and running.

1. Clone the Repository

git clone <your-repo-url>
cd PLGuesser

3. Backend Setup

Navigate to the backend folder, create a virtual environment, and install dependencies.
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
3. Database & Environment (Backend)
Create a .env file in the backend/ directory:

Code snippet

DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME
ALLOWED_ORIGINS=http://localhost:5173
SECRET_KEY=your_super_secret_key
4. Seed Data
Populate your local database with Premier League player data.

# Ensure you are in the root or backend directory and venv is active
python backend/scripts/seed_players.py
5. Frontend Setup
Open a new terminal, navigate to the frontend, and run the app.

cd frontend
npm install

# Create .env (optional)
echo "VITE_API_URL=http://localhost:8000" > .env

npm run dev
Your app should now be running at http://localhost:5173! 🚀

🌍 Deployment
Database (Render/Neon/Supabase)
Ensure your production database is accessible. Update your backend environment variables to match your provider.

Backend (Render)
Connect your repo to Render.

Set the Build Command: pip install -r requirements.txt.

Set the Start Command: uvicorn main:app --host 0.0.0.0 --port 10000 or python main.py

Add Environment Variables:

DATABASE_URL: https://dashboard.render.com/d/dpg-d5lfh8re5dus73dofs00-a

ALLOWED_ORIGINS: https://pl-guesser.vercel.app/

Frontend (Vercel)
Connect your repo.

Set the Build Command: npm run build.

Add Environment Variables:

VITE_API_URL: https://plguesser.onrender.com/

📝 Notes
Timezone: The Daily Challenge resets at midnight Eastern Time (ET).

Guest Mode: Stats are not saved if you play as a guest. Create an account to save your progress!
