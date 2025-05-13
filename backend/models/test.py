# run_one_hand.py
import sys
import os

# "models" パッケージを解決するために、親ディレクトリを sys.path に追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.table import Table
from models.round_manager import RoundManager

def run_one_hand():
    # テーブルとラウンドマネージャーを作成
    table = Table()
    table.start_hand()
    manager = RoundManager(table)
    manager._start_betting_round()

    print("=== Hand Start ===")

    while True:
        result = manager.proceed_one_action()

        # 人間のアクションを待つ段階
        if result == "waiting_for_human":
            # 人間のアクションはテスト用に自動化されているため、即座にシミュレーションして進める
            human = table.get_human_player()
            # 自動でdecide_actionが呼ばれるので、何もする必要なし
            result = manager.resume_after_human_action()

        if result == "hand_over":
            print("=== Hand Over ===")
            break

    # 最後の状態を出力
    print("--- Final Result ---")
    for p in table.seats:
        if p:
            print(f"{p.name} | Stack: {p.stack} | Folded: {p.has_folded} | Hand: {p.hand}")
    print(f"Community Cards: {table.community_cards}")
    print(f"Pot: {table.pot}")

if __name__ == "__main__":
    run_one_hand()
