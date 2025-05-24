# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from api import game  # ゲーム用APIを登録

app = FastAPI()

# フロントエンド（HTML, JS, CSS）を /static に公開
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# ゲームAPIのルーターを /api にまとめて登録
app.include_router(game.router, prefix="/api")

# ブラウザで "/" にアクセスすると index.html を返す
@app.get("/")
def serve_spa():
    return FileResponse(frontend_dir / "index.html")
