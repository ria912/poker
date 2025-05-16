# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from api import game  # api/game.py にある router

app = FastAPI()

# frontend ディレクトリのパス
frontend_dir = Path(__file__).parent.parent / "frontend"

# js フォルダだけを静的にマウント
app.mount("/static/js", StaticFiles(directory=frontend_dir / "js"), name="js")

# APIルーター
app.include_router(game.router, prefix="/api")

# index.html を返す
@app.get("/")
def serve_spa():
    return FileResponse(frontend_dir / "index.html")
