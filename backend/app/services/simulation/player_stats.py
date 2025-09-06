# holdem_app/app/services/simulation/player_stats.py
from collections import defaultdict

class PlayerStats:
    """プレイヤーの統計情報を記録・管理するクラス"""
    def __init__(self, player_id: str, player_name: str):
        self.player_id = player_id
        self.player_name = player_name
        self.hands_played = 0
        self.total_winnings = 0
        
        # VPIP/PFR計算用
        self.vpip_opportunities = 0
        self.vpip_actions = 0
        self.pfr_opportunities = 0
        self.pfr_actions = 0

    def record_preflop_action(self, vpip_opportunity: bool, pfr_opportunity: bool, did_vpip: bool, did_pfr: bool):
        """プリフロップのアクションを記録する"""
        if vpip_opportunity:
            self.vpip_opportunities += 1
            if did_vpip:
                self.vpip_actions += 1
        
        if pfr_opportunity:
            self.pfr_opportunities += 1
            if did_pfr:
                self.pfr_actions += 1

    def record_hand_result(self, final_stack: int, starting_stack: int):
        """ハンド終了時の結果を記録する"""
        self.hands_played += 1
        winnings = final_stack - starting_stack
        self.total_winnings += winnings

    @property
    def vpip(self) -> float:
        """VPIP (Voluntarily Put money In Pot) を計算"""
        return (self.vpip_actions / self.vpip_opportunities) * 100 if self.vpip_opportunities > 0 else 0

    @property
    def pfr(self) -> float:
        """PFR (Pre-Flop Raise) を計算"""
        return (self.pfr_actions / self.pfr_opportunities) * 100 if self.pfr_opportunities > 0 else 0

    def get_bb_per_100(self, big_blind: int) -> float:
        """bb/100 hands を計算"""
        if self.hands_played == 0:
            return 0.0
        return (self.total_winnings / self.hands_played) * 100 / big_blind

    def get_summary(self, big_blind: int) -> str:
        """統計情報のサマリーを文字列で返す"""
        bb_100 = self.get_bb_per_100(big_blind)
        summary = (
            f"--- Stats for {self.player_name} ---\n"
            f"Hands Played: {self.hands_played}\n"
            f"Total Winnings: {self.total_winnings}\n"
            f"bb/100 hands: {bb_100:.2f}\n"
            f"VPIP: {self.vpip:.1f}%\n"
            f"PFR: {self.pfr:.1f}%\n"
            f"---------------------------------"
        )
        return summary
