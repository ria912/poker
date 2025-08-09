# tests/test_table.py

import pytest
from backend.models.table import Table
from backend.models.player import Player
from backend.models.enum import Round

def test_table_initialization():
    # プレイヤーを仮に2人作成（任意で増やせる）
    players = [
        Player(name="Alice", stack=1000),
        Player(name="Bob", stack=1000)
    ]

    # Tableインスタンス作成
    table = Table(players=players)

    # printで出力（開発中の確認用）
    print("\n--- 初期化されたTable ---")
    print("プレイヤー数:", len(table.players))
    for p in table.players:
        print(f"{p.name}: stack={p.stack}, folded={p.folded}")

    print("現在のラウンド:", table.round)
    print("ポット:", table.pot)
    print("コミュニティカード:", table.community_cards)

    # アサーション例（テスト）
    assert len(table.players) == 2
    assert table.round == Round.PREFLOP
    assert table.pot == 0
    assert table.community_cards == []
