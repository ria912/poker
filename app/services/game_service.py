    # --- ゲーム進行制御メソッド ---

    def start_hand(self):
        """新しいハンドを開始"""
        self.table.reset_for_new_hand()
        self.round = Round.PREFLOP
        self.state = State.RUNNING
        self.set_dealer_and_blinds()

    def set_dealer_and_blinds(self):
        """ディーラーとブラインドを設定"""
        self.dealer_index = self.table.get_next_occupied_seat(self.dealer_index)
        sb_index = self.table.get_next_occupied_seat(self.dealer_index)
        bb_index = self.table.get_next_occupied_seat(sb_index)

        self.table.seats[sb_index].place_bet(self.small_blind)
        self.table.seats[bb_index].place_bet(self.big_blind)

        self.current_player_index = self.table.get_next_occupied_seat(bb_index)

    def proceed_to_next_round(self):
        """次のラウンドに進む"""
        if self.round == Round.PREFLOP:
            self.round = Round.FLOP
            self.table.deal_flop()
        elif self.round == Round.FLOP:
            self.round = Round.TURN
            self.table.deal_turn()
        elif self.round == Round.TURN:
            self.round = Round.RIVER
            self.table.deal_river()
        elif self.round == Round.RIVER:
            self.round = Round.SHOWDOWN
            self.state = State.SHOWDOWN
        else:
            self.state = State.FINISHED

    def get_current_player(self):
        """現在アクションすべきプレイヤーを返す"""
        if self.current_player_index is None:
            return None
        return self.table.seats[self.current_player_index].player

    def advance_turn(self):
        """次のプレイヤーにターンを回す"""
        self.current_player_index = self.table.get_next_occupied_seat(self.current_player_index)