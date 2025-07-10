# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api import ai_game

app = FastAPI()

# --- CORS (フロントがlocalhostで動く場合に必要) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番は限定すべき
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ルーター登録 (これによりapi/game/...が利用可能になる) ---
app.include_router(ai_game.router, prefix="/api")

# --- 静的ファイル（フロントHTMLがpublic/にある想定） ---
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
