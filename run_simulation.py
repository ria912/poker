import random
from backend.game_state import GameState
from backend.models.player import Player
from backend.services.round_manager import RoundManager
from backend.services.action_manager import ActionManager
from backend.models.enum import Action, Round

def print_game_state(game_state: GameState):
    """ゲームの状態を分かりやすく表示するヘルパー関数"""
    print("\n" + "="*50)
    state = game_state.get_game_view()
    print(f"ROUND: {state['current_round']} | POT: {state['pot']} | BOARD: {state['board']}")
    print(f"Button is at seat {state['button_index']}")
    print("-"*50)
    for seat in state['seats']:
        if seat['player_name']:
            player_info = (
                f"  Seat {seat['index']}: {seat['player_name']} ({seat['position']}) "
                f"| Stack: {seat['stack']} | Bet: {seat['bet_total']}"
            )
            if seat['is_folded']:
                player_info += " (FOLDED)"
            if seat['hole_cards']:
                 player_info += f" | Hand: {seat['hole_cards']}"
            print(player_info)
    print("="*50 + "\n")


def run_one_hand_simulation():
    """ワンハンドシミュレーションを実行します"""
    
    # 1. プレイヤーの準備
    players = [
        Player(name="Alice", stack=1000),
        Player(name="Bob", stack=1000),
        Player(name="Charlie", stack=1000),
        Player(name="David", stack=1000),
        Player(name="Eve", stack=1000),
        Player(name="Frank", stack=1000),
    ]

    # 2. ゲーム状態の初期化とハンドの開始
    game_state = GameState(max_seats=6)
    game_state.setup_new_game(players)
    game_state.start_new_hand()
    
    print("--- NEW HAND START ---")
    print_game_state(game_state)

    round_manager = RoundManager(game_state)

    # 3. 各ラウンドのループ
    while game_state.current_round != Round.SHOWDOWN:
        
        # アクティブプレイヤーが1人になったらハンド終了
        if len(game_state.table.get_active_seats()) <= 1:
            print("アクティブなプレイヤーが1人になったため、ハンドを終了します。")
            game_state.dealer.distribute_pot()
            break

        print(f"--- STARTING {game_state.current_round.name} ---")
        round_manager.start_betting_round()

        # 4. ベッティングラウンド内のアクションループ
        while not round_manager.is_round_over():
            active_player_index = game_state.active_player_index
            player = game_state.table.seats[active_player_index].player
            table = game_state.table

            legal_actions_info = ActionManager.get_legal_actions_info(player, table)
            legal_actions = legal_actions_info['legal_actions']

            print(f"輪到 {player.name} 行動 (Stack: {player.stack})")
            print(f"合法操作: {[action.name for action in legal_actions]}")

            # AIのアクションをランダムに決定 (簡易版)
            action = random.choice(legal_actions)
            amount = 0
            if action == Action.BET:
                # とりあえずミニマムベット
                amount = table.min_bet if table.min_bet > 0 else 20
            elif action == Action.RAISE:
                 # とりあえずミニマムレイズ
                amount = table.min_bet

            print(f"アクション: {action.name}, 金額: {amount}")

            # アクションを適用
            ActionManager.apply_action(player, table, action, amount)
            
            # レイズ系のアクションが行われた場合、RoundManagerのlast_aggressorを更新
            if action in [Action.BET, Action.RAISE]:
                round_manager.last_aggressor = player

            print_game_state(game_state)

            # ラウンドが終了したかチェック
            if round_manager.is_round_over():
                print(f"--- {game_state.current_round.name} END ---")
                break
            
            # 次のプレイヤーへ
            round_manager.advance_to_next_player()

        # 5. 次のラウンドへ
        round_manager.proceed_to_next_round()

    print("--- HAND OVER ---")
    print("最終結果:")
    print_game_state(game_state)


if __name__ == "__main__":
    run_one_hand_simulation()