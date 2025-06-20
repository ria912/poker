from backend.models.enum import Round, Position

class ActionTurnManager:
    def __init__(self, table: Table):
        self.table = table
        self.current_index: Optional[int] = None

    def initialize_turn_by_round(self, round_stage: Round):
        """ラウンドごとの開始プレイヤーを自動設定"""
        if round_stage == Round.PREFLOP:
            bb_index = self.table.get_seat_index_by_position(Position.BB)
            start_index = (bb_index + 1) % len(self.table.seats)
        else:
            btn_index = self.table.get_seat_index_by_position(Position.BTN)
            start_index = (btn_index + 1) % len(self.table.seats)

        self.current_index = self.find_next_actionable_player(start_index)

    def proceed_to_next(self):
        """次のアクションプレイヤーに進む"""
        if self.current_index is None:
            return
        self.current_index = self.find_next_actionable_player(self.current_index)

    def find_next_actionable_player(self, from_index: int) -> Optional[int]:
        """時計回りで次のアクション可能プレイヤーを探す"""
        n = len(self.table.seats)
        for offset in range(1, n + 1):
            i = (from_index + offset) % n
            seat = self.table.seats[i]
            player = seat.player
            if (
                player
                and player.is_active
                and not player.is_all_in
                and player.bet_total < self.table.current_bet
            ):
                return i
        return None