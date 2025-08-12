from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

from .table import Table
from .player import Player
from .deck import Deck

class GameState(BaseModel):
    """
    アプリケーションのルートとなる、ゲーム全体の状態を管理するシングルトン的なモデル。
    このモデルが全ての状態を保持する。
    """
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    table: Table = Field(default_factory=Table)
    players: List[Player] = Field(default_factory=list) # テーブルに参加している全プレイヤーリスト
    deck: Deck = Field(default_factory=Deck)
    active_player_id: Optional[str] = None # アクション待ちのプレイヤーID
    
    class Config:
        # Pydantic V2
        # from_attributes = True
        # Pydantic V1
        orm_mode = True

# アプリケーションで唯一のGameStateインスタンスを作成
# 実際には、これをメモリ、Redis、DBなどで永続化することになります。
# ここではシンプルにグローバル変数として定義しますが、
# FastAPIのDI(依存性注入)システムを使うのがより良い方法です。
game_state = GameState()