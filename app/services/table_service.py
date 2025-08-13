    


def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """プレイヤーIDからプレイヤーオブジェクトを取得する"""
        for seat in self.seats:
            if seat.is_occupied and seat.player.player_id == player_id:
                return seat.player
        return None

def get_player_by_position(self, position: Position) -> Optional[Player]:
        """ポジションからプレイヤーオブジェクトを取得する"""
        for seat in self.seats:
            if seat.is_occupied and seat.player.position == position:
                return seat.player
        return None