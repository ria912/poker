import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models')))
import pytest
from models.table import Table
from models.player import Player
from models.human_player import HumanPlayer
from models.ai_player import AIPlayer

@pytest.fixture
def table():
    """テスト用のテーブルを初期化するためのfixture"""
    return Table(small_blind=50, big_blind=100)

def test_create_players(table):
    """プレイヤーが正しく作成されているかをテスト"""
    assert len(table.players) == 6  # 1人の人間プレイヤーと5人のAIプレイヤー
    assert isinstance(table.players[0], HumanPlayer)
    assert isinstance(table.players[1], AIPlayer)

def test_start_hand(table):
    """ハンド開始時に正しく初期化されるかをテスト"""
    table.start_hand()
    
    # デッキがシャッフルされている
    assert len(table.deck.cards) == 52
    
    # プレイヤーの手札が配られている
    assert all(player.hand for player in table.players)
    
    # ポットとベット関連の初期値
    assert table.pot == 0
    assert table.current_bet == 0
    assert table.min_bet == table.big_blind
    
    # プレイヤーのスタックとベットがリセットされている
    for player in table.players:
        assert player.stack == 10000  # 初期スタックが10000
        assert player.current_bet == 0
        assert not player.has_folded

def test_post_blinds(table):
    """ブラインドの投稿が正しく行われているかをテスト"""
    table.start_hand()  # ハンドを開始しブラインドを投稿
    sb_player = next(p for p in table.players if p.position == 'SB')
    bb_player = next(p for p in table.players if p.position == 'BB')
    
    # SBとBBにチップが投稿されている
    assert sb_player.current_bet == table.small_blind
    assert bb_player.current_bet == table.big_blind
    assert table.pot == table.small_blind + table.big_blind
    assert table.current_bet == table.big_blind
    assert table.min_bet == table.big_blind

def test_reset_players(table):
    """プレイヤーのリセットが正しく行われるかをテスト"""
    table.start_hand()  # 1ハンド開始
    player = table.players[0]  # 1人目のプレイヤー
    
    player.stack -= 500  # チップを減らしておく
    player.current_bet = 500
    player.has_folded = True
    
    table.reset_players()  # プレイヤーをリセット
    
    # プレイヤーがリセットされていることを確認
    assert player.stack == 10000  # 初期スタック
    assert player.current_bet == 0  # ベットは0
    assert not player.has_folded  # フォールド状態ではない
    assert player.hand == []  # 手札は空であるべき

def test_deck_shuffling(table):
    """デッキがシャッフルされているかをテスト"""
    deck_before = table.deck.cards[:]
    table.deck.deck_shuffle()
    assert table.deck.cards != deck_before  # シャッフル後は元の順番と違うはず
