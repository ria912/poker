# holdem_app/app/models/action.py
from typing import Optional
from dataclasses import dataclass
from .enum import ActionType

@dataclass(frozen=True)
class Action:
    """プレイヤーのアクションを表すクラス"""
    player_id: str
    action_type: ActionType
    amount: Optional[int] = None