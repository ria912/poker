class Seat(BaseModel):
    index: int
    player: Optional[Player] = None
    bet_total: int = 0

    def is_occupied(self) -> bool:
        """席にプレイヤーが座っているか"""
        return self.player is not None

    def clear(self) -> None:
        """プレイヤーを外す（ゲーム終了時など）"""
        self.player = None
        self.bet_total = 0


class Table(BaseModel):
    seats: List[Seat] = Field(default_factory=list)
    pot: int = 0
    board: List[Card] = Field(default_factory=list)
    deck: Deck = Field(default_factory=Deck)

    def reset_for_new_hand(self) -> None:
        """次のハンド用に状態をリセット"""
        self.pot = 0
        self.board.clear()
        for seat in self.seats:
            seat.bet_total = 0
            if seat.player:
                seat.player.reset_for_new_hand()

    def collect_bets_to_pot(self) -> None:
        """全てのベットをポットに集める"""
        for seat in self.seats:
            self.pot += seat.bet_total
            seat.bet_total = 0