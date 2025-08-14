# app/dependencies.py
from typing import Optional
from .models.game_state import GameState

# アプリケーションのライフサイクル中で唯一のGameStateインスタンスを保持する変数
# _（アンダースコア）で始まる変数は、ファイル内でのみ使用するプライベートな変数であることを示す慣習です。
_game_state_instance: Optional[GameState] = None

def get_game_state() -> GameState:
    """
    GameStateのシングルトンインスタンスを取得するための依存性関数。
    
    FastAPIは、この関数を呼び出して、その戻り値をエンドポイントの引数に「注入」します。
    アプリケーション内で初めて呼び出されたときにインスタンスを生成し、
    以降はそのインスタンスを使い回します。
    """
    global _game_state_instance
    if _game_state_instance is None:
        # インスタンスがまだなければ、新しく作成する
        _game_state_instance = GameState()
    
    return _game_state_instance