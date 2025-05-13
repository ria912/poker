from models.table import Table
from models.round_manager import RoundManager
from models.action import ActionType

def test_hand():
    # テーブルとラウンドマネージャの初期化
    table = Table(small_blind=50, big_blind=100, seat_count=6)
    round_manager = RoundManager(table)

    # 1ハンド開始
    table.start_hand()
    
    # 初期状態でプレイヤーの手札とポットを確認
    print("Community Cards:", table.community_cards)
    print("Pot:", table.pot)
    for player in table.seats:
        if player:
            print(f"Player {player.name} - Hand: {player.hand} Stack: {player.stack}")

    # 進行するアクションをシミュレート（人間のアクションは事前に設定）
    human_player = table.get_human_player()

    # 1st アクション（人間プレイヤーのターン）
    round_manager.set_human_action(('call', 100))  # 人間プレイヤーがコール
    result = round_manager.proceed_one_action()
    print(result)
    
    # 2nd アクション（AIプレイヤーのターン）
    result = round_manager.proceed_one_action()
    print(result)

    # 次のアクションを進める（フロップ、ターン、リバーの進行）
    print("Advancing to next street...")
    while result not in ["hand_over", "round_over"]:
        result = round_manager.proceed_one_action()
        print(result)
        print("Pot:", table.pot)
        print("Community Cards:", table.community_cards)
        for player in table.seats:
            if player:
                print(f"Player {player.name} - Stack: {player.stack} Bet: {player.current_bet}")

    # 最終結果の確認
    print("Final Pot:", table.pot)
    for player in table.seats:
        if player:
            print(f"Player {player.name} - Stack: {player.stack} Final Bet: {player.current_bet}")

# テストを実行
test_hand()