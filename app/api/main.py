from fastapi import FastAPI
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.api.routers import games

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI(
    title="Texas Hold'em API",
    description="A simple API to manage a Texas Hold'em game.",
    version="0.1.0",
)

# gamesルーターをアプリケーションに登録
app.include_router(games.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Texas Hold'em API!"}
