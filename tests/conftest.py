import pytest
from app.models.game_state import GameState
from app.models.player import Player

@pytest.fixture
def players():
    """6人分のプレイヤーリストを返すフィクスチャ"""
    return [Player(f"Player_{i}") for i in range(6)]

@pytest.fixture
def game_state(players): # playersフィクスチャを利用するように変更
    """
    3人のプレイヤーが着席した基本的なゲーム状態を返すフィクス- ャ
    - BB=100, SB=50, 席数=6
    """
    # GameStateを直接パラメータで初期化するように変更
    gs = GameState(big_blind=100, small_blind=50, seat_count=6)
    
    # playersフィクスチャからプレイヤーを取得して着席させる
    gs.table.sit_player(players[0], 0, 10000)
    gs.table.sit_player(players[1], 1, 10000)
    gs.table.sit_player(players[2], 2, 10000)
    
    return gs