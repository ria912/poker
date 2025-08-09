from pydantic import BaseModel
from typing import List

# APIレスポンスのデータ構造を定義します
class NewGameResponse(BaseModel):
    player_hand: List[str]
    dealer_hand: List[str]
    
    # Pydanticモデルの挙動を設定する内部クラス
    class Config:
        # この設定により、ORMモデルなどからでもPydanticモデルを作成しやすくなります。
        # 今回は直接的な影響はありませんが、良い習慣として記述しておきます。
        from_attributes = True