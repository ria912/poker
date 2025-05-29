# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from api import game

app = FastAPI()

# CORS設定（フロントエンドが別ホストの場合は必須）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発時はすべて許可。本番は必要に応じて限定。
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# APIルーター登録（必要なら prefix="/api" を付ける）
app.include_router(game.router, prefix="/api")

# 開発用：フロントエンドの静的ファイル配信 ---
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# ルートアクセスで SPA の入り口を返す ---
@app.get("/")
def serve_spa():
    return FileResponse(frontend_dir / "index.html")
