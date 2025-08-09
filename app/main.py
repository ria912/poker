from fastapi import FastAPI
from app.routers import game  # gameルーターをインポート

# FastAPIのインスタンスを作成します
app = FastAPI(
    title="Poker API",
    description="テキサスホールデムポーカーをプレイするためのAPI",
    version="0.1.0",
)

# appにgameルーターを登録します
app.include_router(game.router)

# ルートURL ("/") へのGETリクエストを処理するエンドポイントを定義します
@app.get("/")
def read_root():
    """
    ルートエンドポイント。アプリケーションが動作していることを確認するための
    シンプルなメッセージを返します。
    """
    return {"message": "Welcome to Poker API!"}