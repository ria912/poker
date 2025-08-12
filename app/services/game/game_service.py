from ...models.game_state import GameState
from ...models.enum import PlayerState, Round

# 他のサービスモジュール（今後作成）
# これらは、各専門分野のロジックを担当します。
from . import position_manager
from . import action_manager
from . import round_manager

# テーブルやプレイヤーの状態をリセットするためのサービス
from .. import table_service

# ゲームの定数（将来的には設定ファイルから読み込むのが望ましい）
BIG_BLIND_AMOUNT = 20
SMALL_BLIND_AMOUNT = 10

def start_new_hand(game_state: GameState):
    """
    新しいハンドを開始するためのメイン関数。
    司令塔として、各専門サービスを順番に呼び出していく。
    """
    # 1. ゲーム開始の前提条件をチェック
    _validate_can_start_hand(game_state)

    # 2. 前のハンドの状態をリセット
    table_service.reset_hand(game_state)
    
    # 3. アクティブなプレイヤーリストを作成
    active_players = table_service.get_active_players_for_new_hand(game_state)
    if len(active_players) < 2:
        raise ValueError("Cannot start hand. Not enough active players (at least 2 required).")

    # 4. デッキをシャッフル
    game_state.deck.shuffle()

    # 5. ポジションを決定し、ブラインド対象者情報を取得 (position_managerの仕事)
    # ディーラーボタンを次に移し、SB, BBのプレイヤーを決定する
    blind_players = position_manager.assign_positions_and_get_blinds(game_state, active_players)
    
    # 6. ブラインドを強制ベット (action_managerの仕事)
    # SB, BBのプレイヤーからブラインドを徴収する
    action_manager.post_blinds(
        game_state=game_state,
        sb_player=blind_players["sb_player"],
        bb_player=blind_players["bb_player"],
        sb_amount=SMALL_BLIND_AMOUNT,
        bb_amount=BIG_BLIND_AMOUNT
    )

    # 7. 手札を配る
    _deal_hole_cards(game_state, active_players)

    # 8. プリフロップラウンドを開始 (round_managerの仕事)
    # ラウンド状態をPREFLOPに設定し、最初のアクション番のプレイヤーを決定する
    round_manager.start_preflop_round(game_state, active_players)

    print(f"--- New Hand Started (Game ID: {game_state.game_id}) ---")
    print(f"Dealer is at seat {game_state.table.dealer_position}")
    print(f"Pot: {game_state.table.pot}")


def _validate_can_start_hand(game_state: GameState):
    """ゲームを開始できるかどうかの検証"""
    # 例えば、現在進行中のラウンドがないかなどをチェックできる
    # ここではシンプルに、常に開始できると仮定
    if game_state.table.current_round != Round.PREFLOP and game_state.table.pot > 0:
         # 本来はもっと厳密なチェックが必要
         print("Warning: Starting a new hand while another seems to be in progress.")
    pass

def _deal_hole_cards(game_state: GameState, active_players: list):
    """アクティブな各プレイヤーに手札を2枚ずつ配る"""
    print("Dealing hole cards...")
    for _ in range(2): # 2枚配るので2周する
        for player in active_players:
            if player.state == PlayerState.ACTIVE:
                card = game_state.deck.deal(1)
                player.hand.extend(card)
    
    # デバッグ用に手札を表示
    for player in active_players:
        hand_str = [f"{c.rank}{c.suit}" for c in player.hand]
        print(f"Player {player.name} received hand: {hand_str}")