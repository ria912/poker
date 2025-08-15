app/
├── main.py                     # FastAPIエントリーポイント
│
├── api/                        # APIルーター関連
│   ├── __init__.py
│   ├── game_router.py          # ゲーム進行用エンドポイント
│   ├── player_router.py        # プレイヤー操作用エンドポイント
│   └── table_router.py         # テーブル状態取得など
│
├── models/                     # 状態(データ構造)定義
│   ├── __init__.py
│   ├── enum.py                 # Position, Action, Round, State など
│   ├── player.py               # Player, PlayerState
│   ├── table.py                # Table, Seat
│   ├── deck.py                 # Deck, Card関連（treys利用）
│   └── game_state.py           # ゲーム全体の状態管理用モデル
│
├── services/                   # ビジネスロジック層
│   ├── __init__.py
│   ├── game_service.py     # ハンド進行やラウンド遷移の統括
│   ├── table_service.py        # 座席・ポット・ラウンドリセットなどテーブル操作
│   ├── player_service.py       # プレイヤー状態・アクション処理
│   └── deck_service.py         # カード配布・評価補助
│
├── dependencies.py             # DI設定（サービスインスタンス生成など）
│
├── schemas/                    # API入出力用Pydanticスキーマ
│
└── utils/                      # 共通ユーティリティ
    ├── __init__.py
    ├── card_utils.py           # 役判定など
    └── order_utils.py          # 座席やアクション順序の計算用ユーティリティ
