from fastapi import APIRouter
from app.services import poker_logic
from app.schemas.game import NewGameResponse

# APIRouterインスタンスを作成します
# これにより、関連するエンドポイントをグループ化できます
router = APIRouter(
    prefix="/game",  # このルーターのエンドポイントはすべて "/game" から始まります
    tags=["Game"],   # APIドキュメントで "Game" としてグループ化されます
)

@router.get("/new", response_model=NewGameResponse)
def new_game():
    """
    新しいポーカーゲームを開始する。
    
    新しいデッキを作成し、シャッフルしてプレイヤーとディーラーに
    2枚ずつカードを配ります。
    """
    game_data = poker_logic.start_new_game()
    return game_data