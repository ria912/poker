from models.table import Table
from models.round_manager import RoundManager

def run_full_hand_test():
    table = Table()
    table.start_hand()
    manager = RoundManager(table)

    print("=== ハンド開始 ===")
    print(f"プリフロップ開始 - ポット: {table.pot}")
    print("プレイヤー情報:")
    for i, player in enumerate(table.seats):
        if player:
            print(f"Seat {i+1} | {player.name} | Stack: {player.stack} | Pos: {player.position} | Hand: {player.hand}")

    # 🔧 ベッティングラウンドを明示的に開始
    manager._start_betting_round()

    # アクション処理ループ
    while True:
        result = manager.proceed_one_action()
        if result == "hand_over":
            break

    print("\n=== ショーダウン ===")
    print(f"コミュニティカード: {table.community_cards}")
    print(f"最終ポット: {table.pot}")
    for i, player in enumerate(table.seats):
        if player:
            print(f"{player.name} | Stack: {player.stack} | Folded: {getattr(player, 'has_folded', False)} | Hand: {player.hand}")

if __name__ == "__main__":
    run_full_hand_test()

