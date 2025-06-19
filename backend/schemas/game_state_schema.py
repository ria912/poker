# backend/schemas/game_state_schema.py
from pydantic import BaseModel
from typing import List, Optional
from backend.models.enum import Round, Position

class PlayerInfo(BaseModel):
    name: str
    position: Optional[Position]    
    stack: int
    bet_total: int

    last_action: Optional[str]  # 最後のアクション（例: "bet", "fold"）
    folded: bool
    all_in: bool

    sitting_out: bool = False  # 座っていない場合はTrue


class GameStateResponse(BaseModel):
    round: Round
    pot: int
    board: List[str]  # 例: ["Ah", "7d", "Qc"]
    seats: List[PlayerInfo]
    current_turn: Optional[str]  # プレイヤー名 or None

    legal_actions: List[str] = []  # 例: ["fold", "call", "raise"]

    status: str

class MessageResponse(BaseModel):
    message: str
