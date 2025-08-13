backend/
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
│   ├── game_state.py           # ゲーム全体の状態管理用モデル
│
├── services/                   # ビジネスロジック層
│   ├── __init__.py
│   │
│   ├── game/                   # ゲーム進行に関するロジックまとめ
│   │   ├── __init__.py
│   │   ├── game_service.py     # ハンド進行やラウンド遷移の統括
│   │   ├── action_manager.py   # アクション実行ロジック（bet/call/fold等）
│   │   ├── position_manager.py # BTN/SB/BB割り当てロジック
│   │   ├── round_manager.py    # ラウンド進行管理
│   │   └── evoluter.py         # 勝者判定ロジック
│   │
│   ├── table_service.py        # 座席・ポット・ラウンドリセットなどテーブル操作
│   ├── player_service.py       # プレイヤー状態・アクション処理
│   └── deck_service.py         # カード配布・評価補助
│
├── dependencies.py             # DI設定（サービスインスタンス生成など）
│
├── schemas/                    # API入出力用Pydanticスキーマ
│   ├── __init__.py
│   ├── player_schema.py
│   ├── table_schema.py
│   └── game_schema.py
│
└── utils/                      # 共通ユーティリティ
    ├── __init__.py
    ├── card_utils.py           # カードの変換・評価補助
    └── order_utils.py          # 座席やアクション順序の計算用ユーティリティ
