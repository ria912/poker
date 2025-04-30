from models.table import Table
from models.round_manager import RoundManager

def display_player_info(players, show_hand=True):
    for p in players:
        hand_info = f" | Hand: {p.hand}" if show_hand else ""
        print(f"{p.name} | Stack: {p.stack} | Bet: {p.current_bet} | "
              f"Folded: {p.has_folded}{hand_info}")

def run_single_hand():
    # テーブルとラウンドマネージャーの初期化
    table = Table()
    round_manager = RoundManager(table)

    # ハンドの開始処理（デッキシャッフル、カード配布、ポジション・ブラインドなど）
    round_manager.start_new_round()

    print("\n=== STARTING HAND ===")
    display_player_info(table.players)

    # 各フェーズ（preflop, flop, turn, river）の進行
    while round_manager.phase != 'showdown':
        while not round_manager.should_advance_phase():
            round_manager.proceed_action()

            print(f"\nPot: {table.pot}")
            display_player_info(table.players, show_hand=False)
            print("---")

        round_manager.advance_phase()

        if round_manager.phase != 'showdown':
            print(f"\n>>> Phase: {round_manager.phase.upper()} <<<")
            print(f"Community: {table.community_cards}")
            print(f"Pot: {table.pot}")

    # ショーダウン表示
    print("\n=== SHOWDOWN ===")
    print(f"Community Cards: {table.community_cards}")
    display_player_info(table.players)

if __name__ == "__main__":
    run_single_hand()
