from backend.models.action import Action
from backend.models.enum import Round, Position, Status

def get_action_order(self, round: Round) -> list[int]:
    # アクティブな座席を抽出
    active_seats = [seat for seat in self.table.seats if seat.player and not seat.player.sitting_out]

    # ラウンドに応じて開始ポジションを変えたい場合はここで処理を入れる
    # 例: プリフロップはUTGからスタート（今回は未実装）
    # 便宜上、先頭はSB（Position.SB）

    # ASSIGN_ORDERのインデックスを取得するための辞書
    pos_order_map = {pos: i for i, pos in enumerate(Position.ASSIGN_ORDER)}

    # アクティブな座席をポジション順でソート
    sorted_seats = sorted(
        active_seats,
        key=lambda seat: pos_order_map.get(seat.player.position, 999)
    )

    # 並べ替えた座席のインデックスを返す
    return [seat.index for seat in sorted_seats]
