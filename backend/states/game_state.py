# backend/state/game_state.py
from typing import Optional
from models.table import Table

class GameState:
    """
    ゲーム全体の現在の状態を保持するクラスです。
    このクラスはシングルトンとして扱われ、アプリケーション全体で単一のインスタンスを共有します。
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # table属性がまだ初期化されていない場合のみ初期化する
        if not hasattr(self, 'table'):
            self.table: Optional[Table] = None

    def set_table(self, table: Table):
        """
        現在のテーブル状態を設定します。
        """
        self.table = table

    def get_table(self) -> Optional[Table]:
        """
        現在のテーブル状態を取得します。
        """
        return self.table

# アプリケーション全体で共有するゲーム状態のインスタンス
game_state = GameState()