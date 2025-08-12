from fastapi import FastAPI
from .api import table_router, game_router, player_router

app = FastAPI(
    title="Poker Game API",
    description="A simple API for a Texas Hold'em poker game.",
    version="1.0.0",
)

# 各ルーターをアプリケーションに含める
app.include_router(table_router.router)
app.include_router(game_router.router)
app.include_router(player_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Poker Game API!"}