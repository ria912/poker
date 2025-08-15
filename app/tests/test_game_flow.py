# tests/test_game_flow.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.game_state import game_state, GameState

# テスト用のクライアントを作成
client = TestClient(app)

# 各テストの前にゲームの状態をリセットするためのヘルパー関数
def reset_game():
    # 新しいGameStateインスタンスで上書きして初期化する
    new_state = GameState()
    game_state.game_id = new_state.game_id
    game_state.table = new_state.table
    game_state.deck = new_state.deck
    game_state.game_status = new_state.game_status
    game_state.active_player_id = new_state.active_player_id


def test_initial_state():
    """初期状態でテーブル情報を取得できるかテスト"""
    reset_game()
    response = client.get("/table/")
    assert response.status_code == 200
    data = response.json()
    assert data["table"]["pot"] == 0
    assert len(data["players"]) == 0

def test_add_and_remove_players():
    """プレイヤーの追加と削除ができるかテスト"""
    reset_game()
    # プレイヤー1を追加
    p1_response = client.post("/players/", json={"name": "Alice", "stack": 1000})
    assert p1_response.status_code == 200
    p1_data = p1_response.json()
    assert p1_data["name"] == "Alice"

    # プレイヤー2を追加
    p2_response = client.post("/players/", json={"name": "Bob", "stack": 1000})
    assert p2_response.status_code == 200

    # 状態を確認
    state_response = client.get("/table/")
    assert state_response.status_code == 200
    state_data = state_response.json()
    assert len(state_data["players"]) == 2

    # プレイヤー1を削除
    delete_response = client.delete(f"/players/{p1_data['player_id']}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Player {p1_data['player_id']} has been removed."

    # 状態を再確認
    state_response_after_delete = client.get("/table/")
    assert len(state_response_after_delete.json()["players"]) == 1

def test_start_game():
    """ゲームを開始できるかテスト"""
    reset_game()
    # プレイヤーを2人追加
    client.post("/players/", json={"name": "Alice", "stack": 1000})
    client.post("/players/", json={"name": "Bob", "stack": 1000})

    # ゲーム開始
    start_response = client.post("/game/start")
    assert start_response.status_code == 200
    assert start_response.json()["message"] == "New hand started."

    # ゲーム開始後の状態を確認
    state_response = client.get("/table/")
    data = state_response.json()
    
    # 全プレイヤーに2枚ずつカードが配られているか
    for player in data["players"]:
        assert len(player["hand"]) == 2
    
    # デッキの枚数が減っているか (52 - 2*2 = 48)
    assert len(data["table"]["community_cards"]) == 0

def test_start_game_with_not_enough_players():
    """プレイヤーが少ない場合にゲームが開始できないことをテスト"""
    reset_game()
    client.post("/players/", json={"name": "Alice", "stack": 1000})
    
    start_response = client.post("/game/start")
    assert start_response.status_code == 400
    assert start_response.json()["detail"] == "Not enough players to start."

def test_next_round_flow():
    """ラウンド進行をテスト (フロップ -> ターン -> リバー)"""
    reset_game()
    client.post("/players/", json={"name": "Alice", "stack": 1000})
    client.post("/players/", json={"name": "Bob", "stack": 1000})
    client.post("/game/start")

    # フロップへ
    flop_response = client.post("/game/next_round")
    assert flop_response.status_code == 200
    assert flop_response.json()["message"] == "Proceeded to FLOP round."
    state1 = client.get("/table/").json()
    assert len(state1["table"]["community_cards"]) == 3 # フロップで3枚

    # ターンへ
    turn_response = client.post("/game/next_round")
    assert turn_response.status_code == 200
    assert turn_response.json()["message"] == "Proceeded to TURN round."
    state2 = client.get("/table/").json()
    assert len(state2["table"]["community_cards"]) == 4 # ターンで+1枚

    # リバーへ
    river_response = client.post("/game/next_round")
    assert river_response.status_code == 200
    assert river_response.json()["message"] == "Proceeded to RIVER round."
    state3 = client.get("/table/").json()
    assert len(state3["table"]["community_cards"]) == 5 # リバーで+1枚