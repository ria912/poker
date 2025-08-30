# holdem_app/app/models/game_config.py
from dataclasses import dataclass

@dataclass
class GameConfig:
    """ゲームの設定を保持するクラス"""
    seat_count: int = 6
    big_blind: int = 100
    small_blind: int = 50
    initial_stack: int = 10000