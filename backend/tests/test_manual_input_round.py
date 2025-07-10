from backend.models.enum import Action, Status
from backend.services.round import RoundManager
from backend.models.table import Table
from backend.models.player import Player


class InteractivePlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def act(self, table):
        print(f"\n▶ {self.name} の番です（ポジション: {self.position}）")
        print("選択肢: 1=FOLD, 2=CHECK, 3=CALL, 4=BET, 5=RAISE")

        action_map = {
            "1": Action.FOLD,
            "2": Action.CHECK,
            "3": Action.CALL,
            "4": Action.BET,
            "5": Action.RAISE,
        }

        while True:
            choice = input("アクション番号を入力してください: ").strip()
            if choice in action_map:
                action = action_map[choice]
                break
            print("無効な入力です。1〜5を入力してください。")

        # amount の入力が必要なアクション
        amount = 0
        if action in [Action.BET, Action.RAISE]:
            while True:
                try:
                    amount = int(input("金額を入力してください（整数）: ").strip())
                    if amount >= 0:
                        break
                    print("金額は0以上の整数で入力してください。")
                except ValueError:
                    print("無効な入力です。整数を入力してください。")

        self.last_action = action
        print(f"✅ {self.name} は {action.name}（{amount}）を選択")

        return action, amount

def create_interactive_table():
    table = Table()
    names = ["P1", "P2", "P3", "P4"]

    for i in range(4):
        table.seats[i].player = InteractivePlayer(names[i])
        table.seats[i].index = i  # ✅ Seat.index を明示的に設定（重要！）

    table.btn_index = 0
    table.starting_new_hand()
    return table


def print_players(table: Table):
    print("\n🎮 プレイヤー情報:")
    for seat in table.seats:
        p = seat.player
        if p:
            print(f"・{p.name}: position={p.position}, stack={p.stack}, bet={p.bet_total}")


def run_manual_round():
    table = create_interactive_table()
    manager = RoundManager(table)
    manager.reset()

    print("\n=== 🃏 手動操作テスト開始 ===")
    print_players(table)

    round_name = table.round.name
    print(f"\n🕐 ラウンド開始: {round_name}")

    while True:
        prev_round = table.round  # ← ラウンド変化を検知するため保持
        status = manager.proceed()

        # ✅ アクション適用後の bet_total 表示
        print("\n💡 各プレイヤーのベット状況:")
        for i, seat in enumerate(table.seats):
            if seat.player:
                print(f"  - {seat.player.name} (seat {i}): bet_total = {seat.player.bet_total}")

        # ✅ ラウンドが変わったらボード表示
        if table.round != prev_round:
            round_name = table.round.name
            print(f"\n💡 ラウンド進行 → {round_name}")
            print(f"🃍 ボード: {table.board}")

        print(f"\n💰 ポット: {table.pot} / ステータス: {status.name}")

        if status == Status.ROUND_OVER:
            print("\n✅ ラウンド終了")
            break
        elif status == Status.HAND_OVER:
            print("\n🏁 ハンド終了")
            break

    print("\n🎯 最終ボード:", table.board)
    for seat in table.seats:
        p = seat.player
        if p:
            print(f"{p.name}: action={p.last_action}, stack={p.stack}, folded={p.folded}")


if __name__ == "__main__":
    run_manual_round()
