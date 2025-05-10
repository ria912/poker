# api/game.py
# backend/api/game.py

from fastapi import APIRouter

router = APIRouter(prefix="/game", tags=["game"])

@router.get("/ping")
def ping():
    return {"message": "pong"}
