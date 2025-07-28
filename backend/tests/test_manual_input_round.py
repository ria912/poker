# backend/tests/test_manual_simulation.py

from backend.models.table import Table
from backend.models.player import Player
from backend.services.dealer import Dealer
from backend.services.round_manager import RoundManager
from backend.services.action_manager import ActionManager
from backend.schemas import table_to_dict, action_info_to_dict

def display_table_state(table: Table):
    print("\n=== テーブル情報 ===")
    info = table_to_dict(table)
    print(f"ラウンド: {info['round']}")
    print(f"ポット: {info['pot']} | 現在のベット: {info['current_bet']}")
    print(f"ボード: {' '.join(info['board']) if info['board'] else '(なし)'}")

    for p in info['players']:
        hand_str = ' '.join(p['hand'])
        print(f"[{p['seat']}] {p['position']} {p['name']} | stack: {p['stack']} | "
              f"bet: {p['bet_total']} | hand: {hand_str} | action: {p['last_action']}")


def display_action_options(player: Player, table: Table):
    print(f"\n--- アクション選択: {player.name} ({player.position.name}) ---")
    action_info = action_info_to_dict(player, table)
    options = action_info['legal_actions']

    for i, option in enumerate(options):
        action = option["action"]
        min_amt = option.get("min")
        max_amt = option.get("max")
        if min_amt is not None and max_amt is not None:
            print(f"{i}: {action} ({min_amt} - {max_amt})")
        else:
            print(f"{i}: {action}")
    return options


def manual_action_input(player: Player, table: Table):
    options = display_action_options(player, table)
    while True:
        try:
            choice = int(input("アクション番号を入力: "))
            if choice < 0 or choice >= len(options):
                raise ValueError("無効な番号")
            selected = options[choice]
            action = selected["action"]

            if "min" in selected and "max" in selected:
                amount = int(input(f"額を入力 ({selected['min']}〜{selected['max']}): "))
            else:
                amount = 0

            ActionManager.apply_action(player, action, amount, table)
            print(f"{player.name} → {action} {amount if amount > 0 else ''}")
            break
        except Exception as e:
            print(f"エラー: {e}. 再入力してください。")


def run_manual_simulation():
    # プレイヤー初期化
    players = [
        Player(name="Alice", stack=100),
        Player(name="Bob", stack=100),
        Player(name="Carol", stack=100),
        Player(name="Dave", stack=100),
    ]
    table = Table(players=players)
    dealer = Dealer(table)
    dealer.prepare_new_hand()

    print("\n=== プリフロップ開始 ===")
    round_manager = RoundManager(table)
    display_table_state(table)

    while not round_manager.is_hand_over():
        current_player = round_manager.get_next_player()
        if current_player is None:
            round_manager.advance_round()
            display_table_state(table)
            continue

        manual_action_input(current_player, table)
        display_table_state(table)

    print("\n=== ハンド終了 ===")
    display_table_state(table)


if __name__ == "__main__":
    run_manual_simulation()