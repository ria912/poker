# app/schemas/response.py
from pydantic import BaseModel
from typing import List, Optional, Any
from ..models.player import Player
from ..models.table import Table

class Message(BaseModel):
    """シンプルなメッセージレスポンス用スキーマ"""
    message: str

class GameStateResponse(BaseModel):
    """現在のゲーム状態を返すためのスキーマ"""
    table: Table
    players: List[Player]
    active_player_id: Optional[str] = None
    message: str