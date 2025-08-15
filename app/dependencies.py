# app/dependencies.py
from .models.game_state import game_state, GameState

def get_game_state() -> GameState:
    """
    アプリケーション全体で共有されるGameStateのシングルトンインスタンスを返す。
    FastAPIのDependsにこの関数を渡すことで、各エンドポイントで状態を共有できる。
    """
    return game_state