# app/schemas/player.py
from pydantic import BaseModel, Field
from typing import Optional
from ..models.enum import Action

class PlayerCreate(BaseModel):
    """プレイヤー作成時の入力スキーマ"""
    name: str
    stack: int

class PlayerAction(BaseModel):
    """プレイヤーのアクション入力スキーマ"""
    action: Action
    amount: Optional[int] = None