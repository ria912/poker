from fastapi import APIRouter, HTTPException, Depends

# FastAPIのDI（依存性注入）はまだ設定していないので、
# いったんサービス層を直接インポートします。
# （将来的には Depends を使って注入するのが理想です）
from ..services import table_service, player_service 
from ..schemas import table_schema, player_schema
from ..models.game_state import game_state # アプリケーション全体の状態

router = APIRouter(
    prefix="/table",
    tags=["Table"],
)

@router.get("/", response_model=table_schema.Table)
def get_table_state():
    """現在のテーブルの状態をすべて取得する"""
    return game_state.table

@router.post("/join", response_model=player_schema.Player)
def join_table(player_join_data: player_schema.PlayerCreate):
    """新しいプレイヤーがテーブルに参加する"""
    try:
        # サービス層のロジックを呼び出す
        player = table_service.add_player_to_table(
            game_state, 
            player_join_data.name,
            player_join_data.stack
        )
        return player
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/leave", response_model=player_schema.Player)
def leave_table(player_leave_data: player_schema.PlayerLeave):
    """プレイヤーがテーブルから退出する"""
    try:
        # サービス層のロジックを呼び出す
        player = table_service.remove_player_from_table(
            game_state,
            player_leave_data.player_id
        )
        return player
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))