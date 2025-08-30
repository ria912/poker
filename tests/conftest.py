import pytest
from app.models.game_state import GameState
from app.models.player import Player

@pytest.fixture
def fresh_game_state():
    """プレイヤーが誰も座っていないまっさらなGameStateを返す"""
    return GameState(small_blind=10, big_blind=20)

@pytest.fixture
def game_state_with_3_players():
    """3人のプレイヤーが着席しているGameStateを返す"""
    game_state = GameState(small_blind=10, big_blind=20)
    
    player1 = Player(name="Alice")
    player2 = Player(name="Bob")
    player3 = Player(name="Charlie")

    game_state.table.seats[0].sit_down(player1, 1000)
    game_state.table.seats[1].sit_down(player2, 1000)
    game_state.table.seats[3].sit_down(player3, 1000) # 席を一つ空ける
    
    return game_state