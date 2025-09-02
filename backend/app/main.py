# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import games

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI(
    title="Texas Hold'em API",
    description="A simple API to manage a Texas Hold'em game.",
    version="0.1.0",
)

# --- CORSミドルウェアの設定 ---
origins = [
    "http://localhost",       # ローカル環境
    "http://localhost:3000",  # Reactのデフォルト開発サーバー
    "http://localhost:5173",  # Vite (Vue, React) のデフォルト開発サーバー
    # フロントエンドのデプロイ先のドメインなども必要に応じて追加
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)

# gamesルーターをアプリケーションに登録
app.include_router(games.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Texas Hold'em API!"}
