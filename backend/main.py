from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.security import router as auth_router, get_current_user
from schemas.user import UserResponse
from db.database import create_db_and_tables
from routers import stats_routes, leaderboard
import models.user  # Import models so SQLAlchemy knows about them
import models.player  # Import models so SQLAlchemy knows about them

app = FastAPI(
    title = "PLGuesser-API",
    description = "PLGuesser API",
    version = "1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    )

@app.on_event("startup")
async def startup_event():
    try:
        # ADD THIS BLOCK:
        from db.database import engine
        import os
        print(f"[DEBUG] Current working directory: {os.getcwd()}")
        print(f"[DEBUG] Database URL: {engine.url}")
        print(f"[DEBUG] Resolved database path: {engine.url.database}")
        print()
        
        create_db_and_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(stats_routes.router)
from routers import crud_game, crud_player
app.include_router(crud_game.router)
app.include_router(crud_player.router)
app.include_router(leaderboard.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "Welcome to PLGuesser API"}

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)