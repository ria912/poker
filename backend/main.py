# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import game  # ゲーム用APIエンドポイント

app = FastAPI()

# フロントエンド（別オリジン）からのアクセスを許可するためにCORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発中は "*" でOK。本番はドメインを指定。
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターを登録
app.include_router(game.router)
