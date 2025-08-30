import pytest
from app.models.game_state import GameState
from app.models.game_config import GameConfig
from app.models.player import Player

@pytest.fixture
def game_config():
    """共通のゲーム設定を返すフィクスチャ"""
    return GameConfig(big_blind=100, small_blind=50, initial_stack=10000)

@pytest.fixture
def players():
    """6人分のプレイヤーリストを返すフィクスチャ"""
    return [Player(f"Player_{i}") for i in range(6)]

@pytest.fixture
def game_state(game_config):
    """3人のプレイヤーが着席した基本的なゲーム状態を返すフィクスチャ"""
    gs = GameState(game_config)
    players = [Player(f"Player_{i}") for i in range(3)]
    gs.table.sit_player(players[0], 0, 10000)
    gs.table.sit_player(players[1], 1, 10000)
    gs.table.sit_player(players[2], 2, 10000)
    return gs
