# backend/schemas/game_schema.py

from pydantic import BaseModel
from typing import List, Optional
from backend.models.enum import Action, Position, Round

# --- リクエストスキーマ ---

class StartGameRequest(BaseModel):
    player_num: int = 4  # デフォルトは4人テーブル
    human_seat_index: int = 0  # 人間プレイヤーの席（BTNからの相対位置）


class PlayerActionRequest(BaseModel):
    seat_index: int
    action: Action
    amount: Optional[int] = None  # BETまたはRAISE時のみ指定


# --- レスポンススキーマ ---

class LegalActionSchema(BaseModel):
    action: Action
    min_amount: Optional[int] = None
    max_amount: Optional[int] = None


class PlayerSchema(BaseModel):
    name: str
    is_human: bool
    stack: int
    bet_total: int
    hand: Optional[List[str]]  # 表示は ['Ah', 'Kd'] のような形式
    position: Position
    last_action: Optional[Action] = None


class TableSchema(BaseModel):
    round: Round
    pot: int
    current_bet: int
    board: List[str]  # 表示は ['2c', '7d', 'Jh'] のような形式


class ActionHistorySchema(BaseModel):
    round: Round
    seat_index: int
    player_name: str
    action: Action
    amount: Optional[int]


class GameStateResponse(BaseModel):
    table: TableSchema
    players: List[PlayerSchema]
    legal_actions: List[LegalActionSchema]
    waiting_player: Optional[int]  # アクション待ちのseat_index（Noneなら進行終了）
    action_histories: List[ActionHistorySchema]
