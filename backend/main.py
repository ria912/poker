# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import game

app = FastAPI()

# フロントエンド（例えば localhost:3000）との通信を許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では限定した方がよい
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターを登録
app.include_router(game.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Poker API is running"}
