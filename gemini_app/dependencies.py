# app/dependencies.py
from services.player_service import PlayerService
from services.table_service import TableService
from services.round_service import RoundService
from services.action_service import ActionService
from services.winner_service import WinnerService

def get_player_service() -> PlayerService:
    return PlayerService()

def get_table_service() -> TableService:
    return TableService()

def get_round_service() -> RoundService:
    return RoundService()

def get_action_service() -> ActionService:
    return ActionService()

def get_winner_service() -> WinnerService:
    return WinnerService()