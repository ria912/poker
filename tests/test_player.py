import pytest
from models.player import Player

def test_player_initialization():
    player = Player("Alice", is_human=True)
    assert player.name == "Alice"
    assert player.is_human is True
    assert player.stack == 10000
    assert player.hand == []
    assert player.position is None
    assert player.current_bet == 0
    assert player.has_folded is False

def test_player_betting():
    player = Player("Bob")
    player.current_bet = 50
    player.stack -= 50
    assert player.current_bet == 50
    assert player.stack == 950

def test_player_fold():
    player = Player("Carol")
    player.has_folded = True
    assert player.has_folded is True

def test_player_to_dict_hidden_hand():
    player = Player("CPU1")
    player.hand = ['Ah', 'Ks']
    result = player.to_dict()
    assert result["hand"] == ["X", "X"]

def test_player_to_dict_human_hand():
    player = Player("You", is_human=True)
    player.hand = ['Ah', 'Ks']
    result = player.to_dict()
    assert result["hand"] == ['Ah', 'Ks']
