# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from api import game  # api/game.py にある router

app = FastAPI()

# 静的ファイル（CSS, JSなど）を /static にマウント
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# APIルーターを /api にマウント
app.include_router(game.router, prefix="/api")

# フロントエンドの index.html をトップで返す
@app.get("/")
def serve_spa():
    return FileResponse(frontend_dir / "index.html")
